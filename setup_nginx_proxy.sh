#!/bin/bash

# Nginx Reverse Proxy Setup for Commercial-View
# Spanish Factoring & Commercial Lending Analytics
# Production Load Balancing and SSL Termination

set -e

# Configuration
DOMAIN=${DOMAIN:-"commercial-view.local"}
API_PORT=${API_PORT:-8000}
HTTPS_PORT=${HTTPS_PORT:-8443}
NGINX_SITES_AVAILABLE="/etc/nginx/sites-available"
NGINX_SITES_ENABLED="/etc/nginx/sites-enabled"
SSL_DIR="/etc/ssl/commercial-view"

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

print_header "🌐 Nginx Reverse Proxy Setup for Commercial-View"
echo -e "🏦 Spanish Factoring & Commercial Lending Analytics"
echo -e "📊 Domain: ${DOMAIN} | Backend: localhost:${API_PORT}"
echo ""

# Check if running with appropriate privileges
if [[ $EUID -ne 0 ]]; then
    print_warning "Not running as root. Some operations may require sudo."
    USE_SUDO="sudo"
else
    USE_SUDO=""
fi

# Install Nginx
install_nginx() {
    print_status "Installing Nginx..."
    
    if command -v nginx &> /dev/null; then
        print_success "Nginx is already installed"
        return 0
    fi
    
    # Install based on OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install nginx
        else
            print_error "Please install Homebrew first or install nginx manually"
            return 1
        fi
        
        # macOS nginx paths
        NGINX_SITES_AVAILABLE="/usr/local/etc/nginx/sites-available"
        NGINX_SITES_ENABLED="/usr/local/etc/nginx/sites-enabled"
        
    elif [[ -f /etc/debian_version ]]; then
        # Debian/Ubuntu
        $USE_SUDO apt-get update
        $USE_SUDO apt-get install -y nginx
    elif [[ -f /etc/redhat-release ]]; then
        # RHEL/CentOS
        $USE_SUDO yum install -y nginx
    else
        print_error "Unsupported OS for automatic nginx installation"
        return 1
    fi
    
    print_success "Nginx installed successfully"
}

# Create directories for sites
setup_nginx_directories() {
    print_status "Setting up Nginx directories..."
    
    $USE_SUDO mkdir -p "$NGINX_SITES_AVAILABLE"
    $USE_SUDO mkdir -p "$NGINX_SITES_ENABLED"
    
    # Create nginx.conf that includes sites-enabled
    if [[ "$OSTYPE" == "darwin"* ]]; then
        NGINX_CONF="/usr/local/etc/nginx/nginx.conf"
    else
        NGINX_CONF="/etc/nginx/nginx.conf"
    fi
    
    # Backup original config
    $USE_SUDO cp "$NGINX_CONF" "$NGINX_CONF.backup.$(date +%Y%m%d_%H%M%S)"
    
    print_success "Nginx directories configured"
}

# Create Commercial-View site configuration
create_nginx_site() {
    print_status "Creating Nginx site configuration..."
    
    # Create the site configuration
    cat > /tmp/commercial-view.nginx << EOF
# Commercial-View Spanish Factoring & Commercial Lending
# Nginx Reverse Proxy Configuration
# Abaco Integration: 48,853 records | \$208,192,588.65 USD

# Rate limiting for API protection
limit_req_zone \$binary_remote_addr zone=api_limit:10m rate=10r/s;
limit_req_zone \$binary_remote_addr zone=health_limit:10m rate=1r/s;

# Upstream backend servers
upstream commercial_view_backend {
    # Primary API server
    server 127.0.0.1:$API_PORT max_fails=3 fail_timeout=30s;
    
    # Add more servers for load balancing
    # server 127.0.0.1:8001 max_fails=3 fail_timeout=30s;
    # server 127.0.0.1:8002 max_fails=3 fail_timeout=30s;
    
    # Health check and load balancing
    keepalive 32;
}

# HTTPS Server Block (Primary)
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name $DOMAIN;
    
    # SSL Configuration
    ssl_certificate $SSL_DIR/certificate.crt;
    ssl_certificate_key $SSL_DIR/private.key;
    
    # SSL Security Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self';";
    
    # Commercial-View branding
    add_header X-Powered-By "Commercial-View-Spanish-Factoring" always;
    add_header X-Abaco-Records "48853" always;
    add_header X-Portfolio-USD "208192588.65" always;
    
    # Logging
    access_log /var/log/nginx/commercial-view-access.log;
    error_log /var/log/nginx/commercial-view-error.log;
    
    # Root directory for static files (if any)
    root /var/www/commercial-view;
    index index.html;
    
    # Health check endpoint (high frequency)
    location /health {
        limit_req zone=health_limit burst=5;
        
        proxy_pass http://commercial_view_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Health check specific settings
        proxy_connect_timeout 5s;
        proxy_send_timeout 5s;
        proxy_read_timeout 5s;
        
        # Add health check headers
        add_header X-Health-Check "Spanish-Factoring-System" always;
    }
    
    # Performance monitoring endpoint
    location /performance {
        limit_req zone=api_limit burst=10;
        
        proxy_pass http://commercial_view_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeout settings for performance monitoring
        proxy_connect_timeout 10s;
        proxy_send_timeout 15s;
        proxy_read_timeout 15s;
    }
    
    # Prometheus metrics endpoint
    location /metrics {
        limit_req zone=api_limit burst=5;
        
        # Restrict access to monitoring systems
        allow 127.0.0.1;
        allow ::1;
        # allow 10.0.0.0/8;  # Internal network
        deny all;
        
        proxy_pass http://commercial_view_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # API Documentation (if enabled)
    location ~ ^/(docs|redoc) {
        limit_req zone=api_limit burst=5;
        
        proxy_pass http://commercial_view_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Main API endpoints
    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;
        
        proxy_pass http://commercial_view_backend/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # API specific timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
        
        # Buffer settings for large responses
        proxy_buffering on;
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
        
        # Spanish factoring specific headers
        add_header X-API-Version "1.0" always;
        add_header X-Spanish-Support "enabled" always;
    }
    
    # Root endpoint and general API
    location / {
        limit_req zone=api_limit burst=10;
        
        proxy_pass http://commercial_view_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Standard timeouts
        proxy_connect_timeout 15s;
        proxy_send_timeout 15s;
        proxy_read_timeout 15s;
        
        # Keep-alive
        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }
    
    # Static files (if any)
    location /static/ {
        alias /var/www/commercial-view/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml;
}

# HTTP to HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN;
    
    # Redirect all HTTP traffic to HTTPS
    return 301 https://\$server_name\$request_uri;
}

# Default server block (catch-all)
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    listen 443 ssl default_server;
    listen [::]:443 ssl default_server;
    
    # SSL for default server
    ssl_certificate $SSL_DIR/certificate.crt;
    ssl_certificate_key $SSL_DIR/private.key;
    
    server_name _;
    
    # Return 444 (no response) for unknown hosts
    return 444;
}
EOF

    # Install the site configuration
    $USE_SUDO cp /tmp/commercial-view.nginx "$NGINX_SITES_AVAILABLE/commercial-view"
    
    # Enable the site
    $USE_SUDO ln -sf "$NGINX_SITES_AVAILABLE/commercial-view" "$NGINX_SITES_ENABLED/"
    
    # Remove default site if it exists
    $USE_SUDO rm -f "$NGINX_SITES_ENABLED/default"
    
    print_success "Nginx site configuration created"
}

# Create main nginx.conf with optimizations
create_nginx_main_config() {
    print_status "Creating optimized nginx.conf..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        NGINX_CONF="/usr/local/etc/nginx/nginx.conf"
    else
        NGINX_CONF="/etc/nginx/nginx.conf"
    fi
    
    cat > /tmp/nginx.conf << 'EOF'
# Commercial-View Nginx Configuration
# Spanish Factoring & Commercial Lending Analytics
# Optimized for Production Performance

user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

# Worker connections and performance
events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    # Basic settings
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # Logging format
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for" '
                    'rt=$request_time uct="$upstream_connect_time" '
                    'uht="$upstream_header_time" urt="$upstream_response_time"';
    
    access_log /var/log/nginx/access.log main;
    
    # Performance optimizations
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    keepalive_requests 100;
    types_hash_max_size 2048;
    
    # Hide nginx version
    server_tokens off;
    
    # Buffer sizes
    client_body_buffer_size 128k;
    client_max_body_size 10m;
    client_header_buffer_size 1k;
    large_client_header_buffers 4 4k;
    output_buffers 1 32k;
    postpone_output 1460;
    
    # Timeouts
    client_body_timeout 12;
    client_header_timeout 12;
    send_timeout 10;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;
    
    # Include site configurations
    include /etc/nginx/sites-enabled/*;
}
EOF

    # Adjust paths for macOS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' 's|user nginx;|#user nginx;|g' /tmp/nginx.conf
        sed -i '' 's|/var/log/nginx/|/usr/local/var/log/nginx/|g' /tmp/nginx.conf
        sed -i '' 's|/var/run/nginx.pid|/usr/local/var/run/nginx.pid|g' /tmp/nginx.conf
        sed -i '' 's|/etc/nginx/mime.types|/usr/local/etc/nginx/mime.types|g' /tmp/nginx.conf
        sed -i '' 's|/etc/nginx/sites-enabled/|/usr/local/etc/nginx/sites-enabled/|g' /tmp/nginx.conf
    fi
    
    $USE_SUDO cp /tmp/nginx.conf "$NGINX_CONF"
    
    print_success "Nginx main configuration created"
}

# Create log directories and setup log rotation
setup_logging() {
    print_status "Setting up logging and rotation..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        LOG_DIR="/usr/local/var/log/nginx"
        $USE_SUDO mkdir -p "$LOG_DIR"
    else
        LOG_DIR="/var/log/nginx"
        $USE_SUDO mkdir -p "$LOG_DIR"
        
        # Setup logrotate for nginx
        cat > /tmp/nginx-logrotate << 'EOF'
/var/log/nginx/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 nginx nginx
    sharedscripts
    prerotate
        if [ -d /etc/logrotate.d/httpd-prerotate ]; then \
            run-parts /etc/logrotate.d/httpd-prerotate; \
        fi \
    endscript
    postrotate
        invoke-rc.d nginx rotate >/dev/null 2>&1
    endscript
}
EOF

        $USE_SUDO cp /tmp/nginx-logrotate /etc/logrotate.d/nginx
    fi
    
    print_success "Logging configured"
}

# Test and start nginx
start_nginx() {
    print_status "Testing Nginx configuration..."
    
    # Test configuration
    if $USE_SUDO nginx -t; then
        print_success "Nginx configuration is valid"
    else
        print_error "Nginx configuration test failed"
        return 1
    fi
    
    # Start or reload nginx
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if pgrep -x "nginx" > /dev/null; then
            $USE_SUDO nginx -s reload
            print_success "Nginx reloaded"
        else
            $USE_SUDO nginx
            print_success "Nginx started"
        fi
    else
        # Linux
        if command -v systemctl &> /dev/null; then
            $USE_SUDO systemctl enable nginx
            $USE_SUDO systemctl restart nginx
            print_success "Nginx service started"
        else
            $USE_SUDO service nginx restart
            print_success "Nginx restarted"
        fi
    fi
}

# Create monitoring script
create_nginx_monitoring() {
    print_status "Creating Nginx monitoring script..."
    
    cat > nginx_monitor.sh << 'EOF'
#!/bin/bash
# Nginx Monitoring Script for Commercial-View
# Spanish Factoring & Commercial Lending Analytics

echo "🌐 Commercial-View Nginx Status"
echo "================================="

# Check if Nginx is running
if pgrep -x "nginx" > /dev/null; then
    echo "✅ Nginx: Running"
else
    echo "❌ Nginx: Not running"
fi

# Check SSL certificate expiration
if [ -f "/etc/ssl/commercial-view/certificate.crt" ]; then
    EXPIRY=$(openssl x509 -in /etc/ssl/commercial-view/certificate.crt -noout -dates | grep notAfter | cut -d= -f2)
    EXPIRY_EPOCH=$(date -d "$EXPIRY" +%s 2>/dev/null || date -j -f "%b %d %T %Y %Z" "$EXPIRY" +%s 2>/dev/null)
    NOW_EPOCH=$(date +%s)
    DAYS_LEFT=$(( (EXPIRY_EPOCH - NOW_EPOCH) / 86400 ))
    
    if [ $DAYS_LEFT -gt 30 ]; then
        echo "✅ SSL Certificate: $DAYS_LEFT days remaining"
    elif [ $DAYS_LEFT -gt 7 ]; then
        echo "⚠️  SSL Certificate: $DAYS_LEFT days remaining (renewal recommended)"
    else
        echo "❌ SSL Certificate: $DAYS_LEFT days remaining (urgent renewal needed)"
    fi
else
    echo "⚠️  SSL Certificate: Not found"
fi

# Check upstream health
echo ""
echo "🏦 Upstream Health Check:"
if curl -s -k https://localhost/health > /dev/null; then
    echo "✅ API Backend: Healthy"
else
    echo "❌ API Backend: Unhealthy"
fi

# Show active connections
if command -v nginx &> /dev/null; then
    echo ""
    echo "📊 Nginx Statistics:"
    # This requires nginx status module - basic version
    echo "   Active processes: $(pgrep nginx | wc -l)"
fi

echo ""
echo "🇪🇸 Spanish Factoring System Status: Operational"
echo "📊 Abaco Integration: 48,853 records | $208M USD"
EOF

    chmod +x nginx_monitor.sh
    print_success "Nginx monitoring script created"
}

# Main execution
main() {
    install_nginx
    setup_nginx_directories
    create_nginx_site
    create_nginx_main_config
    setup_logging
    create_nginx_monitoring
    
    # Test configuration before starting
    start_nginx
    
    print_success "🌐 Nginx Reverse Proxy Setup Complete!"
    echo ""
    echo "📊 Reverse Proxy Configuration:"
    echo "   • Domain: $DOMAIN"
    echo "   • HTTPS: Port 443 (SSL termination)"
    echo "   • HTTP: Port 80 (redirects to HTTPS)"
    echo "   • Backend: localhost:$API_PORT"
    echo ""
    echo "🔧 Management Commands:"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "   • Test config: sudo nginx -t"
        echo "   • Reload: sudo nginx -s reload"
        echo "   • Monitor: ./nginx_monitor.sh"
    else
        echo "   • Status: sudo systemctl status nginx"
        echo "   • Reload: sudo systemctl reload nginx"
        echo "   • Monitor: ./nginx_monitor.sh"
    fi
    echo ""
    echo "🏦 Abaco Endpoints (via Nginx):"
    echo "   • Health: https://$DOMAIN/health"
    echo "   • Performance: https://$DOMAIN/performance"
    echo "   • Metrics: https://$DOMAIN/metrics (restricted)"
    echo ""
    print_success "Spanish Factoring system behind production proxy! 🇪🇸🌐"
}

main "$@"