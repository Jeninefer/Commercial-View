# Quickstart Guide

[⬅ Documentation Hub](index.md) · [Architecture Overview](architecture-overview.md) · [API Reference](api-reference.md)

New to Commercial View? This guide walks you from zero to a running API instance with a sample analytics workflow.

## 1. Clone and Prepare the Environment

```bash
# Clone the repository
git clone https://github.com/Jeninefer/Commercial-View.git
cd Commercial-View

# Create and activate a Python virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# (Optional) Install development extras
pip install -r requirements-dev.txt
```

## 2. Validate the Environment

```bash
# Ensure the correct interpreter is active
python -c "import sys; print(sys.executable)"

# Run sanity checks
pytest tests/test_modules.py -q
python -m compileall src
```

If you encounter environment errors, review the [Troubleshooting](../README.md#troubleshooting) section.

## 3. Load Sample Data

Place CSV datasets under `data/` (see [Data & Governance Handbook](data-governance.md) for schema details). If you use the provided fixtures:

```bash
export COMMERCIAL_VIEW_DATA_PATH="$(pwd)/tests/data"
python -m pytest tests/test_data_loader.py -k loan -q
```

## 4. Start the API

```bash
source .venv/bin/activate
uvicorn run:app --reload --port 8000
```

Navigate to:

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>
- Health check: <http://localhost:8000/health>

## 5. Call Key Endpoints

```bash
# Fetch loan data
curl http://localhost:8000/loan-data | jq

# Retrieve payment schedule
curl http://localhost:8000/payment-schedule | jq

# Portfolio metrics
curl http://localhost:8000/portfolio-metrics | jq
```

For the complete endpoint catalog, see the [API Reference](api-reference.md).

## 6. Run Analytics Pipelines Manually

```bash
source .venv/bin/activate
python -m src.pipeline
```

The pipeline prints warnings if the virtual environment is misconfigured or dependencies are missing—fix these before proceeding.

## 7. Optional: Launch the Dashboard

```bash
cd frontend/dashboard
npm install
npm start
```

Configure the dashboard to point to `http://localhost:8000`.

## 8. Next Steps

- Explore the [Implementation Guide](implementation-guide.md) to understand the codebase.
- Review [Testing & Quality Strategy](testing-and-quality.md) before opening a pull request.
- For production readiness, align with the [Operations Runbook](operations-runbook.md) and [Secrets Management](secrets-management.md).
