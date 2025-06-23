from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.revent import *
from pox.lib.util import dpidToStr
from pox.lib.addresses import EthAddr, IPAddr
import pox.lib.packet as pkt
import json

log = core.getLogger ()

MAIN_SWITCH_ID = 1

IPv4_CONFIG = "v4"
IPv6_CONFIG = "v6"
UDP_PROTOCOL = "UDP"
TCP_PROTOCOL = "TCP"

IP_LABEL = "ip_version"
PORT_LABEL = "dst_port"
SRC_IP_LABEL = "src_ip"
DST_IP_LABEL = "dst_ip"
SRC_MAC_LABEL = "src_mac"
DST_MAC_LABEL = "dst_mac"
TRANSPORT_PROTOCOL_LABEL = "transport_protocol"

def _get_transport_protocol(protocol):
    if protocol == UDP_PROTOCOL:
        return pkt.ipv4.UDP_PROTOCOL
    elif protocol == TCP_PROTOCOL:
        return pkt.ipv4.TCP_PROTOCOL
    return None

def _get_ip_version(version):
    if version == IPv4_CONFIG:
        return pkt.ethernet.IP_TYPE
    elif version == IPv6_CONFIG:
        return pkt.ethernet.IPV6_TYPE
    return None

def _read_field(rule, field):
    if field in rule:
        if field == IP_LABEL:
            return _get_ip_version(rule[field])
        elif field == TRANSPORT_PROTOCOL_LABEL:
            return _get_transport_protocol(rule[field])
        elif field == SRC_IP_LABEL or field == DST_IP_LABEL:
            return IPAddr(rule[field])
        elif field == SRC_MAC_LABEL or field == DST_MAC_LABEL:
            return EthAddr(rule[field])
        elif field == PORT_LABEL:
            return int(rule[field])
    return None

def _build_rule(port=None, src_ip=None, dst_ip=None, src_mac=None, dst_mac=None, transport_protocol=None, ip_protocol=IPv6_CONFIG):
    rule = of.ofp_flow_mod()
    rule.match.dl_type = ip_protocol
    rule.match.tp_dst = port
    rule.match.nw_src = src_ip
    rule.match.nw_dst = dst_ip
    rule.match.dl_dst = src_mac
    rule.match.dl_src = dst_mac
    rule.match.nw_proto = transport_protocol

    return rule

def _read_rules_file(filename):
    file = open(filename)
    config = json.load(file)
    file.close()
    return config["rules"]

class Firewall (EventMixin):
    def __init__ (self):
        self.listenTo(core.openflow)
        self._set_rules('rules.json')
        log.debug("Enabling Firewall Module")
        
    def _handle_ConnectionUp (self , event):
        log.info("Switch {} is connected with controller: ".format(event.dpid))
        if event.dpid == self.swith_id: 
            self._load_rules(event)
    
    def _load_rules(self, event):
        for rule in self.rules:
            rule = _build_rule(port=_read_field(rule, PORT_LABEL), 
                               src_ip=_read_field(rule, SRC_IP_LABEL), 
                               dst_ip=_read_field(rule, DST_IP_LABEL),
                               src_mac=_read_field(rule, SRC_MAC_LABEL),
                               dst_mac=_read_field(rule, DST_MAC_LABEL),
                               transport_protocol=_read_field(rule, TRANSPORT_PROTOCOL_LABEL), 
                               ip_protocol=_read_field(rule, IP_LABEL))
            event.connection.send(rule)
    
        log.info("Firewall rules installed on %s switch", dpidToStr(event.dpid))  

    def _set_rules(self, filename):
        self.swith_id = MAIN_SWITCH_ID 
        self.rules = _read_rules_file(filename)
        for rule, i in enumerate(self.rules):
            print("Rule {}: {}".format(rule, i))
    
def launch():
    core.registerNew(Firewall)