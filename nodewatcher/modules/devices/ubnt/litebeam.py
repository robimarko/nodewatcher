from django.utils.translation import ugettext_lazy as _

from nodewatcher.core.generator.cgm import base as cgm_base, protocols as cgm_protocols, devices as cgm_devices


class UBNTLiteAP120(cgm_devices.DeviceBase):
    """
    UBNT LiteAP AC (LAP-120) device descriptor.
    """

    identifier = 'ub-lap-120'
    name = "LiteAP AC (LAP-120)"
    manufacturer = "Ubiquiti"
    url = 'http://www.ubnt.com/'
    architecture = 'ath79_generic'
    radios = [
        cgm_devices.IntegratedRadio('wifi0', _("Integrated wireless radio (5 GHz)"), [
            cgm_protocols.IEEE80211AC(
                cgm_protocols.IEEE80211AC.SHORT_GI_20,
                cgm_protocols.IEEE80211AC.SHORT_GI_40,
                cgm_protocols.IEEE80211AC.RX_STBC1,
                cgm_protocols.IEEE80211AC.DSSS_CCK_40,
            )
        ], [
            cgm_devices.AntennaConnector('a1', "Antenna1")
        ], [
            cgm_devices.DeviceRadio.MultipleSSID,
        ])
    ]
    switches = []
    ports = [
        cgm_devices.EthernetPort('lan0', "Lan0")
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
            'name': 'ubnt_lap-120',
            'files': [
                '*-ath79-generic-ubnt_lap-120-squashfs-factory.bin',
                '*-ath79-generic-ubnt_lap-120-squashfs-sysupgrade.bin',
            ]
        }
    }


# Register LitebBeam devices.
cgm_base.register_device('lede', UBNTLiteAP120)
