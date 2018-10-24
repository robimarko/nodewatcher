from django import apps


class EOIPTunnelConfig(apps.AppConfig):
    name = 'nodewatcher.modules.vpn.eoip'
    label = 'eoip'
    verbose_name = "EOIP tunnel configuration"
