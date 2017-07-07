from django.utils.translation import ugettext_lazy as _

from nodewatcher.core.generator.cgm import base as cgm_base, protocols as cgm_protocols, devices as cgm_devices


class MikrotikRBSXT2nDr3(cgm_devices.DeviceBase):
    """
    Mikrotik RouterBOARD SXT Lite2 (RBSXT2nDr3) device descriptor.
    """

    identifier = 'mt-rb-sxt2ndr3'
    name = "RouterBOARD SXT Lite2 (RBSXT2nDr3)"
    manufacturer = "MikroTik"
    url = 'https://mikrotik.com/product/RBSXT2nDr3'
    architecture = 'ar71xx_mikrotik'
    radios = [
        cgm_devices.IntegratedRadio('wifi0', _("Integrated wireless radio"), [
            cgm_protocols.IEEE80211BGN(
                cgm_protocols.IEEE80211BGN.SHORT_GI_20,
                cgm_protocols.IEEE80211BGN.SHORT_GI_40,
                cgm_protocols.IEEE80211BGN.RX_STBC1,
                cgm_protocols.IEEE80211BGN.DSSS_CCK_40,
            )
        ], [
            cgm_devices.AntennaConnector('a1', "Antenna0")
        ], [
            cgm_devices.DeviceRadio.MultipleSSID,
        ])
    ]
    antennas = [
        # TODO: This information is probably not correct
        cgm_devices.InternalAntenna(
            identifier='a1',
            polarization='horizontal',
            angle_horizontal=360,
            angle_vertical=75,
            gain=2,
        )
    ]
    switches = []
    ports = [
        cgm_devices.EthernetPort('lan0', "Lan0")
    ]
    port_map = {
        'openwrt': {
            'wifi0': 'radio0',
            'lan0': 'eth0',
        }
    }
    drivers = {
        'openwrt': {
            'wifi0': 'mac80211',
        }
    }
    profiles = {
        'lede': {
            'name': 'ubnt-unifiac-lite',
            'files': [
                '*-ar71xx-mikrotik-rb-nor-flash-16M-kernel.bin',
                '*-ar71xx-mikrotik-rb-nor-flash-16M-squashfs-sysupgrade.bin',
                '*-ar71xx-mikrotik-root.squashfs',
                '*-ar71xx-mikrotik-vmlinux.bin',
                '*-ar71xx-mikrotik-vmlinux.elf',
                '*-ar71xx-mikrotik-vmlinux.lzma',
                '*-ar71xx-mikrotik-vmlinux-lzma.elf',
            ]
        }
    }


# Register Mikrotik SXT devices.
cgm_base.register_device('lede', MikrotikRBSXT2nDr3)
