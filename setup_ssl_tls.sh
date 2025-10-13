#!/bin/bash

# SSL/TLS Certificate Setup for Commercial-View
# Spanish Factoring & Commercial Lending Analytics
# Production HTTPS Configuration

set -e

# Configuration
DOMAIN=${DOMAIN:-"commercial-view.local"}
PROJECT_NAME="commercial-view"
SSL_DIR="/etc/ssl/commercial-view"
CERT_DIR="/etc/letsencrypt/live"
API_PORT=${API_PORT:-8000}
HTTPS_PORT=${HTTPS_PORT:-8443}

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

print_header "🔒 SSL/TLS Configuration for Commercial-View"
echo -e "🏦 Spanish Factoring & Commercial Lending Analytics"
echo -e "📊 Domain: ${DOMAIN} | HTTPS Port: ${HTTPS_PORT}"
echo ""

# Check if running with appropriate privileges
if [[ $EUID -ne 0 ]]; then
    print_warning "Not running as root. Some SSL operations may require sudo."
    USE_SUDO="sudo"
else
    USE_SUDO=""
fi

# Option 1: Self-signed certificates for development/testing
create_self_signed_cert() {
    print_status "Creating self-signed SSL certificates..."
    
    # Create SSL directory
    $USE_SUDO mkdir -p "$SSL_DIR"
    
    # Generate private key
    $USE_SUDO openssl genrsa -out "$SSL_DIR/private.key" 2048
    
    # Create certificate signing request config
    cat > /tmp/cert_config << EOF
[req]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn
req_extensions = v3_req

[dn]
C=US
ST=CA
L=San Francisco
O=Commercial View
OU=Spanish Factoring Division
CN=${DOMAIN}

[v3_req]
subjectAltName = @alt_names
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth

[alt_names]
DNS.1 = ${DOMAIN}
DNS.2 = localhost
DNS.3 = *.${DOMAIN}
IP.1 = 127.0.0.1
IP.2 = ::1
EOF

    # Generate certificate
    $USE_SUDO openssl req -new -x509 -key "$SSL_DIR/private.key" \
        -out "$SSL_DIR/certificate.crt" \
        -days 365 \
        -config /tmp/cert_config \
        -extensions v3_req
    
    # Set proper permissions
    $USE_SUDO chmod 600 "$SSL_DIR/private.key"
    $USE_SUDO chmod 644 "$SSL_DIR/certificate.crt"
    
    # Clean up
    rm /tmp/cert_config
    
    print_success "Self-signed certificate created at $SSL_DIR"
}

# Option 2: Let's Encrypt certificates for production
setup_letsencrypt() {
    print_status "Setting up Let's Encrypt SSL certificates..."
    
    # Check if certbot is installed
    if ! command -v certbot &> /dev/null; then
        print_status "Installing certbot..."
        
        # Install certbot based on OS
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            if command -v brew &> /dev/null; then
                brew install certbot
            else
                print_error "Please install Homebrew first or install certbot manually"
                return 1
            fi
        elif [[ -f /etc/debian_version ]]; then
            # Debian/Ubuntu
            $USE_SUDO apt-get update
            $USE_SUDO apt-get install -y certbot python3-certbot-nginx
        elif [[ -f /etc/redhat-release ]]; then
            # RHEL/CentOS
            $USE_SUDO yum install -y certbot python3-certbot-nginx
        else
            print_error "Unsupported OS for automatic certbot installation"
            return 1
        fi
    fi
    
    # Generate certificate (requires domain to point to this server)
    print_status "Requesting SSL certificate for domain: $DOMAIN"
    print_warning "Note: Domain $DOMAIN must point to this server's public IP"
    
    read -p "Continue with Let's Encrypt certificate? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        $USE_SUDO certbot certonly --standalone \
            --preferred-challenges http \
            --email admin@${DOMAIN} \
            --agree-tos \
            --no-eff-email \
            -d $DOMAIN
        
        if [ $? -eq 0 ]; then
            print_success "Let's Encrypt certificate obtained successfully"
            
            # Create symlinks for easier access
            $USE_SUDO mkdir -p "$SSL_DIR"
            $USE_SUDO ln -sf "$CERT_DIR/$DOMAIN/fullchain.pem" "$SSL_DIR/certificate.crt"
            $USE_SUDO ln -sf "$CERT_DIR/$DOMAIN/privkey.pem" "$SSL_DIR/private.key"
            
            # Set up auto-renewal
            setup_cert_renewal
        else
            print_error "Failed to obtain Let's Encrypt certificate"
            return 1
        fi
    else
        print_status "Skipping Let's Encrypt setup"
        return 1
    fi
}

# Set up certificate auto-renewal
setup_cert_renewal() {
    print_status "Setting up certificate auto-renewal..."
    
    # Create renewal script
    cat > /tmp/renew_certs.sh << 'EOF'
#!/bin/bash
# SSL Certificate Renewal Script
# Commercial-View Spanish Factoring System

certbot renew --quiet --no-self-upgrade

# Restart services if certificates were renewed
if [ $? -eq 0 ]; then
    systemctl reload nginx 2>/dev/null || true
    systemctl restart commercial-view 2>/dev/null || true
fi
EOF

    $USE_SUDO cp /tmp/renew_certs.sh /usr/local/bin/renew_commercial_view_certs.sh
    $USE_SUDO chmod +x /usr/local/bin/renew_commercial_view_certs.sh
    
    # Add to crontab for monthly renewal
    (crontab -l 2>/dev/null || echo "") | grep -v "renew_commercial_view_certs" | \
    { cat; echo "0 3 1 * * /usr/local/bin/renew_commercial_view_certs.sh"; } | crontab -
    
    print_success "Certificate auto-renewal configured"
}

# Create HTTPS-enabled FastAPI configuration
create_https_config() {
    print_status "Creating HTTPS configuration..."
    
    # Create HTTPS startup script
    cat > start_https_api.sh << EOF
#!/bin/bash
# HTTPS API Startup Script for Commercial-View
# Spanish Factoring & Commercial Lending Analytics

set -e

echo "🔒 Starting Commercial-View HTTPS API..."
echo "🏦 Abaco Dataset: 48,853 records | Portfolio: \\$208,192,588.65 USD"
echo "🇪🇸 Spanish Factoring with SSL/TLS Security"

# Load environment variables
if [ -f .env.production ]; then
    source .env.production
fi

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

# SSL certificate paths
SSL_CERT="$SSL_DIR/certificate.crt"
SSL_KEY="$SSL_DIR/private.key"

# Verify SSL files exist
if [ ! -f "\$SSL_CERT" ] || [ ! -f "\$SSL_KEY" ]; then
    echo "❌ SSL certificates not found!"
    echo "   Expected: \$SSL_CERT and \$SSL_KEY"
    exit 1
fi

echo "✅ SSL certificates found"
echo "🚀 Starting HTTPS server on port $HTTPS_PORT..."

# Start HTTPS server with SSL
uvicorn main:app \\
    --host 0.0.0.0 \\
    --port $HTTPS_PORT \\
    --ssl-keyfile="\$SSL_KEY" \\
    --ssl-certfile="\$SSL_CERT" \\
    --workers \${UVICORN_WORKERS:-4} \\
    --access-log \\
    --loop uvloop \\
    --http httptools

EOF

    chmod +x start_https_api.sh
    print_success "HTTPS startup script created: start_https_api.sh"
}

# Create systemd service for HTTPS
create_https_service() {
    if command -v systemctl &> /dev/null; then
        print_status "Creating HTTPS systemd service..."
        
        cat > /tmp/commercial-view-https.service << EOF
[Unit]
Description=Commercial-View HTTPS API (Spanish Factoring)
Documentation=https://github.com/Jeninefer/Commercial-View
After=network.target
Requires=network.target

[Service]
Type=exec
User=$(whoami)
Group=$(whoami)
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin:$(pwd)/.venv/bin
EnvironmentFile=$(pwd)/.env.production
ExecStart=$(pwd)/venv/bin/uvicorn main:app \\
    --host 0.0.0.0 \\
    --port $HTTPS_PORT \\
    --ssl-keyfile=$SSL_DIR/private.key \\
    --ssl-certfile=$SSL_DIR/certificate.crt \\
    --workers \${UVICORN_WORKERS:-4} \\
    --access-log
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
AmbientCapabilities=CAP_NET_BIND_SERVICE

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
EOF

        $USE_SUDO cp /tmp/commercial-view-https.service /etc/systemd/system/
        $USE_SUDO systemctl daemon-reload
        $USE_SUDO systemctl enable commercial-view-https
        
        print_success "HTTPS systemd service created"
    fi
}

# Main execution
main() {
    echo "Choose SSL certificate option:"
    echo "1) Self-signed certificate (Development/Testing)"
    echo "2) Let's Encrypt certificate (Production)"
    echo "3) Use existing certificates"
    read -p "Enter choice (1-3): " choice

    case $choice in
        1)
            create_self_signed_cert
            ;;
        2)
            setup_letsencrypt || create_self_signed_cert
            ;;
        3)
            if [ ! -f "$SSL_DIR/certificate.crt" ] || [ ! -f "$SSL_DIR/private.key" ]; then
                print_error "Existing certificates not found at $SSL_DIR"
                print_status "Falling back to self-signed certificates"
                create_self_signed_cert
            else
                print_success "Using existing certificates at $SSL_DIR"
            fi
            ;;
        *)
            print_error "Invalid choice. Creating self-signed certificates"
            create_self_signed_cert
            ;;
    esac

    # Create HTTPS configuration
    create_https_config
    create_https_service

    # Update environment file with HTTPS settings
    if [ -f .env.production ]; then
        # Add HTTPS settings to environment
        echo "" >> .env.production
        echo "# HTTPS Configuration" >> .env.production
        echo "HTTPS_ENABLED=true" >> .env.production
        echo "HTTPS_PORT=$HTTPS_PORT" >> .env.production
        echo "SSL_CERT_PATH=$SSL_DIR/certificate.crt" >> .env.production
        echo "SSL_KEY_PATH=$SSL_DIR/private.key" >> .env.production
    fi

    print_success "🔒 SSL/TLS Configuration Complete!"
    echo ""
    echo "📊 HTTPS Configuration:"
    echo "   • HTTPS URL: https://$DOMAIN:$HTTPS_PORT"
    echo "   • SSL Certificates: $SSL_DIR/"
    echo "   • Startup Script: ./start_https_api.sh"
    echo ""
    echo "🏦 Abaco Integration (Secure):"
    echo "   • Health Check: https://$DOMAIN:$HTTPS_PORT/health"
    echo "   • Performance: https://$DOMAIN:$HTTPS_PORT/performance"
    echo "   • Metrics: https://$DOMAIN:$HTTPS_PORT/metrics"
    echo ""
    echo "🚀 To start HTTPS server:"
    echo "   ./start_https_api.sh"
    echo ""
    if command -v systemctl &> /dev/null; then
        echo "🔧 Service Management:"
        echo "   sudo systemctl start commercial-view-https"
        echo "   sudo systemctl status commercial-view-https"
    fi
    echo ""
    print_success "Spanish Factoring system secured with SSL/TLS! 🇪🇸🔒"
}

main "$@"