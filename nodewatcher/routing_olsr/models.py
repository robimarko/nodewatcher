from django.db import models
from django.utils.translation import ugettext as _

from nodewatcher.monitor import models as monitor_models
from nodewatcher.registry import registration

OLSR_PROTOCOL_NAME = "olsr"

# Register the routing protocol option so interfaces can use it
registration.point("node.config").register_choice("core.interfaces#routing_protocol", OLSR_PROTOCOL_NAME, _("OLSR"))

# Register the subnet announce option so interfaces can use it
registration.point("node.config").register_choice("core.interfaces.network#routing_announce", OLSR_PROTOCOL_NAME, _("OLSR HNA"))

class OlsrRoutingTopologyMonitor(monitor_models.RoutingTopologyMonitor):
    """
    OLSR routing topology.
    """
    pass

registration.point("node.monitoring").register_item(OlsrRoutingTopologyMonitor)

class OlsrTopologyLink(monitor_models.TopologyLink):
    """
    OLSR topology link.
    """
    lq = models.FloatField(default = 0.0)
    ilq = models.FloatField(default = 0.0)
    etx = models.FloatField(default = 0.0)

class OlsrRoutingAnnounceMonitor(monitor_models.RoutingAnnounceMonitor):
    """
    OLSR network announces.
    """
    pass

registration.point("node.monitoring").register_item(OlsrRoutingAnnounceMonitor)
