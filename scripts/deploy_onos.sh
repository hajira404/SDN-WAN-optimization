#!/bin/bash

# Navigate to the ONOS directory
cd ../controllers/onos/apps/wan-optimizer

# Build the ONOS application using Maven
mvn clean install

# Deploy the ONOS application
onos-app activate org.onosproject.wanopt

# Print deployment status
echo "ONOS WAN Optimizer application deployed successfully."