# Implementation Guide

[⬅ Documentation Hub](index.md) · [Architecture Overview](architecture-overview.md)

This guide dives into the code structure, conventions, and patterns that underpin Commercial View. Use it when modifying existing modules or designing new features.

## Repository Layout

| Path | Purpose |
|------|---------|
| `run.py` | FastAPI entrypoint with fallback pipeline stub and global exception handling. |
| `src/pipeline.py` | Orchestrates dataset loading, KPI computation, and caching of analytics outputs. |
| `src/` | Domain modules: data loaders, analytics engines, optimizers, and utility helpers. |
| `scripts/` | Tooling for starting servers, notebooks, or diagnostics with strict environment enforcement. |
| `frontend/` | Optional dashboard assets (Node-based) for visualization. |
| `docs/` | Documentation hub (this guide, architecture, operations, etc.). |
| `tests/` | Pytest suite covering core modules and API expectations. |

## Coding Conventions

- **Python Version:** Target Python 3.11+. Static typing is encouraged—type hints are widely used across modules.
- **Imports:** Keep standard library imports first, third-party second, internal modules last.
- **Logging:** Rely on `logging.getLogger(__name__)`. Avoid `print` statements outside CLI warnings. Respect the fallback logging level set in `run.py`.
- **DataFrames:** Validate schema assumptions explicitly. Prefer `.copy()` before mutating DataFrames.
- **Error Handling:** Raise informative exceptions from loaders, but degrade gracefully in API routes by returning fallbacks (as seen in `run.py`).

## Key Modules

### `src/data_loader.py`

Centralized CSV ingestion. Functions like `load_loan_data` and `load_payment_schedule` accept an optional base path, enabling tests to redirect to fixture directories. Each loader performs schema normalization and value coercion before returning a `pandas.DataFrame`.

### `src/pipeline.py`

`CommercialViewPipeline` is the core orchestrator:

1. `load_all_datasets` iterates through loader registry and caches DataFrames.
2. Metrics methods (`compute_dpd_metrics`, `compute_portfolio_metrics`, `compute_recovery_metrics`) operate on cached data and enrich with derived columns.
3. Methods stash results in `_computed_metrics` for reuse by API endpoints or downstream consumers.

### Analytics Extensions

- `src/feature_engineer.py`: Derived features for segmentation, credit scoring, and underwriting models.
- `src/metrics_calculator.py`: Aggregates cross-sectional KPIs and prepares time-series metrics.
- `src/portfolio_optimizer.py`: Provides optimization routines for loan allocation or rebalancing.
- `src/evergreen_analytics.py` & `src/evergreen.py`: Specialized calculations for evergreen lending products.
- `src/dpd_analyzer.py`: Domain-specific logic for days-past-due classifications.

### API Layer (`run.py` and `src/api.py`)

- Applies CORS restrictions from `ALLOWED_ORIGINS`.
- Exposes endpoints such as `/loan-data`, `/payment-schedule`, `/historic-real-payment`, `/portfolio-metrics`, and `/health`.
- Provides fallback responses when datasets are missing, ensuring contract stability.

## Adding a New Feature

1. **Design** – Draft the user journey and data dependencies. Reference the [Architecture Overview](architecture-overview.md) to identify existing modules to extend.
2. **Implement** – Create or update modules under `src/`. Follow type hints and log meaningful context.
3. **Expose** – If the feature surfaces via API, add routes in `src/api.py` or `run.py`. Document the contract in the [API Reference](api-reference.md).
4. **Test** – Add or update unit tests under `tests/`. Use fixtures to supply synthetic data. Capture new behaviours in the [Testing & Quality Strategy](testing-and-quality.md) if additional workflows are introduced.
5. **Document** – Update relevant guides and changelogs. If secrets or config values are involved, reflect them in [Secrets Management](secrets-management.md).

## Configuration Files

- `config/` and `configs/`: Example YAML/JSON packages for pipelines.
- `requirements*.txt`: Python dependency pins.
- `package.json`: Node dependencies (currently minimal, used for tooling and dashboards).

## Developer Tooling

- `server_control.py`: Wraps Uvicorn invocation with port checks, kill signals, and logging controls.
- `scripts/uvicorn_manager.py`: Programmatic server lifecycle management for CI/CD pipelines.
- `scripts/start_jupyter.py` & `scripts/start_ipython.py`: Bootstraps interactive environments with project paths and environment variables.
- `scripts/install_kernel.py`: Installs Jupyter kernels bound to the project virtualenv.

## Data Contracts

Refer to `tests/data/` fixtures and loader docstrings for canonical column names. When evolving schemas, update the [Data & Governance Handbook](data-governance.md) and reflect expectations in the API reference.

## Related Documents

- [Quickstart Guide](quickstart.md)
- [Testing & Quality Strategy](testing-and-quality.md)
- [Operations Runbook](operations-runbook.md)
