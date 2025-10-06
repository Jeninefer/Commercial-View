# Secrets Management Guide

[⬅ Documentation Hub](index.md) · [Operations Runbook](operations-runbook.md)

This guide explains how to manage credentials, tokens, and sensitive configuration across environments.

## Principles

1. **Least Privilege:** Provision credentials with the minimal scope required.
2. **Separation of Duties:** Production secrets must never be reused in development or staging.
3. **Auditability:** Every secret rotation or access grant should be traceable through tickets or Git history.
4. **Automation First:** Prefer secrets managers (AWS Secrets Manager, Azure Key Vault, HashiCorp Vault) over manual distribution.

## Secret Inventory

| Secret | Description | Scope | Storage |
|--------|-------------|-------|---------|
| `ALLOWED_ORIGINS` | Comma-separated list of domains permitted by CORS. | API | Environment variable / deployment config. |
| `COMMERCIAL_VIEW_DATA_PATH` | Overrides default dataset directory. | API & analytics scripts | `.env` for local, secrets manager in cloud. |
| `PRICING_CONFIG_PATH`, `DPD_POLICY_PATH`, `COLUMN_MAPS_PATH` | Paths to YAML configuration bundles loaded by scripts. | Pipelines | Secrets manager or deployment manifest. |
| `FIGMA_PERSONAL_ACCESS_TOKEN` | Token used by `scripts/start_figma_mcp.py` for design integrations. | Tooling | Secret manager with rotation policy. |
| `GOOGLE_APPLICATION_CREDENTIALS` | (If enabled) Service account for `google_drive_exporter`. | Integrations | GCP Secret Manager / Vault. |

## Local Development

1. Copy `.env.example` (create one if necessary) to `.env.local` and populate with non-production secrets.
2. Use `direnv` or `python -m dotenv` to load variables before running commands.
3. Never commit `.env*` files containing secrets. Add them to `.gitignore`.

Example `.env.local`:

```ini
ALLOWED_ORIGINS=http://localhost:3000
COMMERCIAL_VIEW_DATA_PATH=/Users/me/projects/Commercial-View/data
PRICING_CONFIG_PATH=config/pricing_config.yml
DPD_POLICY_PATH=config/dpd_policy.yml
COLUMN_MAPS_PATH=config/column_maps.yml
```

## CI/CD Pipelines

- Store secrets in the CI provider (GitHub Actions secrets, GitLab CI variables, etc.).
- Inject secrets at runtime using masked variables. Avoid printing values to logs.
- Validate that `COMMERCIAL_VIEW_ROOT` and dependent paths resolve within the CI workspace.

## Rotation Playbook

1. Identify secret and stakeholders.
2. Generate a new credential with overlapping validity (do not revoke the old one immediately).
3. Update infrastructure-as-code or deployment manifests to reference the new secret.
4. Redeploy services.
5. Validate functionality (hit `/health`, run smoke tests).
6. Revoke the old credential and document the change (ticket + commit message).

## Incident Response

If a secret leaks:

1. Rotate immediately following the playbook above.
2. Invalidate exposed tokens, revoke sessions.
3. Audit access logs for suspicious activity.
4. File an incident report and capture remediation steps in the [Operations Runbook](operations-runbook.md).

## Related Documents

- [AI Integrations](ai-integrations.md) – includes AI-specific token guidance.
- [Security Constraints](security_constraints.md)
- [Operations Runbook](operations-runbook.md)
