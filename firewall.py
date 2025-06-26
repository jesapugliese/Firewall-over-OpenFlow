from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.revent import EventMixin
from pox.lib.util import dpidToStr
from pox.lib.addresses import EthAddr
import json
import pox.lib.packet as pkt

log = core.getLogger()

FILENAME_RULES = "rules.json"
SOURCE_MAC_LABEL = "src_mac"
DESTINATION_MAC_LABEL = "dst_mac"
DESTINATION_PORT_LABEL = "dst_port"
TRANSPORT_PROTOCOL_LABEL = "transport_protocol"
IP_VERSION_LABEL = "ip_version"

UDP_UPPER = "UDP"
TCP_UPPER = "TCP"
IPV4_UPPER = "IPV4"
IPV6_UPPER = "IPV6"

class Firewall(EventMixin):
    def __init__(self):
        self.ofp_rules = []
        self.listenTo(core.openflow)
        log.info("Enabling Firewall Module")
        self.protocols = [(UDP_UPPER, pkt.ipv4.UDP_PROTOCOL), (TCP_UPPER, pkt.ipv4.TCP_PROTOCOL)] 
        self.ip_versions = [(IPV4_UPPER, pkt.ethernet.IP_TYPE), (IPV6_UPPER, pkt.ethernet.IPV6_TYPE)]
        self.setup_rules()

    def setup_rules(self):
        log.info("Setting up rules")
        rules_data = self.deserialize_rules()
        for rule_data in rules_data:
            log.info("Processing rule: {}".format(rule_data["name"]))

            rules = [self.rule(rule_data)]

            added_rules = []
            for rule in rules:
                if rule.match.nw_proto is None:
                    # Adding the rule for each protocol
                    rule.match.nw_proto = self.protocols[0][1]
                    for _, value in self.protocols[1:]:
                        added_rule_data = rule_data.copy()
                        added_rule = self.rule(added_rule_data)
                        added_rule.match.nw_proto = value
                        added_rules.append(added_rule)
            rules.extend(added_rules)

            added_rules = []
            for rule in rules:
                if rule.match.dl_type is None:
                    # Adding the rule for each IP version
                    rule.match.dl_type = self.ip_versions[0][1]
                    for _, value in self.ip_versions[1:]:
                        added_rule_data = rule_data.copy()
                        added_rule = self.rule(added_rule_data)
                        added_rule.match.dl_type = value
                        added_rules.append(added_rule)
            rules.extend(added_rules)

            self.ofp_rules.extend(rules)

    def rule(self, rule_data):
        rule = of.ofp_flow_mod()

        if SOURCE_MAC_LABEL in rule_data:
            rule.match.dl_src = EthAddr(rule_data[SOURCE_MAC_LABEL])

        if DESTINATION_MAC_LABEL in rule_data:
            rule.match.dl_dst = EthAddr(rule_data[DESTINATION_MAC_LABEL])

        if DESTINATION_PORT_LABEL in rule_data:
            rule.match.tp_dst = rule_data[DESTINATION_PORT_LABEL]

        if TRANSPORT_PROTOCOL_LABEL in rule_data:
            protocol = rule_data[TRANSPORT_PROTOCOL_LABEL]
            for name, value in self.protocols:
                if protocol.upper() == name:
                    rule.match.nw_proto = value
                    break

        if IP_VERSION_LABEL in rule_data:
            ip_version = rule_data[IP_VERSION_LABEL]
            for name, value in self.ip_versions:
                if ip_version.upper() == name:
                    rule.match.dl_type = value
                    break

        return rule

    def deserialize_rules(self):
        with open(FILENAME_RULES) as file:
            config = json.load(file)
        return config["rules"]

    def _handle_ConnectionUp(self, event):
        log.info("ConnectionUp for switch {}: ".format(dpidToStr(event.dpid)))
        for rule in self.ofp_rules:
            event.connection.send(rule)


def launch():
    core.registerNew(Firewall)
