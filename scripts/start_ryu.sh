#!/bin/bash

# Start the Ryu controller for WAN optimization
ryu-manager --verbose \
    --ofp-tcp-listen-port 6633 \
    --set-logger=debug \
    sdn-wan-optimization/controllers/ryu/traffic_monitor.py \
    sdn-wan-optimization/controllers/ryu/flow_manager.py \
    sdn-wan-optimization/controllers/ryu/topology_discovery.py