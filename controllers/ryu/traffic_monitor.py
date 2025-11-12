from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, set_ev_cls
from ryu.lib import hub
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
import prometheus_client

class TrafficMonitor(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(TrafficMonitor, self).__init__(*args, **kwargs)
        self.metrics = prometheus_client.Counter('traffic_monitor_packets', 'Number of packets monitored')
        self.alert_threshold = 1000  # Example threshold for alerts
        self.monitor_thread = hub.spawn(self.monitor_traffic)

    @set_ev_cls(ofp_event.EventPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        pkt = packet.Packet(ev.msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        if eth:
            self.metrics.inc()  # Increment the packet counter
            self.check_alerts()

    def check_alerts(self):
        if self.metrics._value.get() > self.alert_threshold:
            self.send_alert()

    def send_alert(self):
        self.logger.warning("Traffic alert: Packet count exceeded threshold!")

    def monitor_traffic(self):
        while True:
            hub.sleep(10)  # Monitor every 10 seconds
            self.logger.info("Current packet count: %d", self.metrics._value.get())