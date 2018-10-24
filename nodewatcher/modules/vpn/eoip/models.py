import datetime

from django.apps import apps
from django.contrib.postgres import fields as postgres_fields
from django.db import models
from django.utils.translation import ugettext_lazy as _, ugettext

from polymorphic import models as polymorphic_models

from nodewatcher.core import validators as core_validators
from nodewatcher.core.registry import fields as registry_fields, registration
from nodewatcher.core.generator.cgm import models as cgm_models


class EOIPTunnelConfig(cgm_models.PackageConfig):
    """
    EOIP tunnel configuration.
    """

    interface = registry_fields.ReferenceChoiceField(
        cgm_models.InterfaceConfig,
        related_name='+',
        help_text=_("Select on which interface the broker should listen on."),
    )
    local_ip = models.GenericIPAddressField(null=True, unpack_ipv4=True, verbose_name=_("Local IP adress"))
    remote_ip = models.GenericIPAddressField(null=True, unpack_ipv4=True, verbose_name=_("Remote IP adress"))
    tunnel_id = models.PositiveIntegerField(default=0, verbose_name=_("Tunnel ID"))

    class RegistryMeta(cgm_models.PackageConfig.RegistryMeta):
        registry_name = _("EOIP tunnel configuration")

registration.point('node.config').register_item(EOIPTunnelConfig)
