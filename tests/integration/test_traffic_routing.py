import unittest
from controllers.ryu.flow_manager import FlowManager
from controllers.ryu.traffic_monitor import TrafficMonitor

class TestTrafficRouting(unittest.TestCase):

    def setUp(self):
        self.flow_manager = FlowManager()
        self.traffic_monitor = TrafficMonitor()

    def test_dynamic_rerouting(self):
        # Simulate traffic conditions
        initial_flow = {'src': '10.0.0.1', 'dst': '10.0.0.2', 'bandwidth': 100}
        self.flow_manager.add_flow(initial_flow)

        # Simulate congestion
        self.traffic_monitor.detect_congestion(initial_flow)

        # Reroute traffic
        new_flow = {'src': '10.0.0.1', 'dst': '10.0.0.3', 'bandwidth': 100}
        self.flow_manager.reroute_flow(initial_flow, new_flow)

        # Verify that the flow has been updated
        self.assertIn(new_flow, self.flow_manager.get_flows())
        self.assertNotIn(initial_flow, self.flow_manager.get_flows())

    def test_traffic_monitoring(self):
        # Simulate traffic monitoring
        flow = {'src': '10.0.0.1', 'dst': '10.0.0.2', 'bandwidth': 100}
        self.flow_manager.add_flow(flow)

        # Check if traffic is being monitored
        metrics = self.traffic_monitor.collect_metrics()
        self.assertIn(flow, metrics)

if __name__ == '__main__':
    unittest.main()