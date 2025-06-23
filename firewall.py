# Coursera :
# - Software Defined Networking ( SDN ) course
# -- Programming Assignment : Layer -2 Firewall Application Professor : Nick Feamster
# Teaching Assistant : Arpit Gupta
from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.revent import *
from pox.lib.util import dpidToStr
from pox.lib.addresses import EthAddr, IPAddr
import json
import os


log = core . getLogger ()

DESTINATION_PORT_LABEL = "destination_port"
SOURCE_IP_LABEL = "source_ip"
DESTINATION_IP_LABEL = "destination_ip"
TRANSPORT_PROTOCOL_LABEL = "transport_protocol"
#FILENAME_RULES = "rules.json"
FILENAME_RULES = os.path.join(os.path.dirname(__file__), "rules.json")

class Firewall(EventMixin) :
    def __init__ ( self ) :
        self.ofp_rules = []
        self.listenTo(core.openflow)
        log.debug( "Enabling Firewall Module " )
        self.setup_rules()

    def setup_rules(self):
        rules_data= self.deserialize_rules()
        for rule_data in rules_data:
            self.ofp_rules.append(self.rule(rule_data))

    def rule(self, rule_data):
        rule = of.ofp_flow_mod()
        if DESTINATION_PORT_LABEL in rule_data:
            rule.match.tp_dst = int(rule_data[DESTINATION_PORT_LABEL])
        if SOURCE_IP_LABEL in rule_data:
            rule.match.nw_src = IPAddr(rule_data[SOURCE_IP_LABEL])
        if DESTINATION_IP_LABEL in rule_data:
            rule.match.nw_dst = IPAddr(rule_data[DESTINATION_IP_LABEL])
        if TRANSPORT_PROTOCOL_LABEL in rule_data:
            rule.match.nw_proto = rule_data[TRANSPORT_PROTOCOL_LABEL]

        return rule

    def deserialize_rules(self):#-> list[dict]
        file = open(FILENAME_RULES)
        config = json.load(file)
        file.close()
        return config["rules"]

    def _handle_ConnectionUp(self,event) :
        log.info("ConnectionUp for switch {}: ".format(dpidToStr(event.dpid)))
        for rule in self.ofp_rules:         
            event.connection.send(rule)

def launch() :
    core.registerNew(Firewall)
