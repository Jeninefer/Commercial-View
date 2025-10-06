# Commercial-View Testing Playbook

This document explains how the automated test suites are organised, how they map to
product modules, and how to run or extend them locally and in CI.

## Test Topology

| Domain | Modules Covered | Test File(s) | Representative Scenarios |
| --- | --- | --- | --- |
| **Backend analytics** | `customer_analytics`, `loan_analytics`, `metrics_calculator`, API contracts | `tests/test_backend_analytics.py`, `tests/test_metrics_calculator.py`, `tests/test_api_endpoints.py` | Customer DPD aggregation, weighted portfolio metrics, FastAPI endpoint guards |
| **Data ingestion** | `data_loader`, `data_processor` | `tests/test_data_ingestion.py` | File discovery precedence, error handling for missing feeds, date conversion coercion |
| **AI services & optimisation** | `feature_engineer`, `field_detector`, `portfolio_optimizer` | `tests/test_ai_services.py` | Customer type classification, payment-field detection heuristics, concentration and DPD alerting |
| **Pipeline & integration** | `pipeline.CommercialViewPipeline` | `tests/test_pipeline_integration.py` | Dataset loading resilience, DPD distribution creation, cohort recovery calculations, executive summary synthesis |
| **Frontend components** | React dashboard shell (`App`) | `frontend/dashboard/test/app.test.tsx` | Accessibility affordances, navigation attributes, hero content rendering |

The suite currently implements **38 discrete test cases**, exceeding the 31-case
target while ensuring coverage of happy paths, guard rails, and integration flows.

## Running the Tests Locally

> **Prerequisites**
>
> * Python 3.10+ with the project dependencies installed (`pip install -r requirements.txt`)
> * Node.js 18+ with npm 8+

### Backend & Service Layer (pytest)

```bash
pytest
```

This command executes all Python unit and integration tests under `tests/`. The
suite bootstraps deterministic fixtures for the ETL pipeline, data ingestion, and
AI services. Key edge cases include missing CSV files, zero-weight metrics, and
defaulted loans.

### Frontend Dashboard (Vitest + Testing Library)

```bash
cd frontend/dashboard
npm install
npm run test:vitest
```

Vitest is configured with a JSDOM environment and Testing Library assertions. The
tests validate that the dashboard shell renders accessible navigation and CTA
elements, mirroring the user-facing entry point.

### Combined Execution (CI parity)

From the project root you can run the backend tests followed by the frontend suite
to mirror the CI workflow:

```bash
pytest && (cd frontend/dashboard && npm run test:vitest)
```

## Continuous Integration

GitHub Actions executes both runners on every push or pull request via
`.github/workflows/tests.yml`. The workflow provisions Python, installs
`requirements.txt`, runs `pytest`, then installs npm dependencies in
`frontend/dashboard` and executes `npm run test:vitest` with coverage enabled.

## Extending the Suite

1. **Pick the correct domain**: New analytics logic belongs in `tests/` alongside
   the relevant module. React components should be tested under
   `frontend/dashboard/test/` using Vitest.
2. **Leverage fixtures**: Prefer `pytest` fixtures for shared data or monkeypatching
   external dependencies. The existing `_bootstrap_pipeline` helper illustrates how
   to isolate ETL integrations without touching production modules.
3. **Assert behaviour, not implementation**: Use semantic assertions (e.g., DPD
   bucket names, alert counts, accessibility roles) instead of private attribute
   checks to keep tests resilient.
4. **Document the case**: When adding significant scenarios, append a line to the
   table above or include inline comments so future contributors understand the
   coverage intent.

Following these conventions keeps the testing stack comprehensive, maintainable,
and aligned with the platform's analytics and UX guarantees.
