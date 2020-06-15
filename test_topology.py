import logging
import time
from functools import partial
from subprocess import call

from mininet.cli import CLI
from mininet.link import OVSLink
from mininet.log import info, setLogLevel
from mininet.net import Mininet
from mininet.node import RemoteController, OVSKernelSwitch

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)

CONTROLLER_IP = "127.0.0.1"
CONTROLLER_PORT = 6653
OPENFLOW_PROTOCOL = 'OpenFlow14'
IP_BASE = "10.0.88.0/24"
DPID_BASE = 1000
setLogLevel('info')

if __name__ == '__main__':

    # ---------- clean previous setup  -----------------------------
    call(["mn", "-c"])

    # ----------topology inputs -----------------------------
    # Core network topology
    # in
    # De Maesschalck, S., Colle, D., Lievens, I., Pickavet, M., Demeester, P., Mauz, C., ... & Derkacz, J.(2003).
    # Pan-European optical transport networks: An availability-based comparison.
    # Photonic Network Communications, 5(3), 203 - 225.
    switch_names = {1: "lon", 2: "ams", 3: "bru", 4: "par", 5: "ham",
                    6: "fra", 7: "str", 8: "zur", 9: "lyn", 10: "ber",
                    11: "mun", 12: "mil", 13: "pra", 14: "vie", 15: "zag",
                    16: "rom"}
    switch_link_matrix = [(1, 2), (1, 4), (2, 3), (2, 5), (3, 4),
                          (3, 6), (4, 7), (4, 9), (5, 6), (5, 10),
                          (6, 7), (6, 11), (7, 8), (8, 9), (8, 12),
                          (10, 11), (10, 13), (11, 12), (11, 14), (12, 16),
                          (13, 14), (14, 15), (15, 16)]
    host_count_per_switch = 1

    # ---------- initialize network  -----------------------------
    OpenFlow14Switch = partial(OVSKernelSwitch, protocols=OPENFLOW_PROTOCOL)

    net = Mininet(ipBase=IP_BASE)
    net.addController("c0", controller=RemoteController, link=OVSLink, ip=CONTROLLER_IP, port=CONTROLLER_PORT)

    try:
        # ----------switches and hosts -----------------------------
        switches = {}
        links = {}
        for sw_ind in switch_names:
            name = switch_names[sw_ind]
            dpid = DPID_BASE + sw_ind

            sw = net.addSwitch(name, dpid="%x" % dpid, cls=OpenFlow14Switch)
            switches[sw_ind] = sw
            for host_index in range(1, host_count_per_switch + 1):
                host = net.addHost(name + '%02d' % host_index)
                net.addLink(sw, host)

        # ---------- create links -----------------------------
        for item in switch_link_matrix:
            sw1 = switches[item[0]]
            sw2 = switches[item[1]]
            link = net.addLink(sw1, sw2)
            links[item] = link

        info('*** Starting network\n')
        net.start()
        time.sleep(2)

        info('*** Running CLI\n')
        CLI(net)

        info('*** Stopping network')
        net.stop()
    except Exception as err:
        info(err)

        net.stop()
