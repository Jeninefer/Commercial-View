# Secrets Reference

This document enumerates the sensitive values that must be provisioned for local development and the GitHub Actions CI pipeline. Never commit actual secrets to the repository—store them as environment variables or GitHub encrypted secrets instead.

## Runtime & Integration Secrets
| Name | Where it is used | Description |
| ---- | ---------------- | ----------- |
| `LOOKER_BASE_URL` | Python backend (`src/looker_client.py`, CI pipeline) | Base URL of the Looker instance leveraged for analytics.
| `LOOKER_CLIENT_ID` | Python backend (`src/looker_client.py`, CI pipeline) | OAuth client ID for authenticating with Looker.
| `LOOKER_CLIENT_SECRET` | Python backend (`src/looker_client.py`, CI pipeline) | OAuth client secret paired with the Looker client ID.
| `FIGMA_TOKEN` | Python backend (`src/figma_client.py`, CI pipeline) | Personal access token required to interact with the Figma API.

## CI/CD Specific Secrets
| Name | Purpose |
| ---- | ------- |
| `CI_DEPLOY_SSH_KEY` | Optional private SSH key allowing the CI workflow to pull private dependencies or perform deployment operations over SSH. Provide the key in OpenSSH format without a passphrase. |

## Management Guidance
- Populate `.env` locally using `.env.example` as a template. All Looker and Figma related values must be set before running the backend locally or inside CI.
- In GitHub, navigate to **Settings → Secrets and variables → Actions** and create repository-level secrets for each of the names listed above. The CI workflow (`.github/workflows/ci.yml`) will automatically consume them when present.
- Rotate credentials regularly and update the corresponding GitHub secrets immediately after rotation.
- If the optional `CI_DEPLOY_SSH_KEY` is provided, ensure the corresponding public key is registered with any target systems (e.g., deployment servers or private Git hosts).
