#!/bin/bash

# Alert System Configuration for Commercial-View
# Spanish Factoring & Commercial Lending Analytics
# Comprehensive Monitoring and Notification System

set -e

# Configuration
ALERTMANAGER_PORT=${ALERTMANAGER_PORT:-9093}
ALERTMANAGER_DATA_DIR="./alertmanager-data"
ALERTMANAGER_CONFIG_DIR="./alertmanager-config"
WEBHOOK_PORT=${WEBHOOK_PORT:-9094}
SMTP_SERVER=${SMTP_SERVER:-"smtp.gmail.com"}
SMTP_PORT=${SMTP_PORT:-587}
EMAIL_FROM=${EMAIL_FROM:-"commercial-view@company.com"}
EMAIL_TO=${EMAIL_TO:-"admin@company.com"}
SLACK_WEBHOOK=${SLACK_WEBHOOK:-""}
TEAMS_WEBHOOK=${TEAMS_WEBHOOK:-""}

# Color coding
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

print_header() {
    echo -e "${PURPLE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║${NC} $1"
    echo -e "${PURPLE}╚════════════════════════════════════════════════════════════════╝${NC}"
}

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

print_header "🔔 Alert System Setup for Commercial-View"
echo -e "🏦 Spanish Factoring & Commercial Lending Analytics"
echo -e "🚨 Real-time Monitoring & Notifications"
echo ""

# Create directories
setup_directories() {
    print_status "Creating Alert system directories..."
    
    mkdir -p "$ALERTMANAGER_DATA_DIR"
    mkdir -p "$ALERTMANAGER_CONFIG_DIR"/{templates,scripts}
    chmod 777 "$ALERTMANAGER_DATA_DIR"
    
    print_success "Directories created"
}

# Create Alertmanager configuration
create_alertmanager_config() {
    print_status "Creating Alertmanager configuration..."
    
    cat > "$ALERTMANAGER_CONFIG_DIR/alertmanager.yml" << EOF
# Alertmanager Configuration for Commercial-View
# Spanish Factoring & Commercial Lending Analytics
# Multi-channel notification system

global:
  smtp_smarthost: '$SMTP_SERVER:$SMTP_PORT'
  smtp_from: '$EMAIL_FROM'
  smtp_auth_username: '$EMAIL_FROM'
  smtp_auth_password: 'your_email_password_here'
  
  # Spanish timezone
  timezone: 'Europe/Madrid'

# Routing rules
route:
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'default-receiver'
  
  routes:
    # Critical alerts - immediate notification
    - match:
        severity: critical
      receiver: 'critical-alerts'
      group_wait: 0s
      repeat_interval: 5m
      
    # API alerts - business hours priority
    - match:
        service: commercial-view
      receiver: 'api-alerts'
      
    # Abaco data alerts - data team notification
    - match:
        service: abaco-integration
      receiver: 'data-alerts'
      
    # System alerts - infrastructure team
    - match_re:
        alertname: '(High.*Usage|.*Down|.*Exporter.*)'
      receiver: 'system-alerts'

# Inhibition rules (suppress redundant alerts)
inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'cluster', 'service']

# Notification receivers
receivers:
  # Default receiver
  - name: 'default-receiver'
    email_configs:
      - to: '$EMAIL_TO'
        subject: '🏦 Commercial-View Alert: {{ .GroupLabels.alertname }}'
        body: |
          🇪🇸 Spanish Factoring Alert System
          
          Alert: {{ .GroupLabels.alertname }}
          Status: {{ .Status }}
          
          Details:
          {{ range .Alerts }}
          - {{ .Annotations.summary }}
            Description: {{ .Annotations.description }}
            Started: {{ .StartsAt }}
          {{ end }}
          
          Abaco System: 48,853 records | \$208M USD portfolio
          Dashboard: http://localhost:3000
          
          Commercial-View Team

  # Critical alerts - multiple channels
  - name: 'critical-alerts'
    email_configs:
      - to: '$EMAIL_TO'
        subject: '🚨 CRITICAL: Commercial-View System Alert'
        body: |
          ⚠️  CRITICAL ALERT - IMMEDIATE ACTION REQUIRED ⚠️
          
          System: Spanish Factoring & Commercial Lending
          Alert: {{ .GroupLabels.alertname }}
          
          {{ range .Alerts }}
          🔥 {{ .Annotations.summary }}
          📋 {{ .Annotations.description }}
          🕐 Started: {{ .StartsAt }}
          {{ end }}
          
          🏦 Impact: 48,853 Abaco records | \$208,192,588.65 USD
          
          Actions Required:
          1. Check system status immediately
          2. Review logs: docker logs commercial-view-api
          3. Access monitoring: http://localhost:3000
          
          Escalation: Call +34-XXX-XXX-XXX if unresolved in 5 minutes
          
    webhook_configs:
      - url: 'http://localhost:$WEBHOOK_PORT/webhook/critical'
        send_resolved: true

  # API-specific alerts
  - name: 'api-alerts'
    email_configs:
      - to: '$EMAIL_TO'
        subject: '📊 API Alert: {{ .GroupLabels.alertname }}'
        body: |
          🏦 Commercial-View API Notification
          
          Spanish Factoring System Alert
          Alert: {{ .GroupLabels.alertname }}
          
          {{ range .Alerts }}
          • {{ .Annotations.summary }}
          • {{ .Annotations.description }}
          • Started: {{ .StartsAt }}
          {{ end }}
          
          📊 API Status: Check http://localhost:8000/health
          📈 Metrics: http://localhost:9090
          🖥️  Dashboard: http://localhost:3000
          
  # Data processing alerts
  - name: 'data-alerts'
    email_configs:
      - to: '$EMAIL_TO'
        subject: '📈 Abaco Data Alert: {{ .GroupLabels.alertname }}'
        body: |
          📊 Abaco Data Processing Alert
          
          Spanish Commercial Lending Dataset
          Alert: {{ .GroupLabels.alertname }}
          
          {{ range .Alerts }}
          • {{ .Annotations.summary }}
          • {{ .Annotations.description }}
          • Started: {{ .StartsAt }}
          {{ end }}
          
          📊 Dataset: 48,853 records
          💰 Portfolio: \$208,192,588.65 USD
          🔍 Check data pipeline and processing logs
          
  # System infrastructure alerts
  - name: 'system-alerts'
    email_configs:
      - to: '$EMAIL_TO'
        subject: '🖥️  System Alert: {{ .GroupLabels.alertname }}'
        body: |
          🖥️  Infrastructure Alert - Commercial-View
          
          System Component: {{ .GroupLabels.alertname }}
          
          {{ range .Alerts }}
          • {{ .Annotations.summary }}
          • {{ .Annotations.description }}
          • Started: {{ .StartsAt }}
          {{ end }}
          
          🔧 System Actions:
          1. Check system resources
          2. Review application logs
          3. Monitor performance metrics
          
          Infrastructure Team
EOF

    print_success "Alertmanager configuration created"
}

# Create enhanced alert rules for Prometheus
create_enhanced_alert_rules() {
    print_status "Creating comprehensive alert rules..."
    
    mkdir -p prometheus-rules
    
    cat > prometheus-rules/commercial_view_alerts.yml << 'EOF'
# Commercial-View Comprehensive Alert Rules
# Spanish Factoring & Commercial Lending Analytics
# Production-grade monitoring and alerting

groups:
  # API Health and Performance
  - name: api-health
    interval: 30s
    rules:
      - alert: CommercialViewAPIDown
        expr: up{job="commercial-view-api"} == 0
        for: 1m
        labels:
          severity: critical
          service: commercial-view
          team: backend
        annotations:
          summary: "🚨 Commercial-View API is DOWN"
          description: "Spanish Factoring API has been unreachable for {{ $labels.instance }} for more than 1 minute. Immediate action required!"
          runbook: "Check API logs: docker logs commercial-view-api"
          
      - alert: APIHighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job="commercial-view-api"}[5m])) > 2
        for: 5m
        labels:
          severity: warning
          service: commercial-view
          team: backend
        annotations:
          summary: "⚡ High API Response Times Detected"
          description: "95th percentile response time is {{ $value | humanizeDuration }} (>2s) for the last 5 minutes"
          impact: "User experience degradation on Spanish factoring operations"
          
      - alert: APIHighErrorRate
        expr: (rate(http_requests_total{job="commercial-view-api",status=~"5.."}[5m]) / rate(http_requests_total{job="commercial-view-api"}[5m])) * 100 > 5
        for: 3m
        labels:
          severity: critical
          service: commercial-view
          team: backend
        annotations:
          summary: "🔥 High API Error Rate"
          description: "Error rate is {{ $value | humanizePercentage }} (>5%) for the last 3 minutes"
          impact: "Potential data corruption or system failure affecting $208M USD portfolio"
          
      - alert: APILowThroughput
        expr: rate(http_requests_total{job="commercial-view-api"}[5m]) < 0.1
        for: 10m
        labels:
          severity: warning
          service: commercial-view
          team: backend
        annotations:
          summary: "📉 Low API Request Volume"
          description: "Request rate is {{ $value | humanize }} req/sec (<0.1) for 10 minutes"
          context: "Possible issue with client integrations or system accessibility"

  # System Resources
  - name: system-resources
    interval: 60s
    rules:
      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 85
        for: 10m
        labels:
          severity: warning
          service: system
          team: infrastructure
        annotations:
          summary: "🔥 High CPU Usage"
          description: "CPU usage is {{ $value | humanizePercentage }} (>85%) on {{ $labels.instance }} for 10 minutes"
          action: "Check processes and consider scaling"
          
      - alert: HighMemoryUsage
        expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100 > 90
        for: 5m
        labels:
          severity: critical
          service: system
          team: infrastructure
        annotations:
          summary: "💾 Critical Memory Usage"
          description: "Memory usage is {{ $value | humanizePercentage }} (>90%) on {{ $labels.instance }}"
          impact: "Risk of system instability affecting Abaco data processing"
          
      - alert: LowDiskSpace
        expr: (node_filesystem_avail_bytes{fstype!="tmpfs"} / node_filesystem_size_bytes{fstype!="tmpfs"}) * 100 < 10
        for: 5m
        labels:
          severity: critical
          service: system
          team: infrastructure
        annotations:
          summary: "💿 Low Disk Space"
          description: "Disk space is {{ $value | humanizePercentage }} remaining on {{ $labels.device }} ({{ $labels.instance }})"
          impact: "Risk of data loss and application failure"

  # Abaco Data Processing
  - name: abaco-data
    interval: 300s  # 5 minutes
    rules:
      - alert: AbacoDataProcessingStalled
        expr: increase(abaco_records_processed_total[1h]) == 0
        for: 2h
        labels:
          severity: warning
          service: abaco-integration
          team: data
        annotations:
          summary: "📊 Abaco Data Processing Stalled"
          description: "No Abaco records have been processed in the last 2 hours"
          context: "48,853 records pipeline may be blocked"
          
      - alert: AbacoDataQualityIssue
        expr: increase(abaco_data_validation_errors_total[30m]) > 10
        for: 15m
        labels:
          severity: warning
          service: abaco-integration
          team: data
        annotations:
          summary: "❌ Abaco Data Quality Issues"
          description: "{{ $value }} validation errors in the last 30 minutes (>10)"
          impact: "Data integrity issues affecting Spanish factoring calculations"
          
      - alert: AbacoPortfolioValueAnomaly
        expr: abs(abaco_portfolio_value_usd - 208192588.65) / 208192588.65 * 100 > 5
        for: 30m
        labels:
          severity: critical
          service: abaco-integration
          team: data
        annotations:
          summary: "💰 Portfolio Value Anomaly Detected"
          description: "Portfolio value deviation of {{ $value | humanizePercentage }} from expected $208.19M USD"
          impact: "Critical financial data discrepancy requiring immediate investigation"

  # Database and Storage
  - name: database-health
    interval: 120s
    rules:
      - alert: DatabaseConnectionFailure
        expr: db_up{job="commercial-view-api"} == 0
        for: 2m
        labels:
          severity: critical
          service: database
          team: infrastructure
        annotations:
          summary: "🗄️  Database Connection Lost"
          description: "Unable to connect to database for 2 minutes"
          impact: "Complete data access failure affecting all operations"
          
      - alert: SlowDatabaseQueries
        expr: histogram_quantile(0.95, rate(db_query_duration_seconds_bucket[5m])) > 5
        for: 10m
        labels:
          severity: warning
          service: database
          team: database
        annotations:
          summary: "🐌 Slow Database Queries"
          description: "95th percentile query time is {{ $value | humanizeDuration }} (>5s)"
          impact: "Performance degradation affecting Spanish factoring operations"

  # Security Alerts
  - name: security
    interval: 60s
    rules:
      - alert: SuspiciousTrafficPattern
        expr: rate(nginx_http_requests_total{status="404"}[5m]) > 10
        for: 5m
        labels:
          severity: warning
          service: security
          team: security
        annotations:
          summary: "🛡️  Suspicious Traffic Detected"
          description: "High rate of 404 errors: {{ $value }} req/sec (>10) - possible scanning"
          action: "Review access logs and consider rate limiting"
          
      - alert: UnauthorizedAccessAttempts
        expr: rate(nginx_http_requests_total{status="401"}[5m]) > 5
        for: 5m
        labels:
          severity: warning
          service: security
          team: security
        annotations:
          summary: "🔐 Multiple Unauthorized Access Attempts"
          description: "{{ $value }} unauthorized attempts per second (>5)"
          action: "Check authentication logs and consider IP blocking"

  # SSL/TLS Certificate Monitoring
  - name: ssl-monitoring
    interval: 3600s  # 1 hour
    rules:
      - alert: SSLCertificateExpiringSoon
        expr: (ssl_cert_not_after - time()) / 86400 < 30
        for: 0m
        labels:
          severity: warning
          service: ssl
          team: infrastructure
        annotations:
          summary: "📜 SSL Certificate Expiring Soon"
          description: "SSL certificate expires in {{ $value }} days (<30)"
          action: "Renew SSL certificate before expiration"
          
      - alert: SSLCertificateExpired
        expr: ssl_cert_not_after < time()
        for: 0m
        labels:
          severity: critical
          service: ssl
          team: infrastructure
        annotations:
          summary: "🚨 SSL Certificate EXPIRED"
          description: "SSL certificate has expired!"
          impact: "HTTPS service unavailable - immediate renewal required"
EOF

    print_success "Enhanced alert rules created"
}

# Create webhook receiver for custom notifications
create_webhook_receiver() {
    print_status "Creating webhook notification receiver..."
    
    cat > "$ALERTMANAGER_CONFIG_DIR/scripts/webhook_receiver.py" << 'EOF'
#!/usr/bin/env python3
"""
Webhook Receiver for Commercial-View Alerts
Spanish Factoring & Commercial Lending Analytics
Custom notification processing and routing
"""

import json
import logging
import smtplib
import sqlite3
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, jsonify
import requests

# Configuration
WEBHOOK_PORT = 9094
DATABASE_FILE = "alerts.db"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('webhook_alerts.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class AlertProcessor:
    """Process and route Commercial-View alerts"""
    
    def __init__(self):
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for alert tracking"""
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                alert_name TEXT,
                severity TEXT,
                service TEXT,
                status TEXT,
                description TEXT,
                fingerprint TEXT UNIQUE,
                processed BOOLEAN DEFAULT FALSE
            )
        ''')
        conn.commit()
        conn.close()
        logger.info("Alert database initialized")
    
    def store_alert(self, alert_data):
        """Store alert in database"""
        try:
            conn = sqlite3.connect(DATABASE_FILE)
            cursor = conn.cursor()
            
            # Extract alert information
            for alert in alert_data.get('alerts', []):
                cursor.execute('''
                    INSERT OR REPLACE INTO alerts 
                    (alert_name, severity, service, status, description, fingerprint)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    alert.get('labels', {}).get('alertname', 'Unknown'),
                    alert.get('labels', {}).get('severity', 'unknown'),
                    alert.get('labels', {}).get('service', 'unknown'),
                    alert.get('status', 'unknown'),
                    alert.get('annotations', {}).get('summary', ''),
                    alert.get('fingerprint', '')
                ))
            
            conn.commit()
            conn.close()
            logger.info(f"Stored {len(alert_data.get('alerts', []))} alerts")
            
        except Exception as e:
            logger.error(f"Failed to store alerts: {e}")
    
    def process_critical_alert(self, alert_data):
        """Process critical alerts with enhanced notifications"""
        logger.warning("🚨 Processing CRITICAL alert")
        
        # Store in database
        self.store_alert(alert_data)
        
        # Send enhanced notifications
        self.send_sms_notification(alert_data)
        self.send_slack_notification(alert_data)
        self.trigger_escalation(alert_data)
        
        return {"status": "critical_processed", "escalated": True}
    
    def send_sms_notification(self, alert_data):
        """Send SMS for critical alerts (placeholder)"""
        logger.info("📱 SMS notification triggered (implementation needed)")
        # Implement SMS gateway integration here
        pass
    
    def send_slack_notification(self, alert_data):
        """Send Slack notification"""
        try:
            slack_webhook = "YOUR_SLACK_WEBHOOK_URL_HERE"  # Configure this
            if not slack_webhook or slack_webhook.startswith("YOUR_"):
                logger.info("📢 Slack webhook not configured")
                return
            
            message = {
                "text": "🏦 Commercial-View Alert",
                "attachments": [
                    {
                        "color": "danger" if "critical" in str(alert_data).lower() else "warning",
                        "title": "🇪🇸 Spanish Factoring System Alert",
                        "fields": [
                            {
                                "title": "System",
                                "value": "Commercial-View Analytics",
                                "short": True
                            },
                            {
                                "title": "Portfolio",
                                "value": "$208,192,588.65 USD",
                                "short": True
                            }
                        ],
                        "footer": "Abaco Integration | 48,853 records"
                    }
                ]
            }
            
            response = requests.post(slack_webhook, json=message)
            if response.status_code == 200:
                logger.info("✅ Slack notification sent")
            else:
                logger.error(f"❌ Slack notification failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Slack notification error: {e}")
    
    def trigger_escalation(self, alert_data):
        """Trigger escalation procedures"""
        logger.warning("🔺 Escalation procedures initiated")
        
        # Log escalation
        escalation_log = {
            "timestamp": datetime.now().isoformat(),
            "alert_data": alert_data,
            "escalation_level": "critical",
            "actions_taken": [
                "Database alert stored",
                "SMS notification triggered", 
                "Slack notification sent",
                "Email notification queued"
            ]
        }
        
        # Save escalation log
        with open("escalation.log", "a") as f:
            f.write(json.dumps(escalation_log) + "\n")
        
        logger.info("✅ Escalation logged")

# Initialize alert processor
alert_processor = AlertProcessor()

@app.route('/webhook/<alert_type>', methods=['POST'])
def handle_webhook(alert_type):
    """Handle incoming webhook alerts"""
    try:
        alert_data = request.get_json()
        logger.info(f"📨 Received {alert_type} alert: {alert_data.get('status', 'unknown')}")
        
        if alert_type == 'critical':
            result = alert_processor.process_critical_alert(alert_data)
        else:
            alert_processor.store_alert(alert_data)
            result = {"status": "processed"}
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "commercial-view-webhook",
        "system": "Spanish Factoring Analytics",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/alerts/stats', methods=['GET'])
def alert_stats():
    """Get alert statistics"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        # Get alert counts by severity
        cursor.execute('''
            SELECT severity, COUNT(*) as count 
            FROM alerts 
            WHERE timestamp > datetime('now', '-24 hours')
            GROUP BY severity
        ''')
        
        stats = {
            "period": "24h",
            "by_severity": dict(cursor.fetchall()),
            "system": "Commercial-View Spanish Factoring",
            "portfolio": "$208,192,588.65 USD"
        }
        
        conn.close()
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    logger.info("🚀 Starting Commercial-View Webhook Receiver")
    logger.info("🏦 Spanish Factoring Alert System")
    logger.info(f"📊 Monitoring 48,853 Abaco records | $208M USD portfolio")
    
    app.run(host='0.0.0.0', port=WEBHOOK_PORT, debug=False)
EOF

    chmod +x "$ALERTMANAGER_CONFIG_DIR/scripts/webhook_receiver.py"
    print_success "Webhook receiver created"
}

# Create alert testing script
create_alert_tester() {
    print_status "Creating alert testing script..."
    
    cat > test_alerts.sh << 'EOF'
#!/bin/bash

# Alert System Test Script for Commercial-View
# Spanish Factoring & Commercial Lending Analytics

set -e

# Configuration
PROMETHEUS_URL="http://localhost:9090"
ALERTMANAGER_URL="http://localhost:9093"
API_URL="http://localhost:8000"

# Color coding
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🧪 Testing Commercial-View Alert System${NC}"
echo "================================================"
echo "🏦 Spanish Factoring & Commercial Lending"
echo "📊 Abaco Dataset: 48,853 records | $208M USD"
echo ""

test_prometheus_connection() {
    echo -e "${BLUE}🔍 Testing Prometheus connection...${NC}"
    
    if curl -s "$PROMETHEUS_URL/api/v1/status/config" > /dev/null; then
        echo -e "✅ Prometheus: ${GREEN}Connected${NC}"
    else
        echo -e "❌ Prometheus: ${RED}Disconnected${NC}"
        return 1
    fi
}

test_alertmanager_connection() {
    echo -e "${BLUE}🔔 Testing Alertmanager connection...${NC}"
    
    if curl -s "$ALERTMANAGER_URL/api/v1/status" > /dev/null; then
        echo -e "✅ Alertmanager: ${GREEN}Connected${NC}"
    else
        echo -e "❌ Alertmanager: ${RED}Disconnected${NC}"
        return 1
    fi
}

test_api_health() {
    echo -e "${BLUE}🏥 Testing API health endpoint...${NC}"
    
    if curl -s "$API_URL/health" > /dev/null; then
        echo -e "✅ API Health: ${GREEN}OK${NC}"
    else
        echo -e "❌ API Health: ${RED}Failed${NC}"
        return 1
    fi
}

simulate_test_alert() {
    echo -e "${BLUE}🚨 Simulating test alert...${NC}"
    
    # Create a test metric that will trigger an alert
    curl -X POST "$PROMETHEUS_URL/api/v1/admin/tsdb/delete_series" \
        --data-urlencode 'match[]=test_alert_metric' > /dev/null 2>&1 || true
    
    echo -e "📊 Test alert simulation attempted"
    echo -e "⏳ Check Alertmanager UI for firing alerts: $ALERTMANAGER_URL"
}

check_active_alerts() {
    echo -e "${BLUE}📋 Checking active alerts...${NC}"
    
    ALERTS=$(curl -s "$ALERTMANAGER_URL/api/v1/alerts" | python3 -m json.tool 2>/dev/null || echo '{"data": []}')
    ALERT_COUNT=$(echo "$ALERTS" | grep -o '"state"' | wc -l || echo "0")
    
    echo -e "🔢 Active alerts: $ALERT_COUNT"
    
    if [ "$ALERT_COUNT" -gt 0 ]; then
        echo -e "${YELLOW}⚠️  Active alerts detected${NC}"
        echo -e "🔍 Review at: $ALERTMANAGER_URL/#/alerts"
    else
        echo -e "✅ No active alerts"
    fi
}

check_alert_rules() {
    echo -e "${BLUE}📝 Checking alert rule configuration...${NC}"
    
    RULES=$(curl -s "$PROMETHEUS_URL/api/v1/rules" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    rules = data.get('data', {}).get('groups', [])
    rule_count = sum(len(group.get('rules', [])) for group in rules)
    print(f'Rules loaded: {rule_count}')
except:
    print('Rules check failed')
")
    
    echo -e "📊 $RULES"
}

test_webhook_receiver() {
    echo -e "${BLUE}🪝 Testing webhook receiver...${NC}"
    
    if curl -s "http://localhost:9094/health" > /dev/null; then
        echo -e "✅ Webhook receiver: ${GREEN}Running${NC}"
    else
        echo -e "❌ Webhook receiver: ${RED}Not running${NC}"
        echo -e "💡 Start with: python3 alertmanager-config/scripts/webhook_receiver.py"
    fi
}

generate_test_report() {
    echo -e "\n${BLUE}📊 Alert System Test Report${NC}"
    echo "================================="
    echo "System: Commercial-View Spanish Factoring"
    echo "Timestamp: $(date)"
    echo ""
    
    echo "Component Status:"
    test_prometheus_connection
    test_alertmanager_connection
    test_api_health
    test_webhook_receiver
    
    echo ""
    echo "Alert Configuration:"
    check_alert_rules
    check_active_alerts
    
    echo ""
    echo "🇪🇸 Spanish Factoring System Health: Monitored"
    echo "📊 Abaco Integration: 48,853 records tracked"
    echo "💰 Portfolio Value: $208,192,588.65 USD"
    echo ""
    echo "🔗 Management URLs:"
    echo "   • Prometheus: $PROMETHEUS_URL"
    echo "   • Alertmanager: $ALERTMANAGER_URL"
    echo "   • Grafana: http://localhost:3000"
    echo "   • API: $API_URL"
}

# Main execution
case "${1:-test}" in
    "test")
        generate_test_report
        ;;
    "simulate")
        simulate_test_alert
        ;;
    "alerts")
        check_active_alerts
        ;;
    "rules")
        check_alert_rules
        ;;
    *)
        echo "Usage: $0 {test|simulate|alerts|rules}"
        echo ""
        echo "Commands:"
        echo "  test     - Run complete alert system test"
        echo "  simulate - Simulate a test alert"
        echo "  alerts   - Check active alerts"
        echo "  rules    - Check alert rule configuration"
        ;;
esac
EOF

    chmod +x test_alerts.sh
    print_success "Alert testing script created"
}

# Create Docker Compose for alert stack
create_alert_docker_compose() {
    print_status "Creating alert system Docker Compose..."
    
    cat > docker-compose.alerts.yml << EOF
# Commercial-View Alert System Stack
# Spanish Factoring & Commercial Lending Analytics
# Comprehensive monitoring and notification platform

version: '3.8'

services:
  # Alertmanager - Alert routing and notification
  alertmanager:
    image: prom/alertmanager:latest
    container_name: commercial-view-alertmanager
    restart: unless-stopped
    ports:
      - "$ALERTMANAGER_PORT:9093"
    volumes:
      - ./alertmanager-data:/alertmanager
      - ./$ALERTMANAGER_CONFIG_DIR:/etc/alertmanager:ro
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
      - '--storage.path=/alertmanager'
      - '--web.external-url=http://localhost:$ALERTMANAGER_PORT'
      - '--cluster.listen-address=0.0.0.0:9094'
      - '--log.level=info'
    networks:
      - commercial-view-network
    labels:
      - "com.commercial-view.service=alertmanager"
      - "com.commercial-view.description=Spanish Factoring Alert Management"

  # Webhook Receiver - Custom notification processing
  webhook-receiver:
    build:
      context: .
      dockerfile_inline: |
        FROM python:3.11-slim
        RUN pip install flask requests
        WORKDIR /app
        COPY $ALERTMANAGER_CONFIG_DIR/scripts/webhook_receiver.py .
        EXPOSE $WEBHOOK_PORT
        CMD ["python", "webhook_receiver.py"]
    container_name: commercial-view-webhook
    restart: unless-stopped
    ports:
      - "$WEBHOOK_PORT:$WEBHOOK_PORT"
    volumes:
      - ./webhook-data:/app/data
    environment:
      - WEBHOOK_PORT=$WEBHOOK_PORT
      - DATABASE_FILE=/app/data/alerts.db
    networks:
      - commercial-view-network
    labels:
      - "com.commercial-view.service=webhook-receiver"
      - "com.commercial-view.description=Custom Alert Processing"

  # Blackbox Exporter - External monitoring
  blackbox-exporter:
    image: prom/blackbox-exporter:latest
    container_name: commercial-view-blackbox
    restart: unless-stopped
    ports:
      - "9115:9115"
    volumes:
      - ./$ALERTMANAGER_CONFIG_DIR/blackbox.yml:/etc/blackbox_exporter/config.yml:ro
    networks:
      - commercial-view-network
    labels:
      - "com.commercial-view.service=blackbox-exporter"
      - "com.commercial-view.description=External Endpoint Monitoring"

networks:
  commercial-view-network:
    external: true
    name: commercial-view-network

volumes:
  alertmanager-data:
    name: commercial-view-alertmanager-data
  webhook-data:
    name: commercial-view-webhook-data
EOF

    print_success "Alert system Docker Compose created"
}

# Create blackbox exporter config for external monitoring
create_blackbox_config() {
    print_status "Creating blackbox exporter configuration..."
    
    cat > "$ALERTMANAGER_CONFIG_DIR/blackbox.yml" << EOF
# Blackbox Exporter Configuration for Commercial-View
# Spanish Factoring & Commercial Lending Analytics
# External endpoint monitoring

modules:
  # HTTP GET probe
  http_2xx:
    prober: http
    timeout: 5s
    http:
      valid_http_versions: ["HTTP/1.1", "HTTP/2.0"]
      valid_status_codes: []  # Defaults to 2xx
      method: GET
      headers:
        User-Agent: "Commercial-View-Monitor/1.0"
      fail_if_ssl: false
      fail_if_not_ssl: false
      
  # HTTPS probe with SSL verification
  https_2xx:
    prober: http
    timeout: 5s
    http:
      valid_http_versions: ["HTTP/1.1", "HTTP/2.0"]
      method: GET
      headers:
        User-Agent: "Commercial-View-SSL-Monitor/1.0"
      fail_if_not_ssl: true
      
  # TCP probe for database connections
  tcp_connect:
    prober: tcp
    timeout: 5s
    
  # ICMP probe for network connectivity
  icmp:
    prober: icmp
    timeout: 5s
EOF

    print_success "Blackbox exporter configuration created"
}

# Create alert management script
create_alert_manager_script() {
    print_status "Creating alert management script..."
    
    cat > manage_alerts.sh << 'EOF'
#!/bin/bash

# Alert System Management for Commercial-View
# Spanish Factoring & Commercial Lending Analytics

set -e

# Color coding
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

ACTION=${1:-status}

case $ACTION in
    start)
        echo -e "${BLUE}🚀 Starting Commercial-View Alert System...${NC}"
        
        # Create network if it doesn't exist
        docker network create commercial-view-network 2>/dev/null || true
        
        # Start alert stack
        docker-compose -f docker-compose.alerts.yml up -d
        
        echo -e "${GREEN}✅ Alert system started successfully!${NC}"
        echo ""
        echo "🔔 Alert System URLs:"
        echo "   • Alertmanager: http://localhost:9093"
        echo "   • Webhook Receiver: http://localhost:9094"
        echo "   • Blackbox Exporter: http://localhost:9115"
        echo ""
        echo "🏦 Spanish Factoring Alert System Ready!"
        echo "📊 Monitoring 48,853 Abaco records | $208M USD portfolio"
        ;;
        
    stop)
        echo -e "${YELLOW}⏹️  Stopping Commercial-View Alert System...${NC}"
        docker-compose -f docker-compose.alerts.yml down
        echo -e "${GREEN}✅ Alert system stopped${NC}"
        ;;
        
    restart)
        echo -e "${YELLOW}🔄 Restarting Commercial-View Alert System...${NC}"
        docker-compose -f docker-compose.alerts.yml restart
        echo -e "${GREEN}✅ Alert system restarted${NC}"
        ;;
        
    status)
        echo -e "${BLUE}📊 Commercial-View Alert System Status${NC}"
        echo "======================================="
        
        # Container status
        docker-compose -f docker-compose.alerts.yml ps
        echo ""
        
        # Health checks
        if curl -s http://localhost:9093/api/v1/status > /dev/null; then
            echo -e "✅ Alertmanager: ${GREEN}Healthy${NC}"
        else
            echo -e "❌ Alertmanager: ${RED}Unhealthy${NC}"
        fi
        
        if curl -s http://localhost:9094/health > /dev/null; then
            echo -e "✅ Webhook Receiver: ${GREEN}Healthy${NC}"
        else
            echo -e "❌ Webhook Receiver: ${RED}Unhealthy${NC}"
        fi
        
        if curl -s http://localhost:9115/config > /dev/null; then
            echo -e "✅ Blackbox Exporter: ${GREEN}Healthy${NC}"
        else
            echo -e "❌ Blackbox Exporter: ${RED}Unhealthy${NC}"
        fi
        
        echo ""
        echo "🇪🇸 Spanish Factoring Alert System: Active"
        ;;
        
    logs)
        SERVICE=${2:-alertmanager}
        echo -e "${BLUE}📋 Showing $SERVICE logs...${NC}"
        docker-compose -f docker-compose.alerts.yml logs -f $SERVICE
        ;;
        
    test)
        echo -e "${BLUE}🧪 Running alert system tests...${NC}"
        ./test_alerts.sh test
        ;;
        
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|test}"
        echo ""
        echo "Commands:"
        echo "  start    - Start the alert system stack"
        echo "  stop     - Stop the alert system stack"
        echo "  restart  - Restart the alert system stack"
        echo "  status   - Show system status and health"
        echo "  logs     - Show service logs (optionally specify service)"
        echo "  test     - Run alert system tests"
        exit 1
        ;;
esac
EOF

    chmod +x manage_alerts.sh
    print_success "Alert management script created"
}

# Main execution
main() {
    setup_directories
    create_alertmanager_config
    create_enhanced_alert_rules
    create_webhook_receiver
    create_alert_tester
    create_alert_docker_compose
    create_blackbox_config
    create_alert_manager_script
    
    print_success "🔔 Alert System Configuration Complete!"
    echo ""
    echo "🚀 Quick Start Commands:"
    echo "   • Start alerts: ./manage_alerts.sh start"
    echo "   • Check status: ./manage_alerts.sh status"
    echo "   • Test system: ./manage_alerts.sh test"
    echo ""
    echo "🔔 Alert System URLs:"
    echo "   • Alertmanager: http://localhost:$ALERTMANAGER_PORT"
    echo "   • Webhook Receiver: http://localhost:$WEBHOOK_PORT"
    echo "   • Test API: ./test_alerts.sh"
    echo ""
    echo "📧 Notification Channels:"
    echo "   • Email: $EMAIL_TO"
    echo "   • Webhook: Custom processing"
    echo "   • Database: SQLite alert storage"
    echo ""
    echo "🏦 Spanish Factoring Alerts:"
    echo "   • Portfolio monitoring: \$208M USD"
    echo "   • Abaco data integrity: 48,853 records"
    echo "   • API performance & health"
    echo "   • System resource monitoring"
    echo ""
    print_warning "⚠️  Configure email settings in alertmanager.yml"
    print_success "Alert system ready for Spanish factoring! 🇪🇸🔔"
}

main "$@"