#!/usr/bin/env python3
"""
Enhanced Uvicorn server management for Commercial-View
"""

import os
import sys
import subprocess
import signal
import time
import json
import logging
import psutil
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import requests
from contextlib import contextmanager


class UvicornManager:
    """Manage Uvicorn server for Commercial-View commercial lending platform"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.app_module = "run:app"
        self.default_host = "0.0.0.0"
        self.default_port = 8000
        self.pid_file = self.project_root / "var" / "run" / "uvicorn.pid"
        self.log_dir = self.project_root / "var" / "log"
        self.config_dir = self.project_root / "configs"

        # Ensure directories exist
        self.pid_file.parent.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def load_environment(self) -> None:
        """Load Commercial-View environment variables and commercial lending configurations"""
        # Set project paths
        os.environ["COMMERCIAL_VIEW_ROOT"] = str(self.project_root)
        os.environ["PYTHONPATH"] = (
            f"{self.project_root}/src:{os.environ.get('PYTHONPATH', '')}"
        )

        # Commercial lending specific environment variables
        os.environ["COMMERCIAL_VIEW_MODE"] = "production"
        os.environ["PRICING_CONFIG_PATH"] = str(self.config_dir / "pricing_config.yml")
        os.environ["DPD_POLICY_PATH"] = str(self.config_dir / "dpd_policy.yml")
        os.environ["COLUMN_MAPS_PATH"] = str(self.config_dir / "column_maps.yml")

        # Load .env file if it exists
        env_file = self.project_root / ".env"
        if env_file.exists():
            with open(env_file, encoding="utf-8") as f:
                for line in f:
                    if line.strip() and not line.startswith("#") and "=" in line:
                        key, value = line.strip().split("=", 1)
                        os.environ[key] = value

    def validate_commercial_lending_config(self) -> bool:
        """Validate commercial lending configuration files before starting server"""
        required_configs = [
            self.config_dir / "pricing_config.yml",
            self.config_dir / "dpd_policy.yml",
            self.config_dir / "column_maps.yml",
        ]

        missing_configs = []
        for config in required_configs:
            if not config.exists():
                missing_configs.append(str(config))

        if missing_configs:
            print("❌ Missing required configuration files:")
            for config in missing_configs:
                print(f"   - {config}")
            return False

        print("✅ All commercial lending configuration files found")
        return True

    def setup_logging(self, log_level: str = "info") -> None:
        """Setup comprehensive logging for commercial lending operations"""
        log_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "detailed": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s"
                },
                "commercial": {
                    "format": "%(asctime)s [%(levelname)s] Commercial-View: %(message)s"
                },
            },
            "handlers": {
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": str(self.log_dir / "commercial_view.log"),
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": 5,
                    "formatter": "detailed",
                },
                "access": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": str(self.log_dir / "access.log"),
                    "maxBytes": 10485760,
                    "backupCount": 3,
                    "formatter": "commercial",
                },
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "commercial",
                },
            },
            "loggers": {
                "uvicorn": {
                    "level": log_level.upper(),
                    "handlers": ["file", "console"],
                },
                "uvicorn.access": {"level": "INFO", "handlers": ["access"]},
                "commercial_view": {"level": "INFO", "handlers": ["file", "console"]},
            },
        }

        logging.config.dictConfig(log_config)

    def get_security_headers(self) -> List[str]:
        """Get security headers for commercial lending compliance"""
        return [
            "--header",
            "X-Content-Type-Options:nosnif",
            "--header",
            "X-Frame-Options:DENY",
            "--header",
            "X-XSS-Protection:1; mode=block",
            "--header",
            "Strict-Transport-Security:max-age=31536000; includeSubDomains",
            "--header",
            "Content-Security-Policy:default-src 'sel'",
            "--header",
            "Referrer-Policy:strict-origin-when-cross-origin",
        ]

    def start_server(
        self,
        host: str = None,
        port: int = None,
        reload: bool = True,
        workers: int = 1,
        log_level: str = "info",
        access_log: bool = True,
        ssl_keyfile: str = None,
        ssl_certfile: str = None,
        enable_security_headers: bool = True,
    ) -> None:
        """Start Uvicorn server with Commercial-View commercial lending configuration"""

        # Validate configuration before starting
        if not self.validate_commercial_lending_config():
            sys.exit(1)

        self.load_environment()
        self.setup_logging(log_level)

        host = host or self.default_host
        port = port or self.default_port

        cmd = [
            sys.executable,
            "-m",
            "uvicorn",
            self.app_module,
            "--host",
            host,
            "--port",
            str(port),
            "--log-level",
            log_level,
            "--log-config",
            str(self.create_log_config(log_level)),
        ]

        # Commercial lending specific configurations
        if reload:
            cmd.extend(
                [
                    "--reload",
                    "--reload-dir",
                    "src",
                    "--reload-dir",
                    "scripts",
                    "--reload-dir",
                    "configs",
                    "--reload-exclude",
                    "*.pyc",
                    "--reload-exclude",
                    "*.log",
                    "--reload-exclude",
                    "*.cache",
                ]
            )

        if workers > 1 and not reload:
            cmd.extend(["--workers", str(workers)])
            # Enable worker restart on memory threshold for large portfolios
            cmd.extend(["--max-requests", "1000", "--max-requests-jitter", "100"])

        if access_log:
            cmd.extend(
                [
                    "--access-log",
                    "--access-log-format",
                    '%(h)s "%(r)s" %(s)s %(B)s "%(f)s" "%(a)s" %(D)s',
                ]
            )

        # SSL/TLS configuration for production
        if ssl_keyfile and ssl_certfile:
            cmd.extend(["--ssl-keyfile", ssl_keyfile, "--ssl-certfile", ssl_certfile])
            print("🔒 SSL/TLS enabled for secure commercial lending operations")

        # Security headers for commercial lending compliance
        if enable_security_headers:
            cmd.extend(self.get_security_headers())

        # Commercial lending performance optimizations
        cmd.extend(
            [
                "--loop",
                "uvloop",  # High-performance event loop
                "--http",
                "httptools",  # Fast HTTP parsing
                "--lifespan",
                "on",  # Enable lifespan events for initialization
                "--server-header",  # Disable server header for security
                "--date-header",  # Enable date header for compliance
            ]
        )

        print("🏦 Starting Commercial-View Commercial Lending Platform")
        print(f"📍 Server: {host}:{port}")
        print(f"📁 Project root: {self.project_root}")
        print(f"⚙️ Workers: {workers}")
        print(f"🔄 Reload: {'Enabled' if reload else 'Disabled'}")
        print(f"🔧 Command: {' '.join(cmd)}")

        # Write PID file for process management
        try:
            os.chdir(self.project_root)
            process = subprocess.Popen(cmd)

            with open(self.pid_file, "w") as f:
                f.write(str(process.pid))

            print(f"📝 PID {process.pid} written to {self.pid_file}")

            # Wait for process to complete
            process.wait()

        except KeyboardInterrupt:
            print("\n🛑 Commercial-View server stopped by user")
            self.cleanup_pid_file()
        except Exception as e:
            print(f"❌ Error starting Commercial-View server: {e}")
            self.cleanup_pid_file()
            sys.exit(1)

    def create_log_config(self, log_level: str) -> Path:
        """Create logging configuration file for commercial lending operations"""
        log_config_file = self.project_root / "var" / "log_config.json"
        log_config_file.parent.mkdir(parents=True, exist_ok=True)

        config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                },
                "access": {
                    "format": '%(asctime)s - %(client_addr)s - "%(request_line)s" %(status_code)s',
                },
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": str(self.log_dir / "commercial_view.log"),
                    "maxBytes": 10485760,
                    "backupCount": 5,
                },
                "access": {
                    "formatter": "access",
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": str(self.log_dir / "access.log"),
                    "maxBytes": 10485760,
                    "backupCount": 3,
                },
            },
            "loggers": {
                "uvicorn": {"handlers": ["default"], "level": log_level.upper()},
                "uvicorn.access": {
                    "handlers": ["access"],
                    "level": "INFO",
                    "propagate": False,
                },
            },
        }

        with open(log_config_file, "w") as f:
            json.dump(config, f, indent=2)

        return log_config_file

    def start_development_server(self) -> None:
        """Start server with development settings for commercial lending development"""
        print("🔧 Starting Commercial-View in DEVELOPMENT mode")
        self.start_server(
            host="127.0.0.1",
            port=8000,
            reload=True,
            log_level="debug",
            access_log=True,
            enable_security_headers=False,  # Disabled for development
        )

    def start_production_server(self) -> None:
        """Start server with production settings for commercial lending operations"""
        print("🏭 Starting Commercial-View in PRODUCTION mode")

        # Production SSL configuration (if certificates exist)
        ssl_cert = self.project_root / "certs" / "commercial_view.crt"
        ssl_key = self.project_root / "certs" / "commercial_view.key"

        ssl_keyfile = str(ssl_key) if ssl_key.exists() else None
        ssl_certfile = str(ssl_cert) if ssl_cert.exists() else None

        self.start_server(
            host="0.0.0.0",
            port=8000,
            reload=False,
            workers=min(4, os.cpu_count() or 1),  # Optimize for commercial workloads
            log_level="info",
            access_log=True,
            ssl_keyfile=ssl_keyfile,
            ssl_certfile=ssl_certfile,
            enable_security_headers=True,
        )

    def start_high_performance_server(self) -> None:
        """Start server optimized for large commercial lending portfolios"""
        print("⚡ Starting Commercial-View in HIGH PERFORMANCE mode")

        cpu_count = os.cpu_count() or 1
        optimal_workers = min(cpu_count * 2, 8)  # Balance performance and memory

        self.start_server(
            host="0.0.0.0",
            port=8000,
            reload=False,
            workers=optimal_workers,
            log_level="warning",  # Reduced logging for performance
            access_log=False,
            enable_security_headers=True,
        )

    def check_server_health(
        self, host: str = "localhost", port: int = 8000, ssl: bool = False
    ) -> Dict[str, Any]:
        """Enhanced health check for commercial lending platform"""
        protocol = "https" if ssl else "http"
        base_url = f"{protocol}://{host}:{port}"

        health_status = {
            "server_running": False,
            "health_check": False,
            "api_endpoints": {},
            "response_time": None,
            "timestamp": datetime.now().isoformat(),
        }

        try:
            # Check if server is running
            start_time = time.time()
            response = requests.get(f"{base_url}/health", timeout=10)
            health_status["response_time"] = round((time.time() - start_time) * 1000, 2)

            if response.status_code == 200:
                health_status["server_running"] = True
                health_status["health_check"] = True

                # Check commercial lending specific endpoints
                endpoints_to_check = [
                    "/api/v1/pricing",
                    "/api/v1/dpd-analysis",
                    "/api/v1/portfolio-metrics",
                    "/api/v1/risk-assessment",
                ]

                for endpoint in endpoints_to_check:
                    try:
                        ep_response = requests.get(f"{base_url}{endpoint}", timeout=5)
                        health_status["api_endpoints"][endpoint] = {
                            "status_code": ep_response.status_code,
                            "available": ep_response.status_code
                            in [
                                200,
                                404,
                                405,
                            ],  # 404/405 means endpoint exists but method not allowed
                        }
                    except Exception as e:
                        health_status["api_endpoints"][endpoint] = {
                            "status_code": None,
                            "available": False,
                            "error": str(e),
                        }

        except requests.exceptions.ConnectionError:
            health_status["error"] = "Connection refused - server not running"
        except requests.exceptions.Timeout:
            health_status["error"] = "Health check timeout"
        except Exception as e:
            health_status["error"] = str(e)

        return health_status

    def get_server_status(self) -> Dict[str, Any]:
        """Get detailed server status including resource usage"""
        status = {
            "pid_file_exists": self.pid_file.exists(),
            "process_running": False,
            "resource_usage": {},
            "commercial_view_status": "stopped",
        }

        if self.pid_file.exists():
            try:
                with open(self.pid_file, "r") as f:
                    pid = int(f.read().strip())

                if psutil.pid_exists(pid):
                    process = psutil.Process(pid)
                    status["process_running"] = True
                    status["pid"] = pid
                    status["resource_usage"] = {
                        "cpu_percent": process.cpu_percent(interval=1),
                        "memory_mb": round(process.memory_info().rss / 1024 / 1024, 2),
                        "memory_percent": process.memory_percent(),
                        "num_threads": process.num_threads(),
                        "create_time": datetime.fromtimestamp(
                            process.create_time()
                        ).isoformat(),
                    }
                    status["commercial_view_status"] = "running"
                else:
                    status["commercial_view_status"] = "pid_stale"

            except (ValueError, ProcessLookupError, psutil.NoSuchProcess) as e:
                status["error"] = str(e)

        return status

    def cleanup_pid_file(self) -> None:
        """Clean up PID file"""
        if self.pid_file.exists():
            try:
                self.pid_file.unlink()
                print(f"🧹 Cleaned up PID file: {self.pid_file}")
            except Exception as e:
                print(f"⚠️ Could not clean up PID file: {e}")


def main():
    """Main Uvicorn management function for Commercial-View"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Manage Commercial-View Commercial Lending Server"
    )
    parser.add_argument(
        "action",
        choices=["dev", "prod", "per", "kill", "health", "status"],
        help="Action to perform",
    )
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--workers", type=int, default=1, help="Number of workers")
    parser.add_argument("--log-level", default="info", help="Log level")
    parser.add_argument("--ssl", action="store_true", help="Use HTTPS for health check")
    parser.add_argument("--json", action="store_true", help="Output JSON format")

    args = parser.parse_args()
    manager = UvicornManager()

    if args.action == "dev":
        manager.start_development_server()
    elif args.action == "prod":
        manager.start_production_server()
    elif args.action == "per":
        manager.start_high_performance_server()
    elif args.action == "kill":
        killed = manager.kill_server_on_port(args.port)
        return 0 if killed else 1
    elif args.action == "health":
        health = manager.check_server_health(args.host, args.port, args.ssl)
        if args.json:
            print(json.dumps(health, indent=2))
        else:
            status = "✅ Healthy" if health["health_check"] else "❌ Unhealthy"
            print(f"Commercial-View Server Health: {status}")
            if health.get("response_time"):
                print(f"Response Time: {health['response_time']}ms")
            if health.get("error"):
                print(f"Error: {health['error']}")
        return 0 if health["health_check"] else 1
    elif args.action == "status":
        status = manager.get_server_status()
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print(
                f"🏦 Commercial-View Status: {status['commercial_view_status'].upper()}"
            )
            if status["process_running"]:
                print(f"📊 CPU: {status['resource_usage']['cpu_percent']}%")
                print(
                    f"💾 Memory: {status['resource_usage']['memory_mb']} MB ({status['resource_usage']['memory_percent']:.1f}%)"
                )
                print(f"🧵 Threads: {status['resource_usage']['num_threads']}")
        return 0 if status["process_running"] else 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
