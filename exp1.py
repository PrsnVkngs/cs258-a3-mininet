from mininet.net import Mininet
from mininet.node import Node
from mininet.link import TCLink
from mininet.log import setLogLevel
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
    h1 = net.addHost('h1')  # IPs set later per-link
    h2 = net.addHost('h2')
    h3 = net.addHost('h3')

    # Links (keep references to both ends)
    L_h1_r1 = net.addLink(h1, r1)      # h1-eth0 <-> r1-eth?
    L_r1_r2 = net.addLink(r1, r2)      # r1-eth? <-> r2-eth?
    L_r2_h3 = net.addLink(r2, h3)      # r2-eth? <-> h3-eth0
    L_r1_h2 = net.addLink(r1, h2)      # r1-eth? <-> h2-eth0

    net.build()

    # h1—r1: 10.0.0.1/24 (h1) ↔ 10.0.0.3/24 (r1)
    h1.setIP('10.0.0.1/24', intf=L_h1_r1.intf1)
    r1.setIP('10.0.0.3/24', intf=L_h1_r1.intf2)

    # r1—r2: 10.0.1.1/24 (r1) ↔ 10.0.1.2/24 (r2)
    r1.setIP('10.0.1.1/24', intf=L_r1_r2.intf1)
    r2.setIP('10.0.1.2/24', intf=L_r1_r2.intf2)

    # r2—h3: 10.0.2.1/24 (r2) ↔ 10.0.2.2/24 (h3)
    r2.setIP('10.0.2.1/24', intf=L_r2_h3.intf1)
    h3.setIP('10.0.2.2/24', intf=L_r2_h3.intf2)

    # r1—h2: 10.0.3.4/24 (r1) ↔ 10.0.3.2/24 (h2)
    r1.setIP('10.0.3.4/24', intf=L_r1_h2.intf1)
    h2.setIP('10.0.3.2/24', intf=L_r1_h2.intf2)

    # Default routes on hosts
    h1.cmd("ip route add default via 10.0.0.3")
    h2.cmd("ip route add default via 10.0.3.4")
    h3.cmd("ip route add default via 10.0.2.1")

    # Static routes on routers
    r1.cmd("ip route add 10.0.2.0/24 via 10.0.1.2")
    r2.cmd("ip route add 10.0.0.0/24 via 10.0.1.1")
    r2.cmd("ip route add 10.0.3.0/24 via 10.0.1.1")

    # for n in (h1, h2, h3, r1, r2):
    #     print(n.name, n.cmd("ip -br addr"))

    # Run pings and write result1.txt
    def ping(src, dst):
        return net.get(src).cmd(f"ping -c 1 {dst}")

    with open("result1.txt", "w") as f:
        f.write("# h1 -> h3\n")
        f.write(ping("h1", "10.0.2.2") + "\n")
        f.write("# h2 -> h3\n")
        f.write(ping("h2", "10.0.2.2") + "\n")
        f.write("# h3 -> h1\n")
        f.write(ping("h3", "10.0.0.1") + "\n")
        f.write("# h3 -> h2\n")
        f.write(ping("h3", "10.0.3.2") + "\n")

    net.stop()

if __name__ == "__main__":
    setLogLevel('info')
    run()
