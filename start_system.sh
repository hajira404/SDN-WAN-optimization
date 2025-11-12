#!/bin/bash

# SDN WAN Optimization System Startup Script
# This script starts all components of the system

echo "Starting SDN WAN Optimization System..."

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment
source venv/bin/activate

# Function to start a component in the background
start_component() {
    local name="$1"
    local script="$2"
    local logfile="$3"
    
    echo "Starting $name..."
    nohup python3 "$script" > "$logfile" 2>&1 &
    echo $! > "${name}.pid"
    echo "$name started (PID: $(cat ${name}.pid))"
}

# Function to check if a process is running
check_process() {
    local name="$1"
    local pidfile="${name}.pid"
    
    if [ -f "$pidfile" ]; then
        local pid=$(cat "$pidfile")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo "$name is running (PID: $pid)"
            return 0
        else
            echo "$name is not running"
            rm -f "$pidfile"
            return 1
        fi
    else
        echo "$name is not running"
        return 1
    fi
}

# Function to stop all components
stop_components() {
    echo "Stopping all components..."
    
    for pidfile in *.pid; do
        if [ -f "$pidfile" ]; then
            local pid=$(cat "$pidfile")
            local name=$(basename "$pidfile" .pid)
            
            if ps -p "$pid" > /dev/null 2>&1; then
                echo "Stopping $name (PID: $pid)..."
                kill "$pid"
                sleep 2
                
                # Force kill if still running
                if ps -p "$pid" > /dev/null 2>&1; then
                    echo "Force stopping $name..."
                    kill -9 "$pid"
                fi
            fi
            
            rm -f "$pidfile"
        fi
    done
    
    echo "All components stopped."
}

# Function to show status
show_status() {
    echo "SDN WAN Optimization System Status:"
    echo "=================================="
    check_process "sdn-controller"
    check_process "metrics-collector"
    echo ""
    echo "Access points:"
    echo "- SDN Controller Web Interface: http://localhost:8080"
    echo "- Prometheus Metrics: http://localhost:9090/metrics"
    echo "- System Status: http://localhost:8080/health"
}

# Function to show logs
show_logs() {
    local component="$1"
    if [ -n "$component" ]; then
        if [ -f "${component}.log" ]; then
            echo "=== $component logs ==="
            tail -f "${component}.log"
        else
            echo "No logs found for $component"
        fi
    else
        echo "Available log files:"
        ls -1 *.log 2>/dev/null || echo "No log files found"
    fi
}

# Main script logic
case "$1" in
    start)
        echo "Starting SDN WAN Optimization System..."
        
        # Check if Open vSwitch is running
        if ! systemctl is-active --quiet openvswitch-switch; then
            echo "Starting Open vSwitch..."
            sudo systemctl start openvswitch-switch
        fi
        
        # Start SDN controller
        start_component "sdn-controller" "run_simple.py" "sdn-controller.log"
        sleep 3
        
        # Start metrics collector
        start_component "metrics-collector" "run_monitoring.py" "metrics-collector.log"
        sleep 2
        
        echo ""
        show_status
        echo ""
        echo "System startup complete!"
        echo "You can now access the web interface at http://localhost:8080"
        ;;
        
    stop)
        stop_components
        ;;
        
    restart)
        stop_components
        sleep 3
        "$0" start
        ;;
        
    status)
        show_status
        ;;
        
    logs)
        show_logs "$2"
        ;;
        
    *)
        echo "Usage: $0 {start|stop|restart|status|logs [component]}"
        echo ""
        echo "Commands:"
        echo "  start    - Start all SDN WAN optimization components"
        echo "  stop     - Stop all components"
        echo "  restart  - Restart all components"
        echo "  status   - Show status of all components"
        echo "  logs     - Show available log files or tail specific component logs"
        echo ""
        echo "Examples:"
        echo "  $0 start"
        echo "  $0 logs sdn-controller"
        exit 1
        ;;
esac