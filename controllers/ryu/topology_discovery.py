from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, set_ev_cls
from ryu.lib import hub
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.ofproto import ofproto_v1_3
import json

class TopologyDiscovery(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(TopologyDiscovery, self).__init__(*args, **kwargs)
        self.topology = {}
        self.switches = set()
        self.links = set()
        hub.spawn(self._monitor)

    @set_ev_cls(ofp_event.EventOFPStateChange, [MAIN_DISPATCHER])
    def state_change_handler(self, ev):
        switch = ev.switch
        if ev.state == 'up':
            self.switches.add(switch.id)
            self.topology[switch.id] = {'links': []}
            self.logger.info("Switch %s is up", switch.id)
        elif ev.state == 'down':
            self.switches.discard(switch.id)
            self.topology.pop(switch.id, None)
            self.logger.info("Switch %s is down", switch.id)

    @set_ev_cls(ofp_event.EventOFPPortStatus, [MAIN_DISPATCHER])
    def port_status_handler(self, ev):
        port = ev.port
        switch_id = ev.switch.id
        if port.state == 'up':
            self.topology[switch_id]['links'].append(port.port_no)
            self.logger.info("Port %s on switch %s is up", port.port_no, switch_id)
        elif port.state == 'down':
            self.topology[switch_id]['links'].remove(port.port_no)
            self.logger.info("Port %s on switch %s is down", port.port_no, switch_id)

    def _monitor(self):
        while True:
            self.logger.info("Current topology: %s", json.dumps(self.topology, indent=4))
            hub.sleep(10)  # Monitor every 10 seconds