# API Reference

[⬅ Documentation Hub](index.md) · [Quickstart Guide](quickstart.md)

This document details the FastAPI endpoints exposed by Commercial View. Use it alongside the generated Swagger docs for comprehensive integration guidance.

## Base Information

- **Base URL (local):** `http://localhost:8000`
- **Authentication:** Not enforced by default. Configure API gateways or proxies for production auth.
- **Content Type:** JSON (`application/json`)

## Endpoints

### `GET /`

Returns a welcome message.

```json
{
  "message": "Welcome to the Commercial View API"
}
```

### `GET /loan-data`

Returns loan records loaded via `CommercialViewPipeline`.

- **Success (200):** Array of loan objects.
- **Fallback:** Provides stub data when datasets are unavailable.

```json
[
  {
    "Customer ID": "C001",
    "Amount": 1000,
    "Status": "Active"
  }
]
```

### `GET /payment-schedule`

Returns repayment schedules.

```json
[
  {
    "Customer ID": "C001",
    "Due Date": "2024-01-01",
    "Total Payment": 100
  }
]
```

### `GET /historic-real-payment`

Historical payments aggregated from the pipeline.

- Includes `Payment Date` and `True Principal Payment` columns.

### `GET /schema/{name}`

Retrieves schema metadata for supported datasets (`loan_data`, `payment_schedule`, `historic_real_payment`).

```json
{
  "name": "loan_data",
  "columns": ["Customer ID", "Amount", "Status"]
}
```

### `GET /customer-data`

Placeholder endpoint returning an empty array. Extend this when customer data integration is completed.

### `GET /collateral`

Placeholder endpoint returning an empty array. Intended for collateral details once sourced.

### `GET /executive-summary`

Returns a stub object reserved for executive dashboards.

```json
{
  "portfolio_overview": {}
}
```

### `GET /portfolio-metrics`

Aggregates outstanding balances, active clients, and status metadata.

```json
{
  "portfolio_outstanding": 3000,
  "active_clients": 2,
  "status": "success"
}
```

When real data is loaded, metrics are computed using pandas aggregations from `CommercialViewPipeline`.

### `GET /health`

System health status including dataset availability flags.

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "datasets_available": {
    "loan_data": true,
    "payment_schedule": true,
    "historic_real_payment": false
  }
}
```

## Error Handling

- All unexpected exceptions return `500` with `{"detail": "Internal server error occurred."}`.
- Missing schema names return `404` with `{"detail": "schema not found"}`.

## Versioning

- API version is tracked in `run.py` (`app.version`). Follow the [Versioning Policy](versioning.md) for changes.

## Extending the API

1. Define new routes in `src/api.py` or directly in `run.py`.
2. Ensure responses are serializable and documented here.
3. Add automated tests for the new contract.
4. Update [Operations Runbook](operations-runbook.md) with monitoring or alerting implications.
