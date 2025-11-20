from mininet.net import Mininet
from mininet.node import OVSKernelSwitch
from mininet.link import TCLink
from mininet.topo import Topo
from mininet.log import setLogLevel
from mininet.cli import CLI

class L2Topo(Topo):
    def build(self):
        h1 = self.addHost('h1', ip='10.0.0.1/24')
        h2 = self.addHost('h2', ip='10.0.0.2/24')
        h3 = self.addHost('h3', ip='10.0.0.3/24')
        s1 = self.addSwitch('s1', cls=OVSKernelSwitch, protocols='OpenFlow13', failMode='secure')
        s2 = self.addSwitch('s2', cls=OVSKernelSwitch, protocols='OpenFlow13', failMode='standalone')
        self.addLink(h1, s1)   # s1-eth1
        self.addLink(h2, s1)   # s1-eth2
        self.addLink(s1, s2)   # s1-eth3 <-> s2-eth1
        self.addLink(h3, s2)   # s2-eth2 <-> h3-eth0

def main():
    net = Mininet(topo=L2Topo(), controller=None, autoSetMacs=True, autoStaticArp=True)
    net.start()
    CLI(net)     # keep network alive while you run ovs-ofctl
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    main()
