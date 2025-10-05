# Commercial View

Enterprise-grade portfolio analytics for Abaco Capital.

## Setup and Installation

### Prerequisites

- Python 3.11+
- Virtual environment tool (venv)
- (Optional) Node 18+ for the dashboard

### Install

```bash
git clone https://github.com/Jeninefer/Commercial-View.git
cd Commercial-View

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

**Important**: Use the venv Python

✅ Correct:

```bash
source .venv/bin/activate
python run.py
pytest -q
```

❌ Incorrect:

```bash
/opt/homebrew/bin/python3 run.py
```

## Running the API

```bash
source .venv/bin/activate
uvicorn run:app --reload --port 8000
# or
python run.py
```

## Running Tests

```bash
source .venv/bin/activate
pytest
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
