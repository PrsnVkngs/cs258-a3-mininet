from mininet.net import Mininet
from mininet.node import Node, Host
from mininet.link import Link, TCLink
from mininet.log import setLogLevel, info
from mininet.cli import CLI

class LinuxRouter(Node):
    def config(self, **params):
        super().config(**params)
        self.cmd("sysctl -w net.ipv4.ip_forward=1")

    def terminate(self):
        self.cmd("sysctl -w net.ipv4.ip_forward=0")
        super().terminate()

def run():
    net = Mininet(link=TCLink, build=False)

    # Routers
    r1 = net.addHost('r1', cls=LinuxRouter)
    r2 = net.addHost('r2', cls=LinuxRouter)

    # Hosts
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.3.2/24')
    h3 = net.addHost('h3', ip='10.0.2.2/24')

    # Links + interface IPs on routers
    net.addLink(h1, r1)
    r1.setIP('10.0.0.3/24', intf=r1.defaultIntf()) 

    # r1 <-> r2
    L = net.addLink(r1, r2)
    intf_r1_r2 = r1.nameToIntf(L.intf1.name)
    intf_r2_r1 = r2.nameToIntf(L.intf2.name)
    r1.setIP('10.0.1.1/24', intf=intf_r1_r2)
    r2.setIP('10.0.1.2/24', intf=intf_r2_r1)

    # r2 <-> h3
    net.addLink(r2, h3)
    # set r2 IP on the h3-facing interface
    r2_intfs = [i for i in r2.intfList() if i != r2.defaultIntf() and i != intf_r2_r1]
    r2_to_h3 = [i for i in r2_intfs if r2.IP(i) == '0.0.0.0'][0]
    r2.setIP('10.0.2.1/24', intf=r2_to_h3)

    # r1 <-> h2
    net.addLink(r1, h2)
    # set r1 IP on the h2-facing interface
    r1_intfs = [i for i in r1.intfList() if i not in (r1.defaultIntf(), intf_r1_r2)]
    r1_to_h2 = [i for i in r1_intfs if r1.IP(i) == '0.0.0.0'][0]
    r1.setIP('10.0.3.4/24', intf=r1_to_h2)

    net.build()

    # Host default routes to their first-hop routers
    h1.cmd("ip route add default via 10.0.0.3")
    h2.cmd("ip route add default via 10.0.3.4")
    h3.cmd("ip route add default via 10.0.2.1")

    # Router static routes:
    # r1 needs to reach 10.0.2.0/24 via r2
    r1.cmd("ip route add 10.0.2.0/24 via 10.0.1.2")
    # r2 needs to reach 10.0.0.0/24 and 10.0.3.0/24 via r1
    r2.cmd("ip route add 10.0.0.0/24 via 10.0.1.1")
    r2.cmd("ip route add 10.0.3.0/24 via 10.0.1.1")

    # Pings to collect into result1.txt
    def run_ping(src, dst):
        return net.get(src).cmd(f"ping -c 1 {dst}; echo $?")

    with open("result1.txt", "w") as f:
        f.write("# h1 -> h3\n")
        f.write(run_ping("h1", "10.0.2.2"))
        f.write("\n# h2 -> h3\n")
        f.write(run_ping("h2", "10.0.2.2"))
        f.write("\n# h3 -> h1\n")
        f.write(run_ping("h3", "10.0.0.1"))
        f.write("\n# h3 -> h2\n")
        f.write(run_ping("h3", "10.0.3.2"))
    
    net.stop()
    

if __name__ == "__main__":
    setLogLevel('info')
    run()
