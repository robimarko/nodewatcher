import datetime

from django.apps import apps
from django.contrib.postgres import fields as postgres_fields
from django.db import models
from django.utils.translation import ugettext_lazy as _, ugettext

from polymorphic import models as polymorphic_models

from nodewatcher.core import validators as core_validators
from django.core.validators import MaxValueValidator, MinValueValidator 
from nodewatcher.core.registry import fields as registry_fields, registration
from nodewatcher.core.generator.cgm import models as cgm_models


class EOIPTunnelConfig(cgm_models.PackageConfig):
    """
    EOIP tunnel configuration.
    """

    ip_options = (
        ('-4', 'IPv4'),
        ('-6', 'IPv6')
    )
    ip_family = models.CharField(max_length=5, choices=ip_options, default='-4', verbose_name=_("IP Family"))
    bridge_interface = registry_fields.ReferenceChoiceField(
        cgm_models.BridgeInterfaceConfig,
        related_name='+',
        help_text=_("Select bridge to bind to"),
    )
    interface = models.CharField(max_length=40, default="tap0", verbose_name=_("EOIP interface"))
    local_ip = models.GenericIPAddressField(null=True, unpack_ipv4=True, verbose_name=_("Local IP adress"))
    remote_ip = models.GenericIPAddressField(null=True, unpack_ipv4=True, verbose_name=_("Remote IP adress"))
    tunnel_id = models.PositiveIntegerField(default=0, verbose_name=_("Tunnel ID"))
    mtu = models.PositiveIntegerField(default=1458, validators=[MinValueValidator(0), MaxValueValidator(9000)], verbose_name=_("MTU"))
    custom_route = models.CharField(max_length=100, blank=True, verbose_name=_("Custom route to be executed"))

    class RegistryMeta(cgm_models.PackageConfig.RegistryMeta):
        registry_name = _("EOIP tunnel configuration")

registration.point('node.config').register_item(EOIPTunnelConfig)
