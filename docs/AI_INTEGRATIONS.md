# AI Integrations

The Commercial View platform provides a modular AI layer that powers forecasting,
anomaly detection, and executive reporting. This document explains how to configure
the provider clients, orchestrate them through the service layer, and expose
capabilities to downstream consumers.

## Provider overview

The `src/ai` package introduces typed clients for the following providers:

| Provider   | Environment variables                                                 | Purpose |
| ---------- | --------------------------------------------------------------------- | ------- |
| OpenAI     | `OPENAI_API_KEY`, optional `OPENAI_MODEL`, optional `OPENAI_BASE_URL`  | Primary LLM narrative generation |
| Gemini     | `GEMINI_API_KEY`, optional `GEMINI_MODEL`, optional `GEMINI_API_BASE`  | Backup LLM with strong reasoning |
| Anthropic  | `ANTHROPIC_API_KEY`, optional `ANTHROPIC_MODEL`, optional `ANTHROPIC_API_BASE` | Safety-first LLM for governance |
| HubSpot    | `HUBSPOT_PRIVATE_APP_TOKEN`, optional `HUBSPOT_API_BASE`               | CRM enrichment / context injection |

Each client validates its credentials at instantiation time. Missing credentials
result in a `ProviderAuthenticationError`, ensuring issues surface early during
application boot.

If no providers are configured, the application automatically falls back to a
`LocalEchoClient` that produces deterministic, non-networked responses. This mode
is safe for development and automated testing where secrets are not available.

## Service architecture

The service layer (`src/ai/services.py`) composes provider clients into
business-friendly abstractions:

* `PredictionService` – produces numeric forecasts and AI-generated narratives
* `AnomalyDetectionService` – flags statistical outliers and narrates their drivers
* `ExecutiveSummaryService` – crafts leadership-ready summaries referencing KPI maps

All services rely on `AIServiceContainer`, which resolves the best available
provider according to the priority (`openai`, `anthropic`, `gemini`, `hubspot`).
Custom containers can be supplied for testing or advanced routing requirements.

## FastAPI endpoints

`src/api.py` exposes the services through versionless HTTP endpoints:

* `POST /analytics/predictions` – accepts historical values and forecast horizon
* `POST /analytics/anomalies` – accepts a time-series payload to analyse
* `POST /analytics/executive-summary` – accepts KPI metrics and optional sentiment
* `GET /executive-summary` – returns a baseline executive summary using default KPIs

Responses leverage Pydantic schemas to guarantee consistent, typed payloads.

## Local development

1. Export or inject the relevant API keys for the providers you intend to use
   (e.g. `export OPENAI_API_KEY=...`).
2. Start the API: `uvicorn src.api:app --reload`.
3. Exercise endpoints via curl/Postman or the included FastAPI docs at
   `http://localhost:8000/docs`.

When no provider keys are present, the API operates in echo mode. This allows for
front-end development and integration tests without leaking secrets.

## Testing strategy

Unit and integration tests (`tests/test_ai_services.py`) rely on a stub provider
that emulates LLM responses. This approach ensures deterministic assertions and
keeps CI pipelines air-gapped from external vendors.

## Security considerations

* **Secrets management** – API keys should be supplied via your secrets manager or
  container orchestration platform. Never commit them to source control.
* **Request logging** – avoid logging raw prompts or responses that could contain
  sensitive financial data.
* **Provider isolation** – network access can be restricted per provider when running
  in production; the clients are modular so unused providers need not be deployed.
* **Fallback behaviour** – the `LocalEchoClient` explicitly avoids outbound network
  calls, preventing accidental data exfiltration in lower environments.

## Observability

Each client exposes a `healthcheck()` method summarising readiness state. The
`AIServiceContainer` aggregates these results, enabling future health endpoints or
self-diagnostics dashboards.
