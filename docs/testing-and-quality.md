# Testing & Quality Strategy

[⬅ Documentation Hub](index.md) · [Operations Runbook](operations-runbook.md)

Quality in Commercial View is enforced through automated tests, manual reviews, and documentation standards.

## Testing Pyramid

| Layer | Tooling | Scope |
|-------|---------|-------|
| Unit Tests | `pytest` | Validate loaders, pipeline computations, utility functions. |
| Integration Tests | `pytest` + fixture datasets | Exercise API endpoints against real DataFrame transformations. |
| End-to-End | Manual or scripted smoke tests | Deploy to staging and run critical user journeys (loan ingestion → metrics → export). |

## Test Suites

- `tests/test_modules.py` – sanity tests ensuring core modules import correctly.
- `tests/test_data_loader.py` – validates CSV ingestion, schema expectations, and error handling.
- `tests/test_feature_engineer.py` – covers feature engineering logic.
- `tests/test_feature_engineer_fix.py`, `test_quick_fix.py` – regression tests for previously identified defects.

## Coverage Expectations

- Maintain ≥80% coverage for critical modules (`run.py`, `src/pipeline.py`, `src/data_loader.py`).
- Add coverage gates in CI when feasible (see `scripts/run_coverage.py`).

## Static Analysis & Formatting

- Python: `black`, `ruff`/`flake8`, and `mypy` (where enabled).
- Markdown: Enforced via GitHub Actions workflow (see `.github/workflows/docs-quality.yml`).
- JavaScript/TypeScript (frontend): `npm run lint` (configure when dashboard is active).

## Test Data Management

- Store synthetic fixtures under `tests/data/`.
- For large datasets, use compressed formats and document schema expectations in [Data & Governance Handbook](data-governance.md).
- Refresh fixtures when schema evolves to prevent drift.

## Release Readiness Checklist

1. All automated tests pass locally and in CI.
2. Documentation updated (README, [Implementation Guide](implementation-guide.md), etc.).
3. Security review completed for sensitive changes (refer to [Security Constraints](security_constraints.md)).
4. Performance benchmarks assessed when pipeline logic changes (see [Performance SLOs](performance_slos.md)).

## Manual QA

- Validate API docs load correctly (Swagger, ReDoc).
- Run exploratory testing on analytics-heavy endpoints after major algorithm changes.
- Capture QA notes in release tickets for traceability.

## Observability During Testing

- Enable debug logging (`--log-level debug`) during integration tests when diagnosing issues.
- Monitor metrics exports (if wired) to ensure no regressions in latency or error rate.

## Related Documents

- [Quickstart Guide](quickstart.md)
- [Operations Runbook](operations-runbook.md)
- [Performance SLOs](performance_slos.md)
