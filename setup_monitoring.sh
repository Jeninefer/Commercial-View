#!/bin/bash

# Production Monitoring Setup Script
# Commercial-View Abaco Integration
# Spanish Factoring & Lending Analytics

set -e

echo "🚀 Setting up Production Monitoring for Commercial-View..."

# Configuration
API_PORT=${API_PORT:-8000}
PROMETHEUS_PORT=${PROMETHEUS_PORT:-9090}
GRAFANA_PORT=${GRAFANA_PORT:-3000}
SERVICE_NAME="commercial-view"

# Color coding for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root for system services
if [[ $EUID -eq 0 ]]; then
    print_warning "Running as root - system-wide monitoring setup"
    INSTALL_SYSTEM=true
else
    print_status "Running as user - local monitoring setup"
    INSTALL_SYSTEM=false
fi

# Install monitoring dependencies
print_status "Installing monitoring dependencies..."

# Install Python monitoring packages
pip install --upgrade prometheus-client prometheus-fastapi-instrumentator sentry-sdk[fastapi] structlog psutil

# Create monitoring configuration
print_status "Creating monitoring configuration..."

# Prometheus configuration
cat > prometheus.yml << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'commercial-view'
    static_configs:
      - targets: ['localhost:${API_PORT}']
    scrape_interval: 5s
    metrics_path: /metrics
    
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']
    scrape_interval: 10s

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - localhost:9093
EOF

# Alert rules for Abaco data processing
cat > alert_rules.yml << 'EOF'
groups:
  - name: commercial-view-alerts
    rules:
      - alert: HighRequestLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 0.5
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High request latency detected"
          description: "95th percentile latency is {{ $value }}s"

      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors per second"

      - alert: AbacoDataProcessingFailure
        expr: increase(http_requests_total{endpoint="/health", status!="200"}[5m]) > 3
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Abaco data processing health check failures"
          description: "Health check failed {{ $value }} times in 5 minutes"

      - alert: HighMemoryUsage
        expr: process_resident_memory_bytes / 1024 / 1024 > 1000
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
          description: "Memory usage is {{ $value }}MB"
EOF

# Grafana dashboard configuration
cat > grafana_dashboard.json << 'EOF'
{
  "dashboard": {
    "id": null,
    "title": "Commercial-View Abaco Analytics",
    "tags": ["commercial-view", "abaco", "factoring", "spanish"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Request Rate (Spanish Factoring API)",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ],
        "yAxes": [
          {
            "label": "requests/sec"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "title": "Response Time (95th percentile)",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ],
        "yAxes": [
          {
            "label": "seconds"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
      },
      {
        "id": 3,
        "title": "Abaco Portfolio Value ($208M USD)",
        "type": "stat",
        "targets": [
          {
            "expr": "208192588.65",
            "legendFormat": "Portfolio Value USD"
          }
        ],
        "gridPos": {"h": 4, "w": 6, "x": 0, "y": 8}
      },
      {
        "id": 4,
        "title": "Total Records (48,853)",
        "type": "stat",
        "targets": [
          {
            "expr": "48853",
            "legendFormat": "Total Records"
          }
        ],
        "gridPos": {"h": 4, "w": 6, "x": 6, "y": 8}
      },
      {
        "id": 5,
        "title": "System Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "process_resident_memory_bytes / 1024 / 1024",
            "legendFormat": "Memory MB"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 12}
      },
      {
        "id": 6,
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])",
            "legendFormat": "5xx errors/sec"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 12}
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "5s"
  }
}
EOF

# Create systemd service for Prometheus (if system install)
if [ "$INSTALL_SYSTEM" = true ]; then
    print_status "Creating Prometheus systemd service..."
    
    cat > /etc/systemd/system/prometheus.service << EOF
[Unit]
Description=Prometheus Server
Documentation=https://prometheus.io/docs/
After=network-online.target

[Service]
User=prometheus
Restart=on-failure
ExecStart=/usr/local/bin/prometheus \\
  --config.file=/etc/prometheus/prometheus.yml \\
  --storage.tsdb.path=/var/lib/prometheus/ \\
  --web.console.templates=/etc/prometheus/consoles \\
  --web.console.libraries=/etc/prometheus/console_libraries \\
  --web.listen-address=0.0.0.0:${PROMETHEUS_PORT}

[Install]
WantedBy=multi-user.target
EOF

    # Create prometheus user if it doesn't exist
    if ! id "prometheus" &>/dev/null; then
        useradd --no-create-home --shell /bin/false prometheus
    fi
    
    # Create directories
    mkdir -p /etc/prometheus /var/lib/prometheus
    chown prometheus:prometheus /var/lib/prometheus
    
    # Copy configuration
    cp prometheus.yml alert_rules.yml /etc/prometheus/
    chown prometheus:prometheus /etc/prometheus/*
    
    systemctl daemon-reload
    systemctl enable prometheus
    systemctl start prometheus
    
    print_success "Prometheus service installed and started on port ${PROMETHEUS_PORT}"
else
    print_status "Prometheus configuration saved to prometheus.yml"
    print_status "To run locally: prometheus --config.file=prometheus.yml --web.listen-address=:${PROMETHEUS_PORT}"
fi

# Create monitoring script
cat > monitor_commercial_view.py << 'EOF'
#!/usr/bin/env python3
"""
Commercial-View Production Monitoring Script
Real-time monitoring of Spanish Factoring & Lending Analytics
"""

import time
import requests
import json
import logging
from datetime import datetime
from typing import Dict, Any
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CommercialViewMonitor:
    def __init__(self, api_url="http://localhost:8000", check_interval=30):
        self.api_url = api_url.rstrip('/')
        self.check_interval = check_interval
        self.failed_checks = 0
        self.max_failures = 5
        
    def check_health(self) -> Dict[str, Any]:
        """Check API health endpoint"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            self.failed_checks += 1
            return {"status": "unhealthy", "error": str(e)}
    
    def check_performance(self) -> Dict[str, Any]:
        """Check performance metrics"""
        try:
            response = requests.get(f"{self.api_url}/performance", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning(f"Performance check failed: {e}")
            return {"error": str(e)}
    
    def check_abaco_data_integrity(self, health_data: Dict[str, Any]) -> bool:
        """Verify Abaco data integrity"""
        try:
            abaco_data = health_data.get("abaco_data", {})
            expected_total = 48853
            expected_value = 208192588.65
            
            total_records = abaco_data.get("total_records", 0)
            portfolio_value = abaco_data.get("portfolio_value_usd", 0)
            
            if total_records != expected_total:
                logger.error(f"Abaco record count mismatch: {total_records} != {expected_total}")
                return False
            
            if abs(portfolio_value - expected_value) > 1000:  # Allow $1K variance
                logger.error(f"Portfolio value mismatch: {portfolio_value} != {expected_value}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Data integrity check failed: {e}")
            return False
    
    def send_alert(self, message: str, severity="warning"):
        """Send alert (implement webhook/email integration here)"""
        alert_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "severity": severity,
            "message": message,
            "service": "commercial-view",
            "environment": "production"
        }
        
        # Log alert (extend this to send to alerting system)
        logger.critical(f"ALERT [{severity.upper()}]: {message}")
        
        # Example: Send to webhook (uncomment and configure)
        # try:
        #     requests.post("YOUR_WEBHOOK_URL", json=alert_data, timeout=5)
        # except Exception as e:
        #     logger.error(f"Failed to send alert: {e}")
    
    def run_monitoring_cycle(self):
        """Run one monitoring cycle"""
        logger.info("Starting monitoring cycle...")
        
        # Health check
        health_data = self.check_health()
        
        if health_data.get("status") == "healthy":
            logger.info("✅ Health check passed")
            self.failed_checks = 0
            
            # Verify Abaco data integrity
            if self.check_abaco_data_integrity(health_data):
                logger.info("✅ Abaco data integrity verified")
            else:
                self.send_alert("Abaco data integrity check failed", "critical")
            
        else:
            logger.error("❌ Health check failed")
            if self.failed_checks >= self.max_failures:
                self.send_alert(
                    f"Service unhealthy for {self.failed_checks} consecutive checks",
                    "critical"
                )
        
        # Performance check
        perf_data = self.check_performance()
        if "error" not in perf_data:
            system_metrics = perf_data.get("system", {})
            cpu_percent = system_metrics.get("cpu_percent", 0)
            memory_percent = system_metrics.get("memory_percent", 0)
            
            logger.info(f"📊 CPU: {cpu_percent}%, Memory: {memory_percent}%")
            
            # Alert on high resource usage
            if cpu_percent > 80:
                self.send_alert(f"High CPU usage: {cpu_percent}%", "warning")
            if memory_percent > 85:
                self.send_alert(f"High memory usage: {memory_percent}%", "warning")
        
        logger.info("Monitoring cycle completed")
    
    def run(self):
        """Run continuous monitoring"""
        logger.info(f"Starting Commercial-View monitoring (interval: {self.check_interval}s)")
        logger.info(f"Monitoring API at: {self.api_url}")
        
        try:
            while True:
                self.run_monitoring_cycle()
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
            self.send_alert(f"Monitoring system error: {e}", "critical")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Commercial-View Production Monitor")
    parser.add_argument("--api-url", default="http://localhost:8000", help="API URL to monitor")
    parser.add_argument("--interval", type=int, default=30, help="Check interval in seconds")
    
    args = parser.parse_args()
    
    monitor = CommercialViewMonitor(args.api_url, args.interval)
    monitor.run()
EOF

chmod +x monitor_commercial_view.py

# Create log rotation configuration
if [ "$INSTALL_SYSTEM" = true ]; then
    print_status "Setting up log rotation..."
    
    cat > /etc/logrotate.d/commercial-view << 'EOF'
/var/log/commercial-view/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 commercial-view commercial-view
    postrotate
        systemctl reload commercial-view
    endscript
}
EOF
fi

# Create startup script for monitoring
cat > start_monitoring.sh << 'EOF'
#!/bin/bash

# Start Commercial-View Production Monitoring
echo "🚀 Starting Commercial-View production monitoring..."

# Start API monitoring in background
python3 monitor_commercial_view.py --interval 30 &
MONITOR_PID=$!

echo "✅ Monitor started (PID: $MONITOR_PID)"
echo "📊 Monitoring Commercial-View API at http://localhost:8000"
echo "📈 Prometheus metrics at http://localhost:9090"
echo "📱 Grafana dashboard at http://localhost:3000"
echo ""
echo "Abaco Dataset: 48,853 records | $208M USD Portfolio"
echo "Spanish Factoring & Commercial Lending Analytics"
echo ""
echo "Press Ctrl+C to stop monitoring"

# Wait for interrupt
trap "echo '⏹️  Stopping monitor...'; kill $MONITOR_PID; exit 0" INT TERM

wait $MONITOR_PID
EOF

chmod +x start_monitoring.sh

# Summary
print_success "Monitoring setup completed!"
echo
echo "📊 Production Monitoring Configuration:"
echo "   • Prometheus config: prometheus.yml"
echo "   • Alert rules: alert_rules.yml" 
echo "   • Grafana dashboard: grafana_dashboard.json"
echo "   • Python monitor: monitor_commercial_view.py"
echo "   • Startup script: start_monitoring.sh"
echo
echo "🚀 To start monitoring:"
echo "   ./start_monitoring.sh"
echo
echo "📈 Metrics endpoints:"
echo "   • Health: http://localhost:${API_PORT}/health"
echo "   • Performance: http://localhost:${API_PORT}/performance"
echo "   • Prometheus: http://localhost:${PROMETHEUS_PORT}/metrics"
echo
echo "🔍 Abaco Data Monitoring:"
echo "   • Total Records: 48,853"
echo "   • Portfolio Value: $208,192,588.65 USD"
echo "   • Spanish Support: Enabled"
echo "   • Companies: Abaco Technologies, Abaco Financial"

print_success "Ready for production deployment with comprehensive monitoring! 🎯"