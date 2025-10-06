# Operations Runbook

[⬅ Documentation Hub](index.md) · [Testing & Quality Strategy](testing-and-quality.md)

This runbook consolidates operational procedures for Commercial View across environments.

## Service Overview

- **Primary Service:** FastAPI application served by Uvicorn or Gunicorn.
- **Data Dependencies:** CSV datasets under `data/` or mounted volumes in production.
- **Key Scripts:** `server_control.py`, `scripts/uvicorn_manager.py`, `scripts/debug_server.py`.

## Monitoring

| Signal | Source | Action |
|--------|--------|--------|
| Availability | `/health` endpoint, uptime probes | Investigate failed checks, inspect logs, verify dataset mounts. |
| Performance | Latency metrics via `metrics_registry.py` | Scale horizontally or optimize heavy computations in `CommercialViewPipeline`. |
| Errors | Structured logs (`logging`), CI pipeline notifications | Triage stack traces, reproduce locally, patch and redeploy. |

## On-call Checklist

1. Validate incident details (timestamp, environment, impact).
2. Check `/health` and critical API endpoints.
3. Review recent deployments or configuration changes.
4. Consult [Secrets Management](secrets-management.md) if token issues are suspected.
5. Coordinate with data engineering when dataset freshness is in question.

## Standard Operating Procedures

### Deployment

1. Confirm tests pass (`pytest -q`).
2. Build container image (if applicable) and push to registry.
3. Apply infrastructure manifests (Terraform/Helm) with updated image tag.
4. Monitor `/health` and dashboards for 15 minutes post-deploy.

### Scaling

- **Horizontal:** Increase replica count in orchestrator (Kubernetes/ECS) when CPU or latency thresholds exceed SLOs.
- **Vertical:** Allocate larger instance types for analytics-heavy jobs; update resource requests/limits accordingly.

### Backup & Restore

- Version control raw datasets in secure object storage.
- For critical CSVs, schedule nightly snapshots with checksums.
- To restore, replace corrupted files and restart pipeline services.

### Incident Logging

- Record incident timeline, resolution steps, and follow-ups in the operations tracker.
- Update relevant documentation (this runbook, [Testing & Quality Strategy](testing-and-quality.md), etc.).

## Troubleshooting Matrix

| Symptom | Diagnostic Steps | Resolution |
|---------|------------------|------------|
| API returns 500 | Inspect logs (`uvicorn` output), rerun failing request with debug logging enabled. | Patch offending module, add regression test. |
| Missing datasets | Check `COMMERCIAL_VIEW_DATA_PATH` environment variable. | Mount correct volume, re-run `CommercialViewPipeline.load_all_datasets()`. |
| Port conflicts | Run `python server_control.py --check-only --port <PORT>`. | Terminate rogue process (`--kill-existing`) or choose different port. |
| High latency | Profile pipeline computations (`cProfile`, sampling profilers). | Optimize DataFrame operations or precompute heavy metrics. |

## Change Management

- Follow GitHub Flow: feature branches, PR reviews, CI enforcement.
- Ensure documentation updates accompany functional changes.
- Update [Changelog Archive](CLOSED_PRS_ARCHIVE.md) or release notes as needed.

## Disaster Recovery

1. Declare incident severity and assemble response team.
2. Restore from last known good dataset snapshot.
3. Rebuild containers and redeploy services.
4. Validate functionality using the [Quickstart Guide](quickstart.md) smoke steps.
5. Conduct post-incident review within 48 hours.

## Related Documents

- [Secrets Management](secrets-management.md)
- [Testing & Quality Strategy](testing-and-quality.md)
- [Performance SLOs](performance_slos.md)
