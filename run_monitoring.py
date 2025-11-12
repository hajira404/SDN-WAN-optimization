#!/usr/bin/env python3
"""
Simple network metrics collector for the SDN WAN Optimization system
"""

import time
import json
import logging
from prometheus_client import start_http_server, Counter, Gauge, Histogram
import requests

# Set up logging to file (avoid printing metrics info to terminal)
LOG_FILE = "metrics-collector.log"
formatter = logging.Formatter("%(asctime)s %(levelname)s:%(name)s: %(message)s")

# Configure root logger to write INFO+ into the log file
root_logger = logging.getLogger()
if not root_logger.handlers:
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
root_logger.setLevel(logging.INFO)

logger = logging.getLogger(__name__)

# Prometheus metrics
network_packets = Counter('network_packets_total', 'Total network packets processed')
bandwidth_usage = Gauge('bandwidth_usage_percent', 'Current bandwidth usage percentage')
link_latency = Histogram('link_latency_seconds', 'Link latency in seconds')

class NetworkMetricsCollector:
    def __init__(self):
        self.running = True
        self.sdn_controller_url = "http://localhost:8080"
        
    def collect_metrics(self):
        """Collect and expose network metrics"""
        while self.running:
            try:
                # Simulate collecting metrics from SDN controller
                response = requests.get(f"{self.sdn_controller_url}/metrics", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    
                    # Update Prometheus metrics
                    network_packets.inc(data.get('packet_count', 0))
                    bandwidth_usage.set(self._simulate_bandwidth_usage())
                    link_latency.observe(self._simulate_latency())
                    
                    logger.info(f"Metrics updated: packets={data.get('packet_count', 0)}")
                else:
                    logger.warning(f"Failed to get metrics from SDN controller: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"Cannot connect to SDN controller: {e}")
                # Continue running even if controller is not available
                
            except Exception as e:
                logger.error(f"Error collecting metrics: {e}")
                
            time.sleep(30)  # Collect metrics every 30 seconds
            
    def _simulate_bandwidth_usage(self):
        """Simulate bandwidth usage percentage"""
        import random
        return random.uniform(20, 80)  # Random bandwidth usage between 20-80%
        
    def _simulate_latency(self):
        """Simulate link latency"""
        import random
        return random.uniform(0.001, 0.1)  # Random latency between 1ms and 100ms

def main():
    logger.info("Starting Network Metrics Collector")
    
    # Start Prometheus metrics server
    start_http_server(9090)
    logger.info("Prometheus metrics server started on http://localhost:9090/metrics")
    
    # Start metrics collection
    collector = NetworkMetricsCollector()
    collector.collect_metrics()

if __name__ == '__main__':
    main()