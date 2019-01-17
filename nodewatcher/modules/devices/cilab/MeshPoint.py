from django.utils.translation import ugettext_lazy as _

from nodewatcher.core.generator.cgm import base as cgm_base, protocols as cgm_protocols, devices as cgm_devices


class CilabMeshPointOne(cgm_devices.DeviceBase):
    """
    Cilab MeshPoint One device descriptor.
    """

    identifier = 'cilab-meshpoint-one'
    name = "Cilab MeshPoint One"
    manufacturer = "Cilab"
    url = 'https://www.meshpointone.com'
    architecture = 'ipq40xx_meshpoint'
    usb = True
    radios = [
        cgm_devices.IntegratedRadio('wifi0', _("Integrated wireless radio (2.4 GHz)"), [
            cgm_protocols.IEEE80211BGN(
                cgm_protocols.IEEE80211BGN.SHORT_GI_20,
                cgm_protocols.IEEE80211BGN.SHORT_GI_40,
                cgm_protocols.IEEE80211BGN.RX_STBC1,
                cgm_protocols.IEEE80211BGN.DSSS_CCK_40,
            )
        ], [
            cgm_devices.AntennaConnector('a1', "Antenna1")
        ], [
            cgm_devices.DeviceRadio.MultipleSSID,
        ]),
        cgm_devices.IntegratedRadio('wifi1', _("Integrated wireless radio (5 GHz)"), [
            cgm_protocols.IEEE80211AC(
                cgm_protocols.IEEE80211AC.SHORT_GI_20,
                cgm_protocols.IEEE80211AC.SHORT_GI_40,
                cgm_protocols.IEEE80211AC.RX_STBC1,
                cgm_protocols.IEEE80211AC.DSSS_CCK_40,
            )
        ], [
            cgm_devices.AntennaConnector('a2', "Antenna2")
        ], [
            cgm_devices.DeviceRadio.MultipleSSID,
        ])
    ]
    switches = [
        cgm_devices.Switch(
            'sw0', "Switch0",
            ports=[0, 3, 4],
            cpu_port=0,
            cpu_tagged=True,
            vlans=4096,
            configurable=True,
            presets=[
                cgm_devices.SwitchPreset('default', _("Default VLAN configuration"), vlans=[
                    cgm_devices.SwitchVLANPreset(
                        'wan0', "Wan0",
                        vlan=2,
                        ports=[0, 3],
                    ),
                    cgm_devices.SwitchVLANPreset(
                        'lan0', "Lan0",
                        vlan=1,
                        ports=[0, 4],
                    ),
                ])
            ]
        ),
    ]
    ports = []
    antennas = [
        # TODO: This information is probably not correct
        cgm_devices.InternalAntenna(
            identifier='a1',
            polarization='dual',
            angle_horizontal=360,
            angle_vertical=360,
            gain=3,
        ),
        cgm_devices.InternalAntenna(
            identifier='a2',
            polarization='dual',
            angle_horizontal=360,
            angle_vertical=360,
            gain=3,
        )
    ]
    port_map = {
        'openwrt': {
            'wifi0': 'radio0',
            'wifi1': 'radio1',
            'sw0': cgm_devices.SwitchPortMap('switch0', vlans='eth0.{vlan}'),
        }
    }
    drivers = {
        'openwrt': {
            'wifi0': 'mac80211',
            'wifi1': 'mac80211',
        }
    }
    profiles = {
        'lede': {
            'name': 'cilab_meshpoint-one',
            'files': [
                '*-ipq40xx-cilab_meshpoint-one-squashfs-nand-factory.ubi',
                '*-ipq40xx-cilab_meshpoint-one-squashfs-nand-sysupgrade.bin',
            ]
        }
    }


# Register Cilab router devices.
cgm_base.register_device('lede', CilabMeshPointOne)
