# Coursera :
# - Software Defined Networking ( SDN ) course
# -- Programming Assignment : Layer -2 Firewall Application Professor : Nick Feamster
# Teaching Assistant : Arpit Gupta
from pox.core import core
from typing import List, Dict
import pox.openflow.libopenflow_01 as of
from pox.lib.revent import *
from pox.lib.util import dpidToStr
from pox.lib.addresses import EthAddr
from collections import namedtuple
import json
import os

log = core . getLogger ()

DESTINATION_PORT_LABEL = "destination_port"
SOURCE_IP_LABEL = "source_ip"
DESTINATION_IP_LABEL = "destination_ip"
TRANSPORT_PROTOCOL_LABEL = "transport_protocol"
FILENAME_RULES = "rules.json"

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

    def rule(self, rule_data)-> of.ofp_flow_mod:
        rule= of.ofp_flow_mod()
        rule.match.tp_dst = rule_data[DESTINATION_PORT_LABEL]
        rule.match.nw_src = rule_data[SOURCE_IP_LABEL]
        rule.match.nw_dst = rule_data[DESTINATION_IP_LABEL]
        rule.match.nw_proto = rule_data[TRANSPORT_PROTOCOL_LABEL]
        return rule

    def deserialize_rules(self) -> list[dict]: 
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
