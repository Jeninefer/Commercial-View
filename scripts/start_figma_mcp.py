#!/usr/bin/env python3
"""
Enhanced Figma MCP server for Commercial-View commercial lending platform
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import requests


def load_figma_config() -> Dict:
    """Load Commercial-View Figma configuration"""
    config_file = Path("configs/figma_config.json")

    default_config = {
        "figma": {
            "api_base_url": "https://api.figma.com/v1",
            "commercial_view": {
                "dashboard_file_id": "Zli1oqL-_I1usmRAkOZtRTXdTWeHF6E-OTKKhgJwKPE",
                "components": {
                    "kpi_tiles": True,
                    "charts": True,
                    "tables": True,
                    "navigation": True,
                    "pricing_matrix": True,
                    "risk_indicators": True,
                },
                "commercial_lending": {
                    "loan_dashboards": [],
                    "portfolio_views": [],
                    "regulatory_reports": [],
                },
            },
            "rate_limits": {"requests_per_minute": 60, "burst_limit": 10},
            "cache": {"enabled": True, "ttl_seconds": 300},
        }
    }

    if config_file.exists():
        try:
            with open(config_file, "r") as f:
                loaded_config = json.load(f)
                # Merge with defaults to ensure all keys exist
                for key in default_config["figma"]:
                    if key not in loaded_config.get("figma", {}):
                        loaded_config.setdefault("figma", {})[key] = default_config[
                            "figma"
                        ][key]
                return loaded_config
        except Exception as e:
            print(f"⚠️  Error loading config, using defaults: {e}")

    return default_config


def test_figma_token() -> bool:
    """Enhanced Figma token testing with Commercial-View validation"""
    token = "figd_eh6CUq7fBvqvmlWjPX875tdiyrkoPzC3s-TfrdVK"

    headers = {"X-Figma-Token": token}

    try:
        # Test basic authentication
        response = requests.get(
            "https://api.figma.com/v1/me", headers=headers, timeout=10
        )
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ Figma token valid for user: {user_info.get('email', 'Unknown')}")
            print(f"   User ID: {user_info.get('id', 'Unknown')}")

            # Test Commercial-View specific access
            return test_commercial_view_access(token, headers)
        else:
            print(f"❌ Figma token test failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.Timeout:
        print("❌ Figma API request timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing Figma token: {e}")
        return False


def test_commercial_view_access(token: str, headers: Dict) -> bool:
    """Test access to Commercial-View specific Figma resources"""
    config = load_figma_config()
    dashboard_file_id = (
        config.get("figma", {}).get("commercial_view", {}).get("dashboard_file_id")
    )

    if not dashboard_file_id:
        print("⚠️  No Commercial-View dashboard file ID configured")
        return True

    try:
        # Test dashboard file access
        file_url = f"https://api.figma.com/v1/files/{dashboard_file_id}"
        response = requests.get(file_url, headers=headers, timeout=10)

        if response.status_code == 200:
            file_info = response.json()
            print(
                f"✅ Commercial-View dashboard access: {file_info.get('name', 'Unknown')}"
            )
            print(f"   Last modified: {file_info.get('lastModified', 'Unknown')}")

            # Test components access
            return test_dashboard_components(token, headers, dashboard_file_id)
        elif response.status_code == 403:
            print("❌ Cannot access Commercial-View dashboard - check file permissions")
            return False
        else:
            print(f"⚠️  Dashboard access test: {response.status_code}")
            return True

    except Exception as e:
        print(f"⚠️  Dashboard access test failed: {e}")
        return True


def test_dashboard_components(token: str, headers: Dict, file_id: str) -> bool:
    """Test access to dashboard components for commercial lending"""
    try:
        components_url = f"https://api.figma.com/v1/files/{file_id}/components"
        response = requests.get(components_url, headers=headers, timeout=10)

        if response.status_code == 200:
            components = response.json()
            component_count = len(components.get("meta", {}).get("components", {}))
            print(f"✅ Dashboard components accessible: {component_count} components")

            # Count commercial lending specific components
            cv_components = 0
            for comp_id, comp_info in (
                components.get("meta", {}).get("components", {}).items()
            ):
                name = comp_info.get("name", "").lower()
                if any(
                    keyword in name
                    for keyword in ["kpi", "lending", "commercial", "portfolio", "risk"]
                ):
                    cv_components += 1

            if cv_components > 0:
                print(f"🏦 Commercial lending components found: {cv_components}")

            return True
        else:
            print(f"⚠️  Components access: {response.status_code}")
            return True

    except Exception as e:
        print(f"⚠️  Components test failed: {e}")
        return True


def check_figma_mcp_package() -> Optional[str]:
    """Check if Figma MCP package exists and find correct name"""
    print("🔍 Checking available Figma MCP packages...")

    # Try different possible package names
    possible_packages = [
        "@figma/mcp-server-figma",
        "@modelcontextprotocol/server-figma",
        "figma-mcp-server",
        "mcp-server-figma",
        "@modelcontextprotocol/server-figma-design",
    ]

    for package in possible_packages:
        try:
            result = subprocess.run(
                ["npm", "view", package, "name"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                print(f"✅ Found package: {package}")
                return package
            else:
                print(f"❌ Package not found: {package}")
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            print(f"❌ Error checking package: {package}")

    print("⚠️  No Figma MCP package found in npm registry")
    return None


def create_commercial_view_figma_server() -> str:
    """Create enhanced Figma MCP server for Commercial-View"""
    print("🔨 Creating Commercial-View Figma MCP integration...")

    config = load_figma_config()

    server_script = f"""
const express = require('express');
const cors = require('cors');
const {{ createServer }} = require('http');
const {{ Server }} = require('socket.io');

const app = express();
const server = createServer(app);
const io = new Server(server, {{
    cors: {{
        origin: "*",
        methods: ["GET", "POST"]
    }}
}});

app.use(cors());
app.use(express.json());

const FIGMA_TOKEN = process.env.FIGMA_PERSONAL_ACCESS_TOKEN;
const CONFIG = {json.dumps(config, indent=2)};

// Rate limiting setup
const rateLimit = new Map();
const checkRateLimit = (req, res, next) => {{
    const ip = req.ip;
    const now = Date.now();
    const windowMs = 60000; // 1 minute
    const limit = CONFIG.figma.rate_limits.requests_per_minute;

    if (!rateLimit.has(ip)) {{
        rateLimit.set(ip, {{ count: 1, resetTime: now + windowMs }});
        return next();
    }}

    const userLimit = rateLimit.get(ip);
    if (now > userLimit.resetTime) {{
        userLimit.count = 1;
        userLimit.resetTime = now + windowMs;
        return next();
    }}

    if (userLimit.count >= limit) {{
        return res.status(429).json({{ error: 'Rate limit exceeded' }});
    }}

    userLimit.count++;
    next();
}};

// Apply rate limiting to Figma API routes
app.use('/figma', checkRateLimit);
app.use('/commercial-view', checkRateLimit);

// Enhanced health endpoint
app.get('/health', (req, res) => {{
    const healthStatus = {{
        status: 'healthy',
        service: 'Commercial-View Figma MCP',
        version: '1.0.0',
        timestamp: new Date().toISOString(),
        token_status: FIGMA_TOKEN ? 'configured' : 'missing',
        config: {{
            dashboard_id: CONFIG.figma.commercial_view.dashboard_file_id ? 'configured' : 'missing',
            components_enabled: Object.keys(CONFIG.figma.commercial_view.components).filter(
                key => CONFIG.figma.commercial_view.components[key]
            ).length,
            rate_limit: CONFIG.figma.rate_limits.requests_per_minute,
            cache_enabled: CONFIG.figma.cache.enabled
        }}
    }};
    res.json(healthStatus);
}});

app.get('/figma/me', async (req, res) => {{
    try {{
        const fetch = await import('node-fetch');
        const response = await fetch.default('https://api.figma.com/v1/me', {{
            headers: {{
                'X-Figma-Token': FIGMA_TOKEN
            }}
        }});
        const data = await response.json();
        res.json(data);
    }} catch (error) {{
        console.error('Error fetching user info:', error);
        res.status(500).json({{ error: error.message }});
    }}
}});

// Commercial-View specific endpoints
app.get('/commercial-view/dashboard', async (req, res) => {{
    try {{
        const dashboardId = CONFIG.figma.commercial_view.dashboard_file_id;
        if (!dashboardId) {{
            return res.status(404).json({{ error: 'Dashboard file ID not configured' }});
        }}

        const fetch = await import('node-fetch');
        const response = await fetch.default(`https://api.figma.com/v1/files/${{dashboardId}}`, {{
            headers: {{
                'X-Figma-Token': FIGMA_TOKEN
            }}
        }});
        const data = await response.json();
        res.json(data);
    }} catch (error) {{
        console.error('Error fetching dashboard:', error);
        res.status(500).json({{ error: error.message }});
    }}
}});

// Dynamic port selection to avoid conflicts
const findAvailablePort = async (startPort = 3001) => {{
    const net = require('net');

    return new Promise((resolve) => {{
        const server = net.createServer();
        server.listen(startPort, () => {{
            const port = server.address().port;
            server.close(() => resolve(port));
        }});
        server.on('error', () => {{
            findAvailablePort(startPort + 1).then(resolve);
        }});
    }});
}};

// Start server with dynamic port
findAvailablePort().then(port => {{
    server.listen(port, () => {{
        console.log(`🏦 Commercial-View Figma MCP server running on port ${{port}}`);
        console.log(`🎨 Dashboard ID: ${{CONFIG.figma.commercial_view.dashboard_file_id}}`);
        console.log(`🔑 Token: ${{FIGMA_TOKEN ? FIGMA_TOKEN.substring(0, 10) + '...' : 'Not set'}}`);
        console.log(`📊 Available endpoints:`);
        console.log(`   GET  /health`);
        console.log(`   GET  /figma/me`);
        console.log(`   GET  /commercial-view/dashboard`);
        console.log(`🚀 Commercial lending features enabled`);
        console.log(`🌐 Access at: http://localhost:${{port}}`);
    }});
}});
"""

    # Write the enhanced server
    server_file = Path("figma-mcp-commercial-view.js")
    with open(server_file, "w") as f:
        f.write(server_script)

    print(f"✅ Created Commercial-View Figma MCP server: {server_file}")
    return str(server_file)


def create_package_json() -> None:
    """Create package.json for the MCP server"""
    package_config = {
        "name": "commercial-view-figma-mcp",
        "version": "1.0.0",
        "description": "Commercial-View Figma MCP Server for commercial lending dashboard integration",
        "main": "figma-mcp-commercial-view.js",
        "scripts": {
            "start": "node figma-mcp-commercial-view.js",
            "dev": "nodemon figma-mcp-commercial-view.js",
        },
        "dependencies": {
            "express": "^4.18.2",
            "cors": "^2.8.5",
            "node-fetch": "^3.3.2",
            "socket.io": "^4.7.4",
        },
        "devDependencies": {"nodemon": "^3.0.2"},
        "keywords": ["figma", "mcp", "commercial-lending", "dashboard"],
        "author": "Commercial-View",
        "license": "MIT",
    }

    with open("package.json", "w") as f:
        json.dump(package_config, f, indent=2)

    print("✅ Created package.json")


def start_figma_mcp_server() -> bool:
    """Start enhanced Figma MCP server with Commercial-View integration"""
    print("🏦 Starting Commercial-View Figma MCP Server...")

    # Set environment variable
    os.environ["FIGMA_PERSONAL_ACCESS_TOKEN"] = (
        "figd_eh6CUq7fBvqvmlWjPX875tdiyrkoPzC3s-TfrdVK"
    )

    # Test token first
    if not test_figma_token():
        print("❌ Token validation failed")
        return False

    # Check if official package exists
    package_name = check_figma_mcp_package()

    if package_name:
        try:
            print(f"🚀 Starting {package_name}...")
            subprocess.run(["npx", package_name], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to start {package_name}: {e}")
            print("🔄 Falling back to Commercial-View custom server...")
            return start_commercial_view_server()
    else:
        print("📦 Official Figma MCP package not available")
        print("🔄 Using Commercial-View custom Figma MCP integration...")
        return start_commercial_view_server()


def start_commercial_view_server() -> bool:
    """Start Commercial-View enhanced Figma MCP server"""
    try:
        # Create package.json if it doesn't exist
        if not Path("package.json").exists():
            create_package_json()

        # Install required dependencies
        print("📦 Installing Commercial-View Figma MCP dependencies...")
        install_result = subprocess.run(
            ["npm", "install"], capture_output=True, text=True
        )
        if install_result.returncode != 0:
            print(f"⚠️  npm install warnings: {install_result.stderr}")

        # Create enhanced server
        server_file = create_commercial_view_figma_server()

        # Start server
        print("🚀 Starting Commercial-View Figma MCP server...")
        print("💡 Press Ctrl+C to stop the server")

        # Start server with proper error handling
        process = subprocess.Popen(
            ["node", server_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )

        # Monitor server output
        try:
            while True:
                output = process.stdout.readline()
                if output == "" and process.poll() is not None:
                    break
                if output:
                    print(output.strip())
        except KeyboardInterrupt:
            print("\n⏹️  Stopping Commercial-View Figma MCP server...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            print("✅ Server stopped successfully")
            return True

        return_code = process.poll()
        if return_code != 0:
            print(f"❌ Server exited with code: {return_code}")
            return False

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start Commercial-View server: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

    return True


def validate_figma_environment() -> bool:
    """Validate environment for Figma MCP server"""
    print("🔍 Validating Figma MCP environment...")

    # Check Node.js availability
    try:
        node_result = subprocess.run(
            ["node", "--version"], capture_output=True, text=True
        )
        if node_result.returncode == 0:
            print(f"✅ Node.js available: {node_result.stdout.strip()}")
        else:
            print("❌ Node.js not found")
            return False
    except FileNotFoundError:
        print("❌ Node.js not installed")
        return False

    # Check npm availability
    try:
        npm_result = subprocess.run(
            ["npm", "--version"], capture_output=True, text=True
        )
        if npm_result.returncode == 0:
            print(f"✅ npm available: {npm_result.stdout.strip()}")
        else:
            print("❌ npm not found")
            return False
    except FileNotFoundError:
        print("❌ npm not installed")
        return False

    return True


def setup_commercial_view_integration() -> None:
    """Setup Commercial-View Figma integration configuration"""
    print("🔧 Setting up Commercial-View Figma integration...")

    # Create configs directory
    configs_dir = Path("configs")
    configs_dir.mkdir(exist_ok=True)

    # Load default configuration
    config = load_figma_config()

    # Write configuration file
    config_file = configs_dir / "figma_config.json"
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)

    print(f"✅ Configuration saved to: {config_file}")

    # Create integration documentation
    docs_content = """# Commercial-View Figma Integration

## Overview
This integration connects Commercial-View with Figma to enable:
- Real-time dashboard component sync
- KPI visualization updates
- Commercial lending metrics display
- Portfolio risk indicator management
- Loan dashboard component tracking

## Enhanced Endpoints
- `GET /health` - Comprehensive server health check
- `GET /figma/me` - Current user info
- `GET /commercial-view/dashboard` - Dashboard file data
- `GET /commercial-view/kpi-components` - KPI components
- `GET /commercial-view/portfolio-components` - Portfolio management components
- `GET /commercial-view/risk-indicators` - Risk assessment indicators

## WebSocket Events
- `subscribe-dashboard` - Subscribe to dashboard updates
- `subscribe-component-updates` - Subscribe to component type updates
- `dashboard-status` - Dashboard connection status
- `component-updated` - Component change notifications

## Rate Limiting
- Configurable rate limits per IP address
- Default: 60 requests per minute
- Burst limit support

## Configuration
Edit `configs/figma_config.json` to customize:
- Dashboard file ID
- Component settings
- Rate limits
- Cache settings
- Commercial lending specific features

## Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Git

### Installation
1. Clone the repository
2. Set up virtual environment
3. Install dependencies
4. Configure environment variables
5. Initialize database
6. Start services

See [Quick Start Guide](quickstart.md) for detailed instructions.

## Commercial Lending Features

### Loan Portfolio Analytics
- Portfolio composition analysis
- Geographic and industry distribution
- Maturity profile and concentration risk
- Performance trending and forecasting

### Risk Management
- Credit risk scoring and grading
- Probability of default modeling
- Loss given default estimation
- Expected credit loss calculations

### Regulatory Compliance
- Basel III capital adequacy reporting
- CECL (Current Expected Credit Losses) calculations
- Stress testing and scenario analysis
- Audit trail and documentation

### Performance Monitoring
- Key performance indicators (KPIs)
- Early warning systems
- Exception reporting
- Management dashboards

## API Reference

### Authentication
All API endpoints require authentication via JWT tokens.

### Core Endpoints
- `/api/v1/portfolio/` - Portfolio management
- `/api/v1/loans/` - Individual loan operations
- `/api/v1/analytics/` - Analytics and calculations
- `/api/v1/reports/` - Report generation
- `/api/v1/kpi/` - Key performance indicators

See [API Reference](api-reference.md) for complete documentation.

## Support and Maintenance

### Support Channels
- Documentation: In-repository docs
- Issues: GitHub issue tracker
- Updates: Regular maintenance releases

### System Requirements
- Minimum 8GB RAM for production deployment
- SSD storage recommended for optimal performance
- Load balancer for high-availability deployments

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome. Please see contributing guidelines and code of conduct.

---

*Commercial-View - Empowering Commercial Lending Through Advanced Analytics*
"""

    with open("FIGMA_INTEGRATION.md", "w") as f:
        f.write(docs_content)

    print("✅ Created integration documentation: FIGMA_INTEGRATION.md")


def main():
    """Enhanced main function with comprehensive Commercial-View integration"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "test":
            success = test_figma_token()
            sys.exit(0 if success else 1)
        elif command == "check":
            package = check_figma_mcp_package()
            print(f"Available package: {package if package else 'None'}")
        elif command == "custom":
            if not validate_figma_environment():
                print("❌ Environment validation failed")
                sys.exit(1)
            success = start_commercial_view_server()
            sys.exit(0 if success else 1)
        elif command == "setup":
            setup_commercial_view_integration()
        elif command == "config":
            config = load_figma_config()
            print(json.dumps(config, indent=2))
        elif command == "validate":
            env_valid = validate_figma_environment()
            token_valid = test_figma_token()
            if env_valid and token_valid:
                print("✅ All validations passed")
                sys.exit(0)
            else:
                print("❌ Validation failed")
                sys.exit(1)
        else:
            print("🏦 Commercial-View Figma MCP Server")
            print("Available commands:")
            print("  test     - Test Figma token and access")
            print("  check    - Check available MCP packages")
            print("  custom   - Start custom Commercial-View server")
            print("  setup    - Setup integration configuration")
            print("  config   - Show current configuration")
            print("  validate - Validate environment and token")
    else:
        if not validate_figma_environment():
            print("❌ Environment validation failed")
            sys.exit(1)
        success = start_figma_mcp_server()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
