# Commercial View

Enterprise-grade portfolio analytics for Abaco Capital.

## Setup and Installation

### Prerequisites

- Python 3.11+
- Virtual environment tool (venv)
- (Optional) Node 18+ for the dashboard frontend

### Install

```bash
git clone https://github.com/Jeninefer/Commercial-View.git
cd Commercial-View

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**Important**: Always use the virtual environment's Python!

✅ Correct usage:

```bash
source .venv/bin/activate
python run.py
pytest -q
```

❌ Incorrect usage:

```bash
python3 run.py         # ❌ Uses system Python (not virtual env)
pip install pandas     # ❌ Installs globally, not in .venv
```

## Running the API

### Quick Start

```bash
source .venv/bin/activate
uvicorn run:app --reload --port 8000
# or
python run.py
```

### Advanced Server Control

Use `server_control.py` for advanced server management:

```bash
# Start server on default port 8000
python server_control.py

# Start on custom port
python server_control.py --port 8001

# Kill existing processes and start fresh
python server_control.py --port 8000 --kill-existing

# Check what's using a port (without starting server)
python server_control.py --check-only --port 8000

# Start with custom host and logging
python server_control.py --host 127.0.0.1 --log-level debug

# Disable auto-reload for production
python server_control.py --no-reload

# Force kill stubborn processes
python server_control.py --port 8000 --kill-existing --force-kill
```

#### Server Control Options

| Option | Description | Default |
|--------|-------------|---------|
| `--port` | Port to run server on | 8000 |
| `--host` | Host interface to bind | 0.0.0.0 |
| `--app` | Application import path | run:app |
| `--no-reload` | Disable auto-reload | False |
| `--kill-existing` | Kill processes using port | False |
| `--force-kill` | Force kill with SIGKILL | False |
| `--log-level` | Logging level | info |
| `--check-only` | Only check port usage | False |

## Running Tests

```bash
source .venv/bin/activate
pytest -q                        # Run the full test suite
pytest tests/test_data_loader.py -v  # Run a specific test file
# with coverage
pytest --cov=src tests/
```

## API Docs

- Swagger: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

## Formatting / Type Check

```bash
black src/ tests/
mypy src/
```

## Docker (optional)

```bash
docker build -t commercial-view .
docker run -p 8000:8000 -v "$(pwd)/data:/app/data" commercial-view
```

## Architecture

- `src/data_loader.py` – data loading utilities
- `src/pipeline.py` – processing pipeline
- `run.py` – FastAPI app
- `server_control.py` – advanced server management utility
- `tests/` – test suite

## Configuration

### Data directory

By default, loaders read from `data/pricing/`. To override:

```bash
export COMMERCIAL_VIEW_DATA_PATH=/mnt/shared/pricing-data
# or per-run in your own CLI wrapper
```

### Dataset status

- ✅ Loan Data — present
- ✅ Historic Real Payment — present
- ✅ Payment Schedule — present
- ⚠️ Customer Data — missing (add `Abaco - Loan Tape_Customer Data_Table.csv`)
- ⚠️ Collateral — missing (add `Abaco - Loan Tape_Collateral_Table.csv`)

### Pricing

`data/pricing/` includes risk-based grids (example: `risk_based_pricing.csv`):

- High Risk (300–579): 11–13%
- Medium (580–669): 8–10%
- Low (670–739): 5.5–7.5%
- Very Low (740–850): 4.5–6%

## Frontend (optional, if using dashboard)

```bash
cd frontend/dashboard
npm install
npm start
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Import 'pandas' could not be resolved | Activate .venv and reinstall dependencies: `pip install -r requirements.txt` |
| pytest: command not found | Run `pip install pytest` inside the virtual environment |
| Port already in use | Use `python server_control.py --kill-existing` or try a different port |
| Permission denied killing process | Use `--force-kill` flag or run with sudo (not recommended) |
| Server won't start | Check environment with `python server_control.py --check-only` |
| Frontend build errors | Run `npm audit fix --force` or delete node_modules and reinstall |

### Server Control Troubleshooting

```bash
# Check if virtual environment is active
python server_control.py --check-only

# Find what's using port 8000
python server_control.py --check-only --port 8000

# Kill all processes on port and restart
python server_control.py --kill-existing --force-kill
```

## CI/CD & Versioning

- SemVer (MAJOR.MINOR.PATCH)
- Example release:

```bash
echo "1.2.0" > VERSION
git add VERSION && git commit -m "Bump version to 1.2.0"
git tag -a v1.2.0 -m "Release 1.2.0"
git push origin main --tags
```

## Contributing

1. Fork & branch
2. Implement & test
3. Lint/format
4. PR

## License

Proprietary to Abaco Capital.
