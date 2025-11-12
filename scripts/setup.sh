#!/bin/bash

# Update package lists
sudo apt-get update

# Install required packages
sudo apt-get install -y python3 python3-pip openvswitch-switch

# Install Python dependencies
pip3 install -r ../requirements.txt

# Set up Ryu controller
sudo mkdir -p /etc/ryu
sudo cp ../controllers/ryu/*.py /etc/ryu/

# Set up ONOS application
cd ../controllers/onos/apps/wan-optimizer
mvn clean install

# Start Open vSwitch
sudo service openvswitch-switch start

# Print completion message
echo "Setup completed successfully."