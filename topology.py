from mininet.topo import Topo

HOSTS_COUNT = 4

class Topology(Topo):
    def build(self, switches_count):
        if switches_count < 2:
            print("[ERROR] We need at least 2 switches.")
            exit(-1)

        hosts=[]
        for host in range(HOSTS_COUNT):
            hosts.append(self.addHost(f"host_id{host}" ))

        switches=[]

        for i in range(switches_count):
            switches.append(self.addSwitch(f"switch_id{i}"))

        for i in range(1, switches_count):
            self.addLink(switches[i-1], switches[i])

        self.addLink(hosts[0], switches[0])
        self.addLink(hosts[1], switches[0])
        self.addLink(hosts[2], switches[-1])
        self.addLink(hosts[3], switches[-1])

topos={"topo":Topology}
