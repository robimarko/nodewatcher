import datetime
import mongoengine
import pymongo
import pymongo.objectid
import struct
import time

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .. import errors as stream_errors

# Setup the database connection to MongoDB
# TODO Add support for specifying host, username and password
if "database" not in settings.DATA_STREAM_BACKEND_CONFIGURATION:
  raise ImproperlyConfigured("MongoDB datastream backend requires configuration!")

mongoengine.connect(settings.DATA_STREAM_BACKEND_CONFIGURATION["database"], alias = "datastream")

# TODO Should this be moved somewhere elese?
GRANULARITIES = [
  "seconds",
  "minutes",
  "hours",
  "days"
]

DOWNSAMPLERS = [
  "mean",
  "sum",
  "min",
  "max",
  "sum_squares",
  "std_dev",
  "count"
]

RESERVED_TAGS = [
  "metric_id",
  "downsamplers",
  "highest_granularity"
]

class DownsampleState(mongoengine.EmbeddedDocument):
  running_until = mongoengine.DateTimeField()
  timestamp = mongoengine.DateTimeField()

  meta = dict(
    allow_inheritance = False
  )

class Metric(mongoengine.Document):
  id = mongoengine.SequenceField(primary_key = True, db_alias = "datastream")
  downsamplers = mongoengine.ListField(mongoengine.StringField(choices = DOWNSAMPLERS))
  downsample_state = mongoengine.MapField(mongoengine.EmbeddedDocumentField(DownsampleState))
  highest_granularity = mongoengine.StringField(choices = GRANULARITIES)
  tags = mongoengine.ListField(mongoengine.DynamicField())

  meta = dict(
    db_alias = "datastream",
    collection = "metrics",
    indexes = ["tags"],
    allow_inheritance = False
  )

class hashabledict(dict):
  def __key(self):
    return tuple((k,self[k]) for k in sorted(self))
  def __hash__(self):
    return hash(self.__key())
  def __eq__(self, other):
    return self.__key() == other.__key()

class Downsamplers:
  """
  A container of downsampler classes.
  """
  class Base(object):
    """
    Base class for downsamplers.
    """
    def init(self): pass
    def update(self, datum): pass
    def finish(self, output): pass

  class Count(Base):
    """
    Counts the number of datapoints.
    """
    def init(self):
      self.count = 0

    def update(self, datum):
      self.count += 1

    def finish(self, output):
      output["c"] = self.count

  class Sum(Base):
    """
    Sums the datapoint values.
    """
    def init(self):
      self.sum = 0

    def update(self, datum):
      self.sum += datum

    def finish(self, output):
      output["s"] = float(self.sum)

  class SumSquares(Base):
    """
    Sums the squared datapoint values.
    """
    def init(self):
      self.sum = 0

    def update(self, datum):
      self.sum += datum*datum

    def finish(self, output):
      output["q"] = float(self.sum)

  class Min(Base):
    """
    Stores the minimum of the datapoint values.
    """
    def init(self):
      self.min = None

    def update(self, datum):
      if self.min is None:
        self.min = datum
      else:
        self.min = min(self.min, datum)

    def finish(self, output):
      output["l"] = self.min

  class Max(Base):
    """
    Stores the maximum of the datapoint values.
    """
    def init(self):
      self.max = None

    def update(self, datum):
      if self.max is None:
        self.max = datum
      else:
        self.max = max(self.max, datum)

    def finish(self, output):
      output["u"] = self.max

  class Mean(Base):
    """
    Computes the mean from sum and count (postprocess).
    """
    dependencies = ["sum", "count"]

    def postprocess(self, values):
      values["m"] = float(values["s"]) / values["c"]

  class StdDev(Base):
    """
    Computes the standard deviation from sum, count and sum squares
    (postprocess).
    """
    dependencies = ["sum", "count", "sum_squares"]

    def postprocess(self, values):
      n = float(values["c"])
      s = float(values["s"])
      ss = float(values["q"])
      values["d"] = (n * ss - s**2) / (n * (n-1))

class Backend(object):
  def __init__(self):
    """
    Initializes the MongoDB backend.
    """
    self.downsamplers = [
      ("count",       Downsamplers.Count),
      ("sum",         Downsamplers.Sum),
      ("sum_squares", Downsamplers.SumSquares),
      ("min",         Downsamplers.Min),
      ("max",         Downsamplers.Max),
      ("mean",        Downsamplers.Mean),
      ("std_dev",     Downsamplers.StdDev),
    ]

  def _process_tags(self, tags):
    """
    Checks that reserved tags are not used and converts dicts to their
    hashable counterparts, so they can be used in set operations.
    """
    converted_tags = set()

    for tag in tags:
      if isinstance(tag, dict):
        for reserved in RESERVED_TAGS:
          if reserved in tag:
            raise stream_errors.ReservedTagNameError

        # Convert dicts to hashable dicts so they can be used in set
        # operations
        tag = hashabledict(tag)

      converted_tags.add(tag)

    return converted_tags

  def ensure_metric(self, query_tags, tags, downsamplers, highest_granularity):
    """
    Ensures that a specified metric exists.

    :param query_tags: Tags which uniquely identify a metric
    :param tags: Tags that should be used (together with `query_tags`) to create a
      metric when it doesn't yet exist
    :param downsamplers: A set of names of downsampler functions for this metric
    :param highest_granularity: Predicted highest granularity of the data the metric
      will store, may be used to optimize data storage
    :return: A metric identifier
    """
    try:
      metric = Metric.objects.get(tags__all = query_tags)
    except Metric.DoesNotExist:
      # Create a new metric
      # TODO This is a possible race condition since MongoDB doesn't have transactions
      metric = Metric()

      # Some downsampling functions don't need to be stored in the database but
      # can be computed on the fly from other downsampled values
      downsamplers = set(downsamplers)
      for tag, d in self.downsamplers:
        if tag in downsamplers and hasattr(d, "dependencies"):
          downsamplers.update(d.dependencies)

      # Ensure that the granularity is a valid one and raise error otherwise
      if highest_granularity not in GRANULARITIES:
        raise stream_errors.UnsupportedGranularity

      metric.downsamplers = list(downsamplers)
      metric.highest_granularity = highest_granularity
      metric.tags = list(self._process_tags(query_tags).union(self._process_tags(tags)))

      # Initialize downsample state
      for granularity in GRANULARITIES[GRANULARITIES.index(highest_granularity) + 1:]:
        state = DownsampleState()
        state.running_until = datetime.datetime.utcnow() - datetime.timedelta(hours = 1)
        metric.downsample_state[granularity] = state

      metric.save()
    except mongoengine.ValidationError:
      raise stream_errors.UnsupportedDownsampler
    except Metric.MultipleObjectsReturned:
      raise stream_errors.MultipleMetricsReturned

    return metric.id

  def get_tags(self, metric_id):
    """
    Returns the tags for the specified metric.

    :param metric_id: Metric identifier
    :return: A list of tags for the metric
    """
    try:
      metric = Metric.objects.get(id = metric_id)
      tags = metric.tags
      tags += [
        { "metric_id" : metric.id },
        { "downsamplers" : metric.downsamplers },
        { "highest_granularity" : metric.highest_granularity }
      ]
    except Metric.DoesNotExist:
      raise stream_errors.MetricNotFound

    return tags

  def update_tags(self, metric_id, tags):
    """
    Updates metric tags with new tags, overriding existing ones.

    :param metric_id: Metric identifier
    :param tags: A list of new tags
    """
    Metric.objects(id = metric_id).update(tags = list(self._process_tags(tags)))

  def insert(self, metric_id, value):
    """
    Inserts a data point into the data stream.

    :param metric_id: Metric identifier
    :param value: Metric value
    """
    try:
      metric = Metric.objects.get(id = metric_id)
    except Metric.DoesNotExist:
      raise stream_errors.MetricNotFound

    # Insert the datapoint into appropriate granularity
    db = mongoengine.connection.get_db("datastream")
    collection = getattr(db.datapoints, metric.highest_granularity)
    id = collection.insert({ "m" : metric.id, "v" : value })
    # TODO Should this index be ensured somewhere else, not on every insert?
    collection.ensure_index([('m', pymongo.ASCENDING), ('_id', pymongo.ASCENDING)])

    # Check if we need to perform any downsampling
    if id:
      self._downsample_check(metric, id.generation_time)

  def _round_downsampled_timestamp(self, timestamp, granularity):
    """
    Rounds the timestamp to specific time boundary defined by the
    granularity.

    :param timestamp: Raw timestamp
    :param granularity: Wanted granularity
    :return: Rounded timestamp
    """
    round_map = {
      "seconds" : ["year", "month", "day", "hour", "minute", "second"],
      "minutes" : ["year", "month", "day", "hour", "minute"],
      "hours"   : ["year", "month", "day", "hour"],
      "days"    : ["year", "month", "day"]
    }

    return datetime.datetime(**{ atom : getattr(timestamp, atom) for atom in round_map[granularity]})

  def _downsample_check(self, metric, datum_timestamp):
    """
    Checks if we need to perform any metric downsampling. In case it is needed,
    downsample operations are automatically queued for later execution.

    :param metric: Metric instance
    :param datum_timestamp: Timestamp of the newly inserted datum
    """
    for granularity in GRANULARITIES[GRANULARITIES.index(metric.highest_granularity) + 1:]:
      state = metric.downsample_state.get(granularity, None)
      rounded_timestamp = self._round_downsampled_timestamp(datum_timestamp, granularity)
      if state is None or rounded_timestamp != state.timestamp:
        self._downsample(metric, granularity, rounded_timestamp)

  def _generate_timed_object_id(self, timestamp, metric_id):
    """
    Generates a unique ObjectID for a specific timestamp and metric identifier.

    :param timestamp: Desired timestamp
    :param metric_id: 8-byte packed metric identifier
    :return: A valid object identifier
    """
    oid = ""
    # 4 bytes timestamp
    oid += struct.pack(">i", int(time.mktime(timestamp.timetuple())))
    # 8 bytes of packed metric identifier
    oid += metric_id
    return pymongo.objectid.ObjectId(oid)

  # TODO This should be executed in a celery job in the background
  def _downsample(self, metric, granularity, current_timestamp):
    """
    Performs downsampling on the given metric and granularity.

    :param metric: Metric instance
    :param granularity: Lower granularity to downsample into
    :param current_timestamp: Timestamp of the last inserted datapoint
    """
    # Ensure that we are allowed to perform downsampling and atomically reserve our spot; note
    # that nothing bad would happen if two downsamplers would run for the same metric and granularity
    # at the same time, only processing time would be wasted, because the same values would get computed twice
    now = datetime.datetime.utcnow()
    db = mongoengine.connection.get_db("datastream")
    document = db.metrics.find_and_modify(
      { "_id" : metric.id, "downsample_state.%s.running_until" % granularity : { "$lt" : now } },
      { "$set" : { "downsample_state.%s.running_until" % granularity : now + datetime.timedelta(minutes = 1) } }
    )
    if not document:
      return
    else:
      metric = Metric._from_son(document)

    # Determine the interval that needs downsampling
    datapoints = getattr(db.datapoints, metric.highest_granularity)
    state = metric.downsample_state[granularity]
    if state.timestamp is not None:
      datapoints = datapoints.find({
        "m" : metric.id, "_id__gte" : pymongo.objectid.ObjectId.from_datetime(state.timestamp)
      })
    else:
      # All datapoints should be selected as we obviously haven't done any downsampling yet
      datapoints = datapoints.find({ "m" : metric.id })

    # Initialize downsamplers
    downsamplers = []
    for tag, downsampler in self.downsamplers:
      if tag in metric.downsamplers:
        downsamplers.append(downsampler())

    # Pack metric identifier to be used for object id generation
    metric_id = struct.pack(">Q", metric.id)

    downsampled_points = getattr(db.datapoints, granularity)
    last_timestamp = None
    for datapoint in datapoints.sort("_id"):
      ts = datapoint['_id'].generation_time
      rounded_timestamp = self._round_downsampled_timestamp(ts, granularity)
      if last_timestamp is None:
        for x in downsamplers:
          x.init()
      elif last_timestamp != rounded_timestamp:
        value = {}
        for x in downsamplers:
          x.finish(value)
          x.init()

        # Insert downsampled value
        point_id = self._generate_timed_object_id(rounded_timestamp, metric_id)
        downsampled_points.update(
          { "_id" : point_id, "m" : metric.id },
          { "_id" : point_id, "m" : metric.id, "v" : value },
          upsert = True
        )

      # Abort when we reach the current rounded timestamp as we will process all further
      # datapoints in the next downsampling run; do not call finish on downsamplers as it
      # has already been called above when some datapoints exist
      if rounded_timestamp >= current_timestamp:
        break

      # Update all downsamplers for the current datapoint
      for x in downsamplers:
        x.update(datapoint['v'])

      last_timestamp = rounded_timestamp

    # At the end, update the current timestamp in downsample_state
    db.metrics.update(
      { "_id" : metric.id },
      { "$set" : {
        # Update downsample state timestamp
        "downsample_state.%s.timestamp" % granularity : last_timestamp,
        # Ensure that "downsample mutex" is invalidated
        "downsample_state.%s.running_until" % granularity: now - datetime.timedelta(hours = 1)
      }}
    )
