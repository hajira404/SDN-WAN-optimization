# SDN-Based Traffic Engineering for WAN Optimization

## Overview
This project implements Software-Defined Networking (SDN) based traffic engineering for Wide Area Network (WAN) optimization. It addresses link congestion in hybrid WANs by dynamically rerouting traffic using Ryu and ONOS controllers, integrated with monitoring capabilities via Prometheus.

## Project Structure
The project is organized into several directories, each serving a specific purpose:

- **controllers**: Contains the SDN controllers (Ryu and ONOS) responsible for managing network flows and topology.
  - **ryu**: Implements traffic monitoring and flow management.
  - **onos**: Contains the WAN optimization application.

- **monitoring**: Includes Prometheus configuration and collectors for network metrics.
  
- **network**: Defines the network topology and switch configurations in JSON format.

- **scripts**: Contains shell scripts for setting up the environment and starting the controllers.

- **tests**: Includes unit and integration tests to ensure the functionality of the project.

- **docker-compose.yml**: Defines the services for running the project using Docker.

- **requirements.txt**: Lists the Python dependencies required for the project.

## Setup Instructions
1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd sdn-wan-optimization
   ```

2. **Install Dependencies**
   Use the provided `requirements.txt` to install Python dependencies.
   ```bash
   pip install -r requirements.txt
   ```

# SDN WAN Optimization — simplified (no Docker)

Overview
--
This repository contains a simplified, runnable demo of an SDN-based WAN optimization system.
The lightweight mode provides a Flask-based dashboard and a Prometheus-compatible metrics collector
so you can experiment locally without installing heavy controller stacks.

What was cleaned
--
- `docker-compose.yml` and a set of transient runtime files (PID/logs) were removed from the
   repository to keep the workspace focused on the lightweight demo you are running.

If you want to run the full Ryu/ONOS stack locally, those components are still present under
`controllers/` and `scripts/`, but running them may require additional system dependencies
(Python 3.8/3.9 for older Ryu builds, Java/Maven for ONOS). See the “Advanced” section below.

Quick start — lightweight demo (recommended)
--
This is the current working setup that I verified in this workspace.

1) Create or activate the project's venv (if you used the provided `venv` just activate it):

```bash
# if you already have the venv created (provided in repo)
source ./venv/bin/activate

# otherwise create one with a matching Python version
python3 -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
```

2) Start the simple web UI (serves on port 8080):

```bash
# from project root
./venv/bin/python run_simple.py &

# check the health endpoint
curl http://localhost:8080/health
```

3) Start the Prometheus-compatible metrics collector (optional, serves metrics on port 9090):

```bash
./venv/bin/python run_monitoring.py &

# Prometheus-style metrics will be available at
http://localhost:9090/metrics
```

4) Open the dashboard in a browser:

- Dashboard UI: http://localhost:8080/
- Smaller/simple static dashboard: http://localhost:8080/simple
- API endpoints:
   - http://localhost:8080/metrics  (JSON)
   - http://localhost:8080/flows
   - http://localhost:8080/topology
   - http://localhost:8080/health

Notes and troubleshooting
--
- If the Flask server does not respond, check `run_simple.log` (the app logs to stdout; if you
   start with `nohup` redirect to a file) and confirm the process is listening on port 8080.
- If you plan to run the Ryu apps, create a separate venv with Python 3.8 or 3.9 and install the
   original pinned packages there; some older packages (like `ryu`) may not build on newer Python.
- For browser problems (blank page), open Developer Tools (F12) and check Console/Network.

Advanced — Ryu and ONOS (optional)
--
- Ryu apps and an ONOS app are included in `controllers/` and scripts under `scripts/`.
- Running them requires extra system-level setup:
   - Ryu: a Python environment compatible with the `ryu` package (some versions require older
      Python). Use `./scripts/start_ryu.sh` after preparing the environment.
   - ONOS: JVM + Maven and a running ONOS instance. Use `./scripts/deploy_onos.sh` after
      building the ONOS app with Maven.

If you want I can:
- prepare a secondary venv for Ryu (Python 3.9), install the original pinned requirements, and
   try starting the Ryu controller for you, or
- help you configure a real Prometheus server to scrape `http://localhost:9090/metrics`.

Contact / Next steps
--
Tell me if you want me to remove more files, create a dedicated Ryu-compatible venv and install
the full dependencies, or prepare a short script to start/stop the demo and collector.
