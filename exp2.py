from mininet.net import Mininet
from mininet.node import OVSKernelSwitch, Controller
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.topo import Topo

class L2Topo(Topo):
    def build(self):
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')

        s1 = self.addSwitch('s1', cls=OVSKernelSwitch, protocols='OpenFlow13', failMode='secure')
        s2 = self.addSwitch('s2', cls=OVSKernelSwitch, protocols='OpenFlow13', failMode='standalone')
        
        self.addLink(h1, s1)  # s1-eth1
        self.addLink(h2, s1)  # s1-eth2
        self.addLink(s1, s2)  # s1-eth3 <-> s2-eth1
        self.addLink(h3, s2)  # s2-eth2 <-> h3-eth0

def main():
    net = Mininet(topo=L2Topo(), controller=None, autoSetMacs=True, autoStaticArp=True) 
    net.start()
    
    out1 = net.get('h1').cmd('ping -c 1 h3')
    out2 = net.get('h2').cmd('ping -c 1 h3')

    with open('result2.txt', 'w') as f:
        f.write('# BEFORE adding flows to s1\n')
        f.write('## h1 -> h3\n' + out1 + '\n')
        f.write('## h2 -> h3\n' + out2 + '\n')

    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    main()
