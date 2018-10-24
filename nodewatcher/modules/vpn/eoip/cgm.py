from django import dispatch
from django.apps import apps
from django.utils.translation import ugettext as _

from nodewatcher.core.generator.cgm import base as cgm_base

from . import models


@cgm_base.register_platform_package('openwrt', 'eoip', models.EOIPTunnelConfig)
def eoip_config(node, pkgcfg, cfg):
    """
    Configures EOIP tunnels.
    """

    try:
        pkgcfg = pkgcfg.get()
    except models.EOIPTunnelConfig.MultipleObjectsReturned:
        raise cgm_base.ValidationError(_("Only one tunneldigger broker may be defined."))

    # Check if interface selected.
    if not pkgcfg.interface:
        raise cgm_base.ValidationError(_("EOIP must have a interface defined."))

    # Configure EOIP tunnels.

    tunnel = cfg['eoip'].add('tunnel')
    tunnel.interface = pkgcfg.interface
    tunnel.local_ip = pkgcfg.local_ip
    tunnel.remote_ip = pkgcfg.remote_ip
    tunnel.tunnel_id = pkgcfg.tunnel_id

    # Ensure that "eoip" package is installed.
    cfg.packages.update(['eoip'])
