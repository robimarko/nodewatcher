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

    pkgcfg = pkgcfg.get()

    # Check if interface selected.
    if not pkgcfg.interface:
        raise cgm_base.ValidationError(_("EOIP must have a interface defined."))

    eoip_interface = cfg.network.find_named_section('interface', _managed_by=pkgcfg.interface)
    if not eoip_interface:
        raise cgm_base.ValidationError(_("Configured EOIP interface not found."))

    # Configure EOIP tunnels.

    tunnel = cfg['eoip'].add('tunnel')
    tunnel.interface = eoip_interface.get_key()
    tunnel.local_ip = pkgcfg.local_ip
    tunnel.remote_ip = pkgcfg.remote_ip
    tunnel.tunnel_id = pkgcfg.tunnel_id

    # Ensure that "eoip" package is installed.
    cfg.packages.update(['eoip'])
