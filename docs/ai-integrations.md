# AI Integrations

[⬅ Documentation Hub](index.md) · [Implementation Guide](implementation-guide.md)

Commercial View integrates with AI tooling to accelerate analysis and provide intelligent workflows. This guide summarizes existing integrations and outlines safe extension practices.

## Existing Integrations

| Component | Module | Purpose |
|-----------|--------|---------|
| Model Context Protocol (MCP) | `mcp-servers.md`, `scripts/start_figma_mcp.py` | Provides AI-assisted design workflows via Figma MCP server. |
| Feature Engineering | `src/feature_engineer.py` | Uses heuristics and ML-ready feature pipelines to enrich loan datasets for modeling. |
| Portfolio Optimization | `src/portfolio_optimizer.py` | Supports algorithmic optimization that can be augmented with ML-driven scoring. |
| Evergreen Analytics | `src/evergreen_analytics.py` | Supplies AI-friendly transformations for evergreen lending scenarios. |

## Design Principles

1. **Transparency:** Log prompts and responses (redacting sensitive data) for auditing.
2. **Security:** AI integrations must follow the [Secrets Management](secrets-management.md) guidance—tokens are never hard-coded.
3. **Human-in-the-loop:** Critical decisions (credit approvals, pricing) require analyst confirmation before deployment.
4. **Modularity:** Encapsulate AI logic in dedicated modules to avoid contaminating deterministic analytics with stochastic behaviour.

## Adding a New AI Workflow

1. **Scope the Use Case** – Identify target dataset and desired outcome. Validate that data residency or compliance policies permit AI usage.
2. **Provision Credentials** – Follow the [Secrets Management Guide](secrets-management.md) to store API keys or tokens.
3. **Implement Client** – Create a new module under `src/` or `scripts/`. Use dependency injection to allow unit tests to stub remote calls.
4. **Guardrails** – Add schema validation and response sanity checks. Consider implementing rate limiting or fallback behaviour.
5. **Telemetry** – Emit structured logs and metrics (`metrics_registry.py`) to monitor success rates and latency.
6. **Document & Train** – Update this guide with usage instructions and inform operations/on-call teams through the [Operations Runbook](operations-runbook.md).

## Prompt Safety Checklist

- Remove personally identifiable information (PII) before sending payloads.
- Use deterministic prompts with explicit instructions to avoid undesirable outputs.
- Cap response length and enforce JSON schemas when parsing AI output.
- Store prompts in version control for reproducibility.

## Testing AI Integrations

- Use `pytest` with fixtures that mock external services.
- Provide canned responses to validate parsing and fallback logic.
- Include end-to-end smoke tests that run only in environments with credentials available (guarded by markers).
- Document testing strategy updates in [Testing & Quality Strategy](testing-and-quality.md).

## Related Documents

- [Implementation Guide](implementation-guide.md)
- [Secrets Management Guide](secrets-management.md)
- [Operations Runbook](operations-runbook.md)
