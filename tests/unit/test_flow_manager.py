import unittest
from controllers.ryu.flow_manager import FlowManager

class TestFlowManager(unittest.TestCase):

    def setUp(self):
        self.flow_manager = FlowManager()

    def test_add_flow(self):
        flow = {'id': '1', 'match': {'in_port': 1}, 'actions': [{'type': 'OUTPUT', 'port': 2}]}
        result = self.flow_manager.add_flow(flow)
        self.assertTrue(result)
        self.assertIn(flow['id'], self.flow_manager.flows)

    def test_modify_flow(self):
        flow = {'id': '2', 'match': {'in_port': 1}, 'actions': [{'type': 'OUTPUT', 'port': 2}]}
        self.flow_manager.add_flow(flow)
        modified_flow = {'id': '2', 'match': {'in_port': 1}, 'actions': [{'type': 'OUTPUT', 'port': 3}]}
        result = self.flow_manager.modify_flow(modified_flow)
        self.assertTrue(result)
        self.assertEqual(self.flow_manager.flows['2']['actions'][0]['port'], 3)

    def test_delete_flow(self):
        flow = {'id': '3', 'match': {'in_port': 1}, 'actions': [{'type': 'OUTPUT', 'port': 2}]}
        self.flow_manager.add_flow(flow)
        result = self.flow_manager.delete_flow(flow['id'])
        self.assertTrue(result)
        self.assertNotIn(flow['id'], self.flow_manager.flows)

    def test_flow_not_found(self):
        result = self.flow_manager.delete_flow('non_existent_flow')
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()