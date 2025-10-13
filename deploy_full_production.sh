#!/bin/bash

# Complete Production Deployment and Testing Suite
# Commercial-View Abaco Integration
# Spanish Factoring & Commercial Lending Analytics - 48,853 Records | $208M USD

set -e

# Configuration
PROJECT_NAME="commercial-view"
API_PORT=${API_PORT:-8000}
SERVICE_USER=${SERVICE_USER:-$USER}
PYTHON_VERSION="3.13"
ENVIRONMENT="production"

# Color coding
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
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

# Main deployment header
print_header "🏦 Commercial-View Production Deployment Suite"
echo -e "🇪🇸 Spanish Factoring & Commercial Lending Analytics"
echo -e "📊 Abaco Dataset: 48,853 records | Portfolio: \$208,192,588.65 USD"
echo -e "🚀 Environment: ${ENVIRONMENT} | Python: ${PYTHON_VERSION}"
echo ""

# Step 1: Pre-deployment validation
print_header "Step 1: Pre-deployment Validation"

print_status "Checking system requirements..."

# Python version check
if command -v python3 >/dev/null 2>&1; then
    PYTHON_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    if [ "$PYTHON_VER" = "$PYTHON_VERSION" ]; then
        print_success "Python $PYTHON_VER detected ✓"
    else
        print_warning "Python $PYTHON_VER detected (expected $PYTHON_VERSION)"
    fi
else
    print_error "Python 3 not found. Please install Python $PYTHON_VERSION"
    exit 1
fi

# Check if port is available
if lsof -Pi :$API_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    print_warning "Port $API_PORT is already in use"
    EXISTING_PID=$(lsof -Pi :$API_PORT -sTCP:LISTEN -t)
    print_status "Existing process PID: $EXISTING_PID"
    
    read -p "Stop existing service? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kill $EXISTING_PID
        sleep 2
        print_success "Stopped existing service"
    else
        print_error "Cannot continue with port $API_PORT in use"
        exit 1
    fi
else
    print_success "Port $API_PORT is available ✓"
fi

# Disk space check
AVAILABLE_GB=$(df . | tail -1 | awk '{print int($4/1024/1024)}')
if [ $AVAILABLE_GB -lt 2 ]; then
    print_error "Insufficient disk space: ${AVAILABLE_GB}GB available (need 2GB+)"
    exit 1
else
    print_success "Disk space: ${AVAILABLE_GB}GB available ✓"
fi

print_success "Pre-deployment validation completed"

# Step 2: Environment setup
print_header "Step 2: Environment Setup"

print_status "Setting up Python virtual environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Created virtual environment"
else
    print_status "Using existing virtual environment"
fi

# Activate virtual environment
source venv/bin/activate
print_success "Activated virtual environment"

# Upgrade pip
pip install --upgrade pip > /dev/null 2>&1
print_success "Updated pip"

# Install production dependencies
print_status "Installing production dependencies..."

pip install --upgrade \
    fastapi==0.104.1 \
    "uvicorn[standard]==0.24.0" \
    pandas==2.1.3 \
    numpy==1.25.2 \
    python-dotenv==1.0.0 \
    prometheus-client==0.19.0 \
    prometheus-fastapi-instrumentator==6.1.0 \
    "sentry-sdk[fastapi]==1.38.0" \
    structlog==23.2.0 \
    psutil==5.9.6 \
    aiohttp==3.9.1 \
    > /dev/null 2>&1

print_success "Production dependencies installed"

# Step 3: Configuration
print_header "Step 3: Production Configuration"

print_status "Creating production environment configuration..."

# Create production environment file
cat > .env.production << 'EOF'
# Commercial-View Abaco Production Configuration
# Spanish Factoring & Commercial Lending Analytics

# Environment
ENVIRONMENT=production
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO

# Abaco Dataset Configuration
ABACO_RECORDS_TOTAL=48853
ABACO_LOAN_RECORDS=16205
ABACO_PAYMENT_RECORDS=16443
ABACO_SCHEDULE_RECORDS=16205
ABACO_PORTFOLIO_VALUE=208192588.65
ABACO_CURRENCY=USD
ABACO_COMPANY_1=Abaco Technologies
ABACO_COMPANY_2=Abaco Financial

# Spanish Support
SPANISH_SUPPORT=true
SPANISH_ACCURACY_TARGET=99.97
BULLET_PAYMENTS_ENABLED=true

# Monitoring
PROMETHEUS_ENABLED=true
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id

# Security (Generate new values for production)
SECRET_KEY=your-super-secret-key-change-in-production
API_KEY=your-api-key-change-in-production

# Performance
UVICORN_WORKERS=4
UVICORN_MAX_REQUESTS=1000
UVICORN_MAX_REQUESTS_JITTER=100
EOF

# Set secure permissions
chmod 600 .env.production
print_success "Created secure production configuration"

# Replace main.py with enhanced version
if [ -f "main_enhanced.py" ]; then
    cp main_enhanced.py main.py
    print_success "Updated main application with monitoring support"
else
    print_warning "Enhanced main.py not found - using existing main.py"
fi

# Step 4: Service setup (if running as root or with sudo)
print_header "Step 4: Service Configuration"

if [ "$EUID" -eq 0 ] || command -v sudo >/dev/null 2>&1; then
    print_status "Creating systemd service..."
    
    SERVICE_FILE="/etc/systemd/system/${PROJECT_NAME}.service"
    
    # Create service file
    sudo tee $SERVICE_FILE > /dev/null << EOF
[Unit]
Description=Commercial-View Abaco Integration API
Documentation=https://github.com/Jeninefer/Commercial-View
After=network.target

[Service]
Type=exec
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
EnvironmentFile=$(pwd)/.env.production
ExecStart=$(pwd)/venv/bin/uvicorn main:app \\
    --host \${API_HOST} \\
    --port \${API_PORT} \\
    --workers \${UVICORN_WORKERS} \\
    --max-requests \${UVICORN_MAX_REQUESTS} \\
    --max-requests-jitter \${UVICORN_MAX_REQUESTS_JITTER}
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=3
KillMode=mixed
TimeoutStopSec=10

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=$(pwd)

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=commercial-view

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable $PROJECT_NAME
    print_success "Created and enabled systemd service"
else
    print_warning "Cannot create systemd service (no sudo access)"
    print_status "Service will be managed manually"
fi

# Step 5: Start application
print_header "Step 5: Application Startup"

print_status "Starting Commercial-View API..."

# Start the application
if [ "$EUID" -eq 0 ] || command -v sudo >/dev/null 2>&1; then
    sudo systemctl start $PROJECT_NAME
    sleep 3
    
    if sudo systemctl is-active --quiet $PROJECT_NAME; then
        print_success "Service started successfully via systemd"
    else
        print_error "Service failed to start via systemd"
        sudo systemctl status $PROJECT_NAME
        exit 1
    fi
else
    # Manual startup
    source .env.production
    export $(cat .env.production | grep -v '^#' | xargs)
    
    nohup uvicorn main:app \
        --host ${API_HOST:-0.0.0.0} \
        --port ${API_PORT:-8000} \
        --workers ${UVICORN_WORKERS:-4} \
        > logs/api.log 2>&1 &
    
    API_PID=$!
    echo $API_PID > api.pid
    
    sleep 3
    
    if kill -0 $API_PID 2>/dev/null; then
        print_success "Service started successfully (PID: $API_PID)"
    else
        print_error "Service failed to start manually"
        exit 1
    fi
fi

# Step 6: Health validation
print_header "Step 6: Health Validation"

print_status "Waiting for service to be ready..."
sleep 5

# Health check
print_status "Performing health check..."
for i in {1..10}; do
    if curl -s "http://localhost:${API_PORT}/health" > /dev/null 2>&1; then
        HEALTH_RESPONSE=$(curl -s "http://localhost:${API_PORT}/health")
        print_success "Health check passed ✓"
        
        # Validate Abaco data in response
        if echo "$HEALTH_RESPONSE" | grep -q "48853"; then
            print_success "Abaco record count validated ✓"
        else
            print_warning "Abaco record count not found in health response"
        fi
        
        if echo "$HEALTH_RESPONSE" | grep -q "208192588.65"; then
            print_success "Portfolio value validated ✓"
        else
            print_warning "Portfolio value not found in health response"
        fi
        
        break
    else
        print_status "Attempt $i/10: Waiting for service..."
        sleep 2
    fi
    
    if [ $i -eq 10 ]; then
        print_error "Health check failed after 10 attempts"
        exit 1
    fi
done

# Step 7: Performance testing
print_header "Step 7: Performance Testing"

if [ -f "performance_test.py" ]; then
    print_status "Running performance tests..."
    
    python3 performance_test.py \
        --base-url "http://localhost:${API_PORT}" \
        --users 5 \
        --requests 20 \
        --duration 30 \
        --ramp-up 5 \
        --output "performance_results.json"
    
    if [ $? -eq 0 ]; then
        print_success "Performance tests passed ✓"
    else
        print_warning "Performance tests completed with warnings"
    fi
else
    print_warning "Performance test script not found - skipping"
fi

# Step 8: Monitoring setup
print_header "Step 8: Monitoring Setup"

if [ -f "setup_monitoring.sh" ]; then
    print_status "Setting up monitoring..."
    bash setup_monitoring.sh
    print_success "Monitoring configured"
else
    print_warning "Monitoring setup script not found"
fi

# Step 9: Final validation and summary
print_header "Step 9: Deployment Summary"

print_success "🎉 Commercial-View Production Deployment Completed!"
echo ""
echo "📊 Service Information:"
echo "   • API URL: http://localhost:${API_PORT}"
echo "   • Health Check: http://localhost:${API_PORT}/health"
echo "   • Performance Metrics: http://localhost:${API_PORT}/performance"
echo "   • Documentation: http://localhost:${API_PORT}/docs"
echo ""
echo "🏦 Abaco Integration:"
echo "   • Total Records: 48,853"
echo "   • Portfolio Value: \$208,192,588.65 USD"
echo "   • Companies: Abaco Technologies, Abaco Financial"
echo "   • Spanish Support: Enabled"
echo ""
echo "🔧 Management Commands:"
if [ "$EUID" -eq 0 ] || command -v sudo >/dev/null 2>&1; then
    echo "   • Status: sudo systemctl status ${PROJECT_NAME}"
    echo "   • Logs: sudo journalctl -u ${PROJECT_NAME} -f"
    echo "   • Restart: sudo systemctl restart ${PROJECT_NAME}"
    echo "   • Stop: sudo systemctl stop ${PROJECT_NAME}"
else
    echo "   • Status: kill -0 \$(cat api.pid)"
    echo "   • Logs: tail -f logs/api.log"
    echo "   • Stop: kill \$(cat api.pid)"
fi
echo ""
echo "📈 Monitoring:"
if [ -f "start_monitoring.sh" ]; then
    echo "   • Start monitoring: ./start_monitoring.sh"
fi
if [ -f "performance_test.py" ]; then
    echo "   • Performance test: python3 performance_test.py"
fi
echo ""
echo "🚀 Next Steps:"
echo "   1. Configure production secrets in .env.production"
echo "   2. Set up SSL/TLS certificates for HTTPS"
echo "   3. Configure reverse proxy (nginx/Apache)"
echo "   4. Set up log aggregation (ELK stack)"
echo "   5. Configure alerting webhooks"
echo ""
print_success "Production deployment ready for Spanish factoring operations! 🇪🇸💼"