#!/usr/bin/env python3
"""
Simple standalone version of the SDN WAN Optimization system
This runs the monitoring and basic functionality without requiring complex Ryu setup
"""

import time
import threading
import logging
from flask import Flask, jsonify, request
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class SimpleTrafficMonitor:
    def __init__(self):
        self.packet_count = 0
        self.alert_threshold = 1000
        self.running = True
        
    def start_monitoring(self):
        """Start the monitoring thread"""
        def monitor():
            while self.running:
                time.sleep(10)
                logger.info(f"Current packet count: {self.packet_count}")
                if self.packet_count > self.alert_threshold:
                    logger.warning("Traffic alert: Packet count exceeded threshold!")
        
        thread = threading.Thread(target=monitor)
        thread.daemon = True
        thread.start()
        logger.info("Traffic monitoring started")

class SimpleFlowManager:
    def __init__(self):
        self.flows = {}
        self.running = True
        self._flow_idx = 1
        
    def add_flow(self, flow_id, flow_data):
        self.flows[flow_id] = flow_data
        logger.info(f"Added flow: {flow_id}")
        
    def get_flows(self):
        return self.flows

    def remove_flow(self, flow_id):
        if flow_id in self.flows:
            del self.flows[flow_id]
            logger.info(f"Removed flow: {flow_id}")

    def simulate_flow_management(self, monitor: SimpleTrafficMonitor, interval=6):
        """Background simulator that creates/removes flows based on packet load.

        - If packet_count is high, create flows (up to a cap).
        - If packet_count is low, remove some flows to simulate teardown.
        This demonstrates the flow manager reacting to traffic and produces
        visible entries under `/flows` for demo purposes.
        """
        import random

        def manager():
            while self.running:
                pkt = monitor.packet_count
                active = len(self.flows)

                # If traffic is high, create new flows
                if pkt > 200 and active < 20:
                    # create 1-3 new flows
                    for _ in range(random.randint(1, 3)):
                        fid = f"flow{self._flow_idx}"
                        self._flow_idx += 1
                        flow_data = {
                            "src": f"10.0.0.{random.randint(1,254)}",
                            "dst": f"10.0.1.{random.randint(1,254)}",
                            "priority": random.choice([100,200,300]),
                            "created_at": int(time.time()),
                        }
                        self.add_flow(fid, flow_data)

                # If traffic low, remove some flows
                if pkt < 150 and active > 0:
                    # remove 1-2 random flows
                    remove_n = min(active, random.randint(1, 2))
                    keys = list(self.flows.keys())
                    for fid in random.sample(keys, remove_n):
                        self.remove_flow(fid)

                # Occasionally update existing flows' metrics.
                # Recompute the current keys before sampling so we don't try
                # to sample more items than exist (which caused a ValueError
                # and terminated the thread previously).
                if random.random() < 0.3:
                    keys = list(self.flows.keys())
                    if keys:
                        k = min(3, len(keys))
                        for fid in random.sample(keys, k):
                            self.flows[fid]["last_seen_packets"] = random.randint(0, 1000)

                time.sleep(interval)

        thread = threading.Thread(target=manager, name="FlowManagerSim")
        thread.daemon = True
        thread.start()
        logger.info("Flow manager simulation started")

class SimpleTopologyDiscovery:
    def __init__(self):
        # Load topology from config file
        try:
            with open('network/topology/network_topology.json', 'r') as f:
                self.topology = json.load(f)
        except FileNotFoundError:
            self.topology = {"switches": [], "links": []}
            logger.warning("No topology file found, using empty topology")
    
    def get_topology(self):
        return self.topology

# Initialize components
traffic_monitor = SimpleTrafficMonitor()
flow_manager = SimpleFlowManager()
topology_discovery = SimpleTopologyDiscovery()

# Flask routes
@app.route('/')
def home():
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SDN WAN Optimization System</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .status-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .card:hover {
            transform: translateY(-5px);
        }
        .card h3 {
            margin: 0 0 15px 0;
            color: #4a5568;
        }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .running { background-color: #48bb78; }
        .stopped { background-color: #f56565; }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        .topology-view {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
        }
        .switch {
            display: inline-block;
            background: #4299e1;
            color: white;
            padding: 10px;
            margin: 5px;
            border-radius: 5px;
            font-size: 0.9em;
        }
        .api-endpoints {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
        }
        .endpoint {
            background: #f7fafc;
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
            font-family: monospace;
        }
        .refresh-btn {
            background: #4299e1;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
        }
        .refresh-btn:hover {
            background: #3182ce;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌐 SDN WAN Optimization System</h1>
            <p>Software-Defined Networking for Wide Area Network Optimization</p>
        </div>
        
        <div class="status-cards">
            <div class="card">
                <h3><span class="status-indicator running"></span>System Status</h3>
                <p><strong>Status:</strong> <span style="color: #48bb78;">RUNNING</span></p>
                <p><strong>Uptime:</strong> <span id="uptime">Loading...</span></p>
                <p><strong>Mode:</strong> Development</p>
            </div>
            
            <div class="card">
                <h3><span class="status-indicator running"></span>Traffic Monitor</h3>
                <p><strong>Packets Processed:</strong> <span id="packet-count">0</span></p>
                <p><strong>Alert Threshold:</strong> 1,000</p>
                <p><strong>Status:</strong> Active</p>
            </div>
            
            <div class="card">
                <h3><span class="status-indicator running"></span>Flow Manager</h3>
                <p><strong>Active Flows:</strong> <span id="flow-count">0</span></p>
                <p><strong>Flow Rules:</strong> Dynamic</p>
                <p><strong>Optimization:</strong> Enabled</p>
            </div>
            
            <div class="card">
                <h3><span class="status-indicator running"></span>Topology Discovery</h3>
                <p><strong>Switches:</strong> <span id="switch-count">4</span></p>
                <p><strong>Links:</strong> Active</p>
                <p><strong>Protocol:</strong> OpenFlow</p>
            </div>
        </div>
        
        <div class="metrics-grid">
            <div class="card">
                <h3>📊 Live Metrics</h3>
                <p><strong>Bandwidth Usage:</strong> <span id="bandwidth">Loading...</span>%</p>
                <p><strong>Link Latency:</strong> <span id="latency">Loading...</span> ms</p>
                <p><strong>Prometheus Metrics:</strong> <a href="/api/prometheus" target="_blank">View</a></p>
                <button class="refresh-btn" onclick="refreshMetrics()">Refresh Data</button>
                <label style="margin-left:10px;color:#fff;">Burst:</label>
                <input id="burst-amount" type="number" value="2000" style="width:100px;margin-left:8px;padding:6px;border-radius:4px;border:1px solid #ddd;" />
                <button class="refresh-btn" style="margin-left:8px;" onclick="simulateBurst()">Simulate Burst</button>
            </div>
            
            <div class="card">
                <h3>🔧 System Components</h3>
                <p>✅ Traffic Monitor</p>
                <p>✅ Flow Manager</p>
                <p>✅ Topology Discovery</p>
                <p>✅ Metrics Collector</p>
                <p>✅ Web Interface</p>
            </div>
        </div>
        
        <div class="topology-view">
            <h3>🏗️ Network Topology</h3>
            <p>Current network consists of 4 OpenFlow switches:</p>
            <div id="topology">
                <div class="switch">Switch 1 (100Mbps)</div>
                <div class="switch">Switch 2 (50-100Mbps)</div>
                <div class="switch">Switch 3 (75-100Mbps)</div>
                <div class="switch">Switch 4 (50-75Mbps)</div>
            </div>
        </div>
        
        <div class="api-endpoints">
            <h3>🔌 API Endpoints</h3>
            <div class="endpoint">GET <a href="/metrics">/metrics</a> - System metrics and stats</div>
            <div class="endpoint">GET <a href="/health">/health</a> - Health check</div>
            <div class="endpoint">GET <a href="/flows">/flows</a> - Current flow information</div>
            <div class="endpoint">GET <a href="/topology">/topology</a> - Network topology</div>
        </div>
    </div>
    
    <script>
        let startTime = Date.now();
        
        function updateUptime() {
            const uptime = Math.floor((Date.now() - startTime) / 1000);
            const hours = Math.floor(uptime / 3600);
            const minutes = Math.floor((uptime % 3600) / 60);
            const seconds = uptime % 60;
            document.getElementById('uptime').textContent = 
                `${hours.toString().padStart(2,'0')}:${minutes.toString().padStart(2,'0')}:${seconds.toString().padStart(2,'0')}`;
        }
        
        function refreshMetrics() {
            fetch('/metrics')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('packet-count').textContent = data.packet_count.toLocaleString();
                    document.getElementById('flow-count').textContent = data.flows;
                    document.getElementById('switch-count').textContent = data.topology.topology.switches.length;
                })
                .catch(error => console.error('Error:', error));
                
            // Simulate bandwidth and latency data
            document.getElementById('bandwidth').textContent = (Math.random() * 60 + 20).toFixed(1);
            document.getElementById('latency').textContent = (Math.random() * 50 + 10).toFixed(1);
        }
        
        // Update uptime every second
        setInterval(updateUptime, 1000);
        
        // Refresh metrics every 10 seconds
        setInterval(refreshMetrics, 10000);
        
        // Initial load
        refreshMetrics();

        function simulateBurst() {
            const amountEl = document.getElementById('burst-amount');
            const amount = parseInt(amountEl && amountEl.value) || 2000;
            fetch(`/simulate_burst?amount=${amount}`)
                .then(response => response.json())
                .then(data => {
                    document.getElementById('packet-count').textContent = data.packet_count.toLocaleString();
                    // refresh flows/topology display
                    refreshMetrics();
                })
                .catch(err => {
                    console.error('Burst error', err);
                    alert('Failed to trigger burst');
                });
        }
    </script>
</body>
</html>
    '''

@app.route('/simple')
def simple_dashboard():
    """Simple dashboard that loads faster"""
    with open('simple_dashboard.html', 'r') as f:
        return f.read()

@app.route('/metrics')
def metrics():
    return jsonify({
        "packet_count": traffic_monitor.packet_count,
        "flows": len(flow_manager.flows),
        "topology": topology_discovery.get_topology()
    })

@app.route('/flows')
def flows():
    return jsonify(flow_manager.get_flows())

@app.route('/topology')
def topology():
    return jsonify(topology_discovery.get_topology())

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/api/prometheus')
def prometheus_proxy():
    """Proxy to Prometheus metrics for the web interface"""
    try:
        import requests
        response = requests.get('http://localhost:9090/metrics', timeout=5)
        return response.text, 200, {'Content-Type': 'text/plain'}
    except:
        return "Prometheus metrics unavailable", 503


@app.route('/simulate_burst', methods=['GET', 'POST'])
def simulate_burst():
    """Trigger a simulated traffic burst.

    Query params:
      - amount: integer, how many packets to add (default 2000)

    Returns the new packet_count.
    """
    try:
        amount = int(request.args.get('amount', request.form.get('amount', 2000)))
    except Exception:
        amount = 2000

    # Reset packet count then set to the burst amount so bursts don't accumulate
    old = traffic_monitor.packet_count
    traffic_monitor.packet_count = amount
    logger.info(f"Simulated burst: reset {old} -> {amount}, new packet_count={traffic_monitor.packet_count}")
    return jsonify({"packet_count": traffic_monitor.packet_count, "added": amount})

def main():
    logger.info("Starting SDN WAN Optimization System (Simple Mode)")
    
    # Start monitoring
    traffic_monitor.start_monitoring()

    # Start flow manager simulation so flows are created/removed based on load
    try:
        flow_manager.simulate_flow_management(traffic_monitor)
    except Exception:
        logger.exception("Failed to start flow manager simulation")
    
    # Start Flask app
    logger.info("Starting web interface on http://localhost:8080")
    # Run without the Flask reloader to avoid multiple processes and reloader-related
    # issues when launching from background or in containers. Use a single process
    # so monitoring and HTTP clients receive responses reliably.
    app.run(host='0.0.0.0', port=8080, debug=False)

if __name__ == '__main__':
    main()