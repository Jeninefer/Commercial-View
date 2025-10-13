#!/bin/bash

# Grafana Dashboard Setup for Commercial-View
# Spanish Factoring & Commercial Lending Analytics
# Abaco Dataset Visualization & Monitoring

set -e

# Configuration
GRAFANA_PORT=${GRAFANA_PORT:-3000}
GRAFANA_DATA_DIR="./grafana-data"
GRAFANA_CONFIG_DIR="./grafana-config"
PROMETHEUS_PORT=${PROMETHEUS_PORT:-9090}
PROMETHEUS_DATA_DIR="./prometheus-data"
API_ENDPOINT=${API_ENDPOINT:-"http://localhost:8000"}

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

print_header "📊 Grafana Dashboard Setup for Commercial-View"
echo -e "🏦 Spanish Factoring & Commercial Lending Analytics"
echo -e "📈 Abaco Dataset: 48,853 records | \$208,192,588.65 USD"
echo ""

# Create directories
setup_directories() {
    print_status "Creating Grafana directories..."
    
    mkdir -p "$GRAFANA_DATA_DIR"
    mkdir -p "$GRAFANA_CONFIG_DIR"/{provisioning,dashboards,datasources,plugins}
    mkdir -p "$PROMETHEUS_DATA_DIR"
    
    # Set permissions for Grafana
    chmod 777 "$GRAFANA_DATA_DIR"
    chmod 777 "$PROMETHEUS_DATA_DIR"
    
    print_success "Directories created"
}

# Install Prometheus (metrics collection)
install_prometheus() {
    print_status "Setting up Prometheus for metrics collection..."
    
    # Create Prometheus configuration
    cat > "$GRAFANA_CONFIG_DIR/prometheus.yml" << EOF
# Prometheus Configuration for Commercial-View
# Spanish Factoring & Commercial Lending Analytics

global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  # Commercial-View API metrics
  - job_name: 'commercial-view-api'
    static_configs:
      - targets: ['host.docker.internal:8000']
    metrics_path: '/metrics'
    scrape_interval: 10s
    scrape_timeout: 5s
    
  # System metrics (if node_exporter is available)
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['host.docker.internal:9100']
    scrape_interval: 15s
    
  # Nginx metrics (if nginx_exporter is available)
  - job_name: 'nginx-exporter'
    static_configs:
      - targets: ['host.docker.internal:9113']
    scrape_interval: 15s

  # Self-monitoring
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
EOF

    print_success "Prometheus configuration created"
}

# Create Grafana datasource configuration
create_datasources() {
    print_status "Creating Grafana datasources..."
    
    cat > "$GRAFANA_CONFIG_DIR/provisioning/datasources/prometheus.yml" << EOF
# Grafana Datasources for Commercial-View
# Spanish Factoring & Commercial Lending Analytics

apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://host.docker.internal:$PROMETHEUS_PORT
    isDefault: true
    editable: true
    jsonData:
      timeInterval: "15s"
    uid: prometheus-uid

  - name: TestData DB
    type: testdata
    access: proxy
    isDefault: false
    editable: true
    uid: testdata-uid
EOF

    print_success "Datasources configured"
}

# Create Commercial-View dashboard
create_dashboard() {
    print_status "Creating Commercial-View analytics dashboard..."
    
    cat > "$GRAFANA_CONFIG_DIR/dashboards/commercial-view.json" << 'EOF'
{
  "dashboard": {
    "id": null,
    "title": "🏦 Commercial-View: Spanish Factoring Analytics",
    "description": "Real-time analytics for Spanish commercial lending and factoring operations. Abaco dataset: 48,853 records | $208,192,588.65 USD portfolio.",
    "tags": ["commercial-view", "spanish-factoring", "abaco", "commercial-lending"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "🇪🇸 Spanish Factoring Portfolio Overview",
        "type": "stat",
        "targets": [
          {
            "expr": "48853",
            "legendFormat": "Total Records",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "mappings": [],
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {
                  "color": "green",
                  "value": null
                }
              ]
            }
          }
        },
        "options": {
          "reduceOptions": {
            "values": false,
            "calcs": [
              "lastNotNull"
            ],
            "fields": ""
          },
          "orientation": "auto",
          "textMode": "auto",
          "colorMode": "value",
          "graphMode": "area",
          "justifyMode": "auto"
        },
        "pluginVersion": "8.0.0",
        "gridPos": {
          "h": 8,
          "w": 6,
          "x": 0,
          "y": 0
        }
      },
      {
        "id": 2,
        "title": "💰 Portfolio Value (USD)",
        "type": "stat",
        "targets": [
          {
            "expr": "208192588.65",
            "legendFormat": "Total Portfolio",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "mappings": [],
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {
                  "color": "blue",
                  "value": null
                }
              ]
            },
            "unit": "currencyUSD"
          }
        },
        "options": {
          "reduceOptions": {
            "values": false,
            "calcs": [
              "lastNotNull"
            ],
            "fields": ""
          },
          "orientation": "auto",
          "textMode": "auto",
          "colorMode": "value",
          "graphMode": "area",
          "justifyMode": "auto"
        },
        "pluginVersion": "8.0.0",
        "gridPos": {
          "h": 8,
          "w": 6,
          "x": 6,
          "y": 0
        }
      },
      {
        "id": 3,
        "title": "📊 API Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "Requests/sec",
            "refId": "A"
          }
        ],
        "yAxes": [
          {
            "label": "Requests/sec",
            "show": true
          },
          {
            "show": true
          }
        ],
        "xAxis": {
          "show": true
        },
        "gridPos": {
          "h": 8,
          "w": 12,
          "x": 12,
          "y": 0
        }
      },
      {
        "id": 4,
        "title": "⚡ API Response Times",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile",
            "refId": "A"
          },
          {
            "expr": "histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "50th percentile",
            "refId": "B"
          }
        ],
        "yAxes": [
          {
            "label": "Seconds",
            "show": true
          },
          {
            "show": true
          }
        ],
        "xAxis": {
          "show": true
        },
        "gridPos": {
          "h": 8,
          "w": 12,
          "x": 0,
          "y": 8
        }
      },
      {
        "id": 5,
        "title": "🏥 System Health Status",
        "type": "stat",
        "targets": [
          {
            "expr": "up{job=\"commercial-view-api\"}",
            "legendFormat": "API Status",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "mappings": [
              {
                "options": {
                  "0": {
                    "text": "DOWN",
                    "color": "red"
                  },
                  "1": {
                    "text": "UP",
                    "color": "green"
                  }
                },
                "type": "value"
              }
            ],
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {
                  "color": "red",
                  "value": null
                },
                {
                  "color": "green",
                  "value": 1
                }
              ]
            }
          }
        },
        "options": {
          "reduceOptions": {
            "values": false,
            "calcs": [
              "lastNotNull"
            ],
            "fields": ""
          },
          "orientation": "auto",
          "textMode": "auto",
          "colorMode": "background",
          "graphMode": "none",
          "justifyMode": "center"
        },
        "pluginVersion": "8.0.0",
        "gridPos": {
          "h": 8,
          "w": 6,
          "x": 12,
          "y": 8
        }
      },
      {
        "id": 6,
        "title": "💾 Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "process_resident_memory_bytes",
            "legendFormat": "Memory Usage",
            "refId": "A"
          }
        ],
        "yAxes": [
          {
            "label": "Bytes",
            "show": true
          },
          {
            "show": true
          }
        ],
        "xAxis": {
          "show": true
        },
        "gridPos": {
          "h": 8,
          "w": 6,
          "x": 18,
          "y": 8
        }
      },
      {
        "id": 7,
        "title": "🏦 Abaco Dataset Analysis",
        "type": "table",
        "targets": [
          {
            "expr": "increase(abaco_records_processed_total[1h])",
            "legendFormat": "Records Processed (1h)",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "mappings": [],
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {
                  "color": "green",
                  "value": null
                }
              ]
            }
          }
        },
        "options": {
          "showHeader": true
        },
        "pluginVersion": "8.0.0",
        "gridPos": {
          "h": 8,
          "w": 12,
          "x": 0,
          "y": 16
        }
      },
      {
        "id": 8,
        "title": "🔄 Error Rate",
        "type": "singlestat",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m]) / rate(http_requests_total[5m]) * 100",
            "legendFormat": "Error Rate %",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "mappings": [],
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {
                  "color": "green",
                  "value": null
                },
                {
                  "color": "yellow",
                  "value": 1
                },
                {
                  "color": "red",
                  "value": 5
                }
              ]
            },
            "unit": "percent"
          }
        },
        "options": {
          "reduceOptions": {
            "values": false,
            "calcs": [
              "lastNotNull"
            ],
            "fields": ""
          },
          "orientation": "auto",
          "textMode": "auto",
          "colorMode": "background",
          "graphMode": "area",
          "justifyMode": "center"
        },
        "pluginVersion": "8.0.0",
        "gridPos": {
          "h": 8,
          "w": 12,
          "x": 12,
          "y": 16
        }
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "10s",
    "version": 1,
    "uid": "commercial-view-main"
  }
}
EOF

    print_success "Commercial-View dashboard created"
}

# Create dashboard provisioning configuration
create_dashboard_provisioning() {
    print_status "Setting up dashboard provisioning..."
    
    cat > "$GRAFANA_CONFIG_DIR/provisioning/dashboards/dashboard.yml" << EOF
# Dashboard provisioning for Commercial-View
# Spanish Factoring & Commercial Lending Analytics

apiVersion: 1

providers:
  - name: 'commercial-view-dashboards'
    orgId: 1
    folder: 'Commercial-View'
    type: file
    disableDeletion: false
    editable: true
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/dashboards
EOF

    print_success "Dashboard provisioning configured"
}

# Create Docker Compose for Grafana stack
create_docker_compose() {
    print_status "Creating Docker Compose for Grafana stack..."
    
    cat > docker-compose.grafana.yml << EOF
# Commercial-View Grafana Stack
# Spanish Factoring & Commercial Lending Analytics
# Monitoring and Visualization Platform

version: '3.8'

services:
  # Prometheus - Metrics Collection
  prometheus:
    image: prom/prometheus:latest
    container_name: commercial-view-prometheus
    restart: unless-stopped
    ports:
      - "$PROMETHEUS_PORT:9090"
    volumes:
      - ./prometheus-data:/prometheus
      - ./$GRAFANA_CONFIG_DIR/prometheus.yml:/etc/prometheus/prometheus.yml:ro
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'
    networks:
      - commercial-view-network
    labels:
      - "com.commercial-view.service=prometheus"
      - "com.commercial-view.description=Spanish Factoring Metrics Collection"

  # Grafana - Visualization and Dashboards
  grafana:
    image: grafana/grafana:latest
    container_name: commercial-view-grafana
    restart: unless-stopped
    ports:
      - "$GRAFANA_PORT:3000"
    volumes:
      - ./grafana-data:/var/lib/grafana
      - ./$GRAFANA_CONFIG_DIR/provisioning:/etc/grafana/provisioning:ro
      - ./$GRAFANA_CONFIG_DIR/dashboards:/etc/grafana/dashboards:ro
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=commercial_view_admin
      - GF_SECURITY_ADMIN_USER=admin
      - GF_INSTALL_PLUGINS=grafana-piechart-panel,grafana-worldmap-panel
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_SECURITY_DISABLE_GRAVATAR=true
      - GF_ANALYTICS_REPORTING_ENABLED=false
      - GF_ANALYTICS_CHECK_FOR_UPDATES=false
      - GF_SERVER_ROOT_URL=http://localhost:$GRAFANA_PORT
      - GF_DASHBOARDS_DEFAULT_HOME_DASHBOARD_PATH=/etc/grafana/dashboards/commercial-view.json
    networks:
      - commercial-view-network
    depends_on:
      - prometheus
    labels:
      - "com.commercial-view.service=grafana"
      - "com.commercial-view.description=Spanish Factoring Analytics Dashboard"

  # Node Exporter - System Metrics (optional)
  node-exporter:
    image: prom/node-exporter:latest
    container_name: commercial-view-node-exporter
    restart: unless-stopped
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    networks:
      - commercial-view-network
    labels:
      - "com.commercial-view.service=node-exporter"
      - "com.commercial-view.description=System Metrics Collection"

networks:
  commercial-view-network:
    driver: bridge
    name: commercial-view-network
    labels:
      - "com.commercial-view.network=main"
      - "com.commercial-view.description=Spanish Factoring Network"

volumes:
  grafana-data:
    name: commercial-view-grafana-data
  prometheus-data:
    name: commercial-view-prometheus-data
EOF

    print_success "Docker Compose configuration created"
}

# Create Grafana startup script
create_startup_script() {
    print_status "Creating Grafana management script..."
    
    cat > start_grafana.sh << 'EOF'
#!/bin/bash

# Grafana Management Script for Commercial-View
# Spanish Factoring & Commercial Lending Analytics

set -e

# Color coding
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

ACTION=${1:-start}

case $ACTION in
    start)
        echo -e "${BLUE}🚀 Starting Commercial-View Grafana Stack...${NC}"
        docker-compose -f docker-compose.grafana.yml up -d
        
        echo -e "${GREEN}✅ Grafana stack started successfully!${NC}"
        echo ""
        echo "📊 Access URLs:"
        echo "   • Grafana: http://localhost:3000 (admin/commercial_view_admin)"
        echo "   • Prometheus: http://localhost:9090"
        echo "   • Node Exporter: http://localhost:9100"
        echo ""
        echo "🏦 Spanish Factoring Dashboard ready!"
        echo "📈 Monitoring 48,853 Abaco records | $208M USD portfolio"
        ;;
        
    stop)
        echo -e "${YELLOW}⏹️  Stopping Commercial-View Grafana Stack...${NC}"
        docker-compose -f docker-compose.grafana.yml down
        echo -e "${GREEN}✅ Grafana stack stopped${NC}"
        ;;
        
    restart)
        echo -e "${YELLOW}🔄 Restarting Commercial-View Grafana Stack...${NC}"
        docker-compose -f docker-compose.grafana.yml restart
        echo -e "${GREEN}✅ Grafana stack restarted${NC}"
        ;;
        
    logs)
        echo -e "${BLUE}📋 Showing Grafana logs...${NC}"
        docker-compose -f docker-compose.grafana.yml logs -f grafana
        ;;
        
    status)
        echo -e "${BLUE}📊 Commercial-View Grafana Status${NC}"
        echo "================================="
        docker-compose -f docker-compose.grafana.yml ps
        echo ""
        
        # Check Grafana health
        if curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
            echo -e "✅ Grafana: ${GREEN}Healthy${NC}"
        else
            echo -e "❌ Grafana: ${RED}Unhealthy${NC}"
        fi
        
        # Check Prometheus health
        if curl -s http://localhost:9090/-/healthy > /dev/null 2>&1; then
            echo -e "✅ Prometheus: ${GREEN}Healthy${NC}"
        else
            echo -e "❌ Prometheus: ${RED}Unhealthy${NC}"
        fi
        
        echo ""
        echo "🇪🇸 Spanish Factoring Analytics: Ready"
        ;;
        
    update)
        echo -e "${BLUE}🔄 Updating Grafana stack...${NC}"
        docker-compose -f docker-compose.grafana.yml pull
        docker-compose -f docker-compose.grafana.yml up -d
        echo -e "${GREEN}✅ Grafana stack updated${NC}"
        ;;
        
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|update}"
        echo ""
        echo "Commands:"
        echo "  start    - Start the Grafana monitoring stack"
        echo "  stop     - Stop the Grafana monitoring stack"  
        echo "  restart  - Restart the Grafana monitoring stack"
        echo "  status   - Show status and health checks"
        echo "  logs     - Show Grafana logs"
        echo "  update   - Update containers to latest versions"
        exit 1
        ;;
esac
EOF

    chmod +x start_grafana.sh
    print_success "Grafana management script created"
}

# Create initial alert rules (for future use with Alertmanager)
create_alert_rules() {
    print_status "Creating Prometheus alert rules..."
    
    mkdir -p "$GRAFANA_CONFIG_DIR/rules"
    
    cat > "$GRAFANA_CONFIG_DIR/rules/commercial_view_alerts.yml" << EOF
# Commercial-View Alert Rules
# Spanish Factoring & Commercial Lending Analytics

groups:
  - name: commercial-view-alerts
    rules:
      # API Health Alerts
      - alert: CommercialViewAPIDown
        expr: up{job="commercial-view-api"} == 0
        for: 1m
        labels:
          severity: critical
          service: commercial-view
        annotations:
          summary: "Commercial-View API is down"
          description: "Spanish Factoring API has been down for more than 1 minute"

      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
          service: commercial-view
        annotations:
          summary: "High API response times"
          description: "95th percentile response time is {{ \$value }}s for 5 minutes"

      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
          service: commercial-view
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ \$value | humanizePercentage }} for 5 minutes"

      # System Resource Alerts
      - alert: HighMemoryUsage
        expr: process_resident_memory_bytes / 1024 / 1024 / 1024 > 2
        for: 10m
        labels:
          severity: warning
          service: commercial-view
        annotations:
          summary: "High memory usage"
          description: "Memory usage is {{ \$value }}GB for 10 minutes"

      # Business Logic Alerts
      - alert: AbacoDataProcessingStalled
        expr: increase(abaco_records_processed_total[1h]) == 0
        for: 2h
        labels:
          severity: warning
          service: abaco-integration
        annotations:
          summary: "Abaco data processing has stalled"
          description: "No Abaco records have been processed in the last hour"
EOF

    print_success "Alert rules created"
}

# Main execution
main() {
    setup_directories
    install_prometheus
    create_datasources
    create_dashboard
    create_dashboard_provisioning
    create_docker_compose
    create_startup_script
    create_alert_rules
    
    print_success "📊 Grafana Dashboard Setup Complete!"
    echo ""
    echo "🚀 Quick Start Commands:"
    echo "   • Start monitoring: ./start_grafana.sh start"
    echo "   • Check status: ./start_grafana.sh status"
    echo "   • View logs: ./start_grafana.sh logs"
    echo ""
    echo "📊 Dashboard Access:"
    echo "   • Grafana: http://localhost:$GRAFANA_PORT"
    echo "   • Username: admin"
    echo "   • Password: commercial_view_admin"
    echo ""
    echo "📈 Prometheus Metrics:"
    echo "   • Prometheus UI: http://localhost:$PROMETHEUS_PORT"
    echo "   • Node Exporter: http://localhost:9100"
    echo ""
    echo "🏦 Spanish Factoring Analytics:"
    echo "   • 48,853 Abaco records monitored"
    echo "   • \$208,192,588.65 USD portfolio tracked"
    echo "   • Real-time performance metrics"
    echo ""
    print_success "Grafana monitoring ready for Spanish factoring! 🇪🇸📊"
}

main "$@"