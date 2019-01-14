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

    eoip_bridge = cfg.network.find_named_section('interface', _managed_by=pkgcfg.bridge_interface)
    if not eoip_bridge:
        raise cgm_base.ValidationError(_("Configured EOIP bridge not found."))

    # Configure EOIP tunnels.

    tunnel = cfg['eoip'].add('tunnel')
    tunnel.ip_family = pkgcfg.ip_family
    tunnel.interface = pkgcfg.interface
    tunnel.bridge = eoip_bridge.get_key()
    tunnel.local_ip = pkgcfg.local_ip
    tunnel.remote_ip = pkgcfg.remote_ip
    tunnel.tunnel_id = pkgcfg.tunnel_id
    tunnel.mtu = pkgcfg.mtu
    tunnel.custom_route = pkgcfg.custom_route

    # Ensure that "eoip" and "ipset" packages are installed.
    cfg.packages.update(['eoip', 'ipset'])
