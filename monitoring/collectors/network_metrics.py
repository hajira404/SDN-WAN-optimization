import psutil
import time
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

# Create a registry for Prometheus metrics
registry = CollectorRegistry()

# Define metrics
cpu_usage_gauge = Gauge('cpu_usage', 'CPU Usage Percentage', registry=registry)
memory_usage_gauge = Gauge('memory_usage', 'Memory Usage Percentage', registry=registry)
disk_usage_gauge = Gauge('disk_usage', 'Disk Usage Percentage', registry=registry)

def collect_metrics():
    # Collect CPU usage
    cpu_usage = psutil.cpu_percent(interval=1)
    cpu_usage_gauge.set(cpu_usage)

    # Collect memory usage
    memory_usage = psutil.virtual_memory().percent
    memory_usage_gauge.set(memory_usage)

    # Collect disk usage
    disk_usage = psutil.disk_usage('/').percent
    disk_usage_gauge.set(disk_usage)

def main():
    while True:
        collect_metrics()
        # Push metrics to Prometheus Pushgateway
        push_to_gateway('localhost:9091', job='network_metrics', registry=registry)
        time.sleep(60)  # Collect metrics every 60 seconds

if __name__ == "__main__":
    main()