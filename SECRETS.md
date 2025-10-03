# Secrets Management

This document describes all secrets and API keys required for the Commercial-View project.

## Required Secrets

### GitHub Actions Secrets

The following secrets must be configured in GitHub repository settings (Settings > Secrets and variables > Actions):

#### CI/CD Secrets

- `DEPLOY_VISUAL_CI_KEY`: SSH deploy key for accessing the Dashboard repository during CI runs

#### SonarQube

- `SONAR_TOKEN`: Authentication token for SonarQube server
- Configure in `sonar-project.properties` or as environment variable

### Application Secrets

These secrets should be configured in your local `.env` file (never commit this file):

#### Figma Integration

- `FIGMA_ACCESS_TOKEN`: Personal access token from Figma account settings
- `FIGMA_FILE_KEY`: File key from Figma file URL

**How to get Figma tokens:**
1. Go to Figma account settings
2. Navigate to "Personal access tokens"
3. Create a new token with appropriate scopes
4. Copy the token immediately (it won't be shown again)

#### Google Gemini AI

- `GEMINI_API_KEY`: API key from Google AI Studio
- `GEMINI_PROJECT_ID`: Google Cloud project ID

**How to get Gemini API key:**
1. Visit https://makersuite.google.com/app/apikey
2. Create a new API key
3. Copy the key for use in your `.env` file

#### Google Cloud Platform

- `GOOGLE_CLOUD_PROJECT_ID`: GCP project identifier
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to service account JSON file
- `GOOGLE_API_KEY`: Google Cloud API key

**How to set up Google Cloud credentials:**
1. Go to Google Cloud Console
2. Create a service account
3. Download the JSON credentials file
4. Store securely and reference the path in `GOOGLE_APPLICATION_CREDENTIALS`

#### OpenAI

- `OPENAI_API_KEY`: API key from OpenAI platform
- `OPENAI_ORGANIZATION_ID`: Organization ID (if applicable)

**How to get OpenAI API key:**
1. Visit https://platform.openai.com/api-keys
2. Create a new secret key
3. Copy the key immediately (it won't be shown again)

#### HubSpot

- `HUBSPOT_API_KEY`: HubSpot API key
- `HUBSPOT_ACCESS_TOKEN`: Private app access token
- `HUBSPOT_PORTAL_ID`: HubSpot portal/account ID

**How to get HubSpot credentials:**
1. Log in to HubSpot
2. Navigate to Settings > Integrations > Private Apps
3. Create a new private app
4. Copy the access token

## Setting Up Secrets

### Local Development

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and replace placeholder values with actual credentials

3. Verify `.env` is in `.gitignore` (it already is)

### GitHub Actions

1. Go to repository Settings
2. Navigate to Secrets and variables > Actions
3. Click "New repository secret"
4. Add each required secret

### SonarQube

1. Log in to your SonarQube server
2. Generate a token in My Account > Security
3. Add the token to GitHub secrets or local environment

## Security Best Practices

### DO

✅ Use environment variables for all secrets
✅ Rotate keys regularly (quarterly recommended)
✅ Use separate keys for development, staging, and production
✅ Limit key permissions to minimum required
✅ Enable audit logging where available
✅ Use secret management services (AWS Secrets Manager, Azure Key Vault, etc.) in production

### DON'T

❌ Never commit secrets to version control
❌ Never share secrets in chat, email, or documentation
❌ Never log secrets to console or files
❌ Never use production secrets in development
❌ Never reuse the same secret across multiple services
❌ Never embed secrets in client-side code

## Secret Rotation

When rotating secrets:

1. Generate new credentials
2. Update in all environments simultaneously
3. Test that services still work
4. Revoke old credentials
5. Document the rotation in change log

## Monitoring

- Monitor API usage for anomalies
- Set up alerts for unusual activity
- Review access logs regularly
- Track secret age and rotate before expiration

## Incident Response

If a secret is compromised:

1. **Immediately revoke** the compromised secret
2. **Generate new** credentials
3. **Update** all environments
4. **Notify** team and stakeholders
5. **Investigate** how the compromise occurred
6. **Document** the incident and lessons learned

## Compliance

Ensure secrets management complies with:

- GDPR (if handling EU data)
- SOC 2 requirements
- Industry-specific regulations
- Company security policies

## Tools

Recommended tools for secret management:

- **Development**: direnv, dotenv
- **CI/CD**: GitHub Secrets, GitLab CI/CD variables
- **Production**: AWS Secrets Manager, Azure Key Vault, HashiCorp Vault
- **Scanning**: git-secrets, truffleHog, GitHub secret scanning

## Support

For questions about secrets management:

1. Check this documentation first
2. Review service-specific documentation (links in `.env.example`)
3. Contact the security team
4. Create an issue in the repository (without including sensitive information)

## References

- [Figma API Documentation](https://www.figma.com/developers/api)
- [Google Gemini Documentation](https://ai.google.dev/docs)
- [Google Cloud Documentation](https://cloud.google.com/docs)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [HubSpot API Documentation](https://developers.hubspot.com/)
