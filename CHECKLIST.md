# Setup Validation Checklist

Use this checklist to verify your Commercial-View setup is complete and correct.

## ✅ Repository Setup

- [ ] Repository cloned successfully
- [ ] All files are present (13 files total)
- [ ] `.git` directory exists
- [ ] No uncommitted changes in working directory

## ✅ Configuration Files

### Environment Configuration
- [ ] `.env.example` file exists (913 bytes)
- [ ] `.env` file created from `.env.example`
- [ ] `.env` file is in `.gitignore`
- [ ] `.gitignore` file configured (718 bytes)

### CI/CD Configuration
- [ ] `.github/workflows/ci-ssh-checkout.yml` exists (1.6K)
- [ ] Workflow triggers configured (push, PR, manual)
- [ ] Python 3.9 specified
- [ ] All workflow steps present

### Code Quality Configuration
- [ ] `sonar-project.properties` exists (799 bytes)
- [ ] SonarQube project key configured
- [ ] Code exclusions defined
- [ ] Coverage paths configured

## ✅ Documentation Files

### Root Documentation
- [ ] `README.md` updated (2.4K) - Project overview
- [ ] `SECRETS.md` created (5.2K) - Secrets management guide
- [ ] `IMPLEMENTATION.md` created (4.2K) - Implementation summary
- [ ] `ARCHITECTURE.md` created (11K) - System architecture
- [ ] `QUICKSTART.md` created (5.0K) - Quick start guide

### Integration Documentation
- [ ] `docs/integrations/ai-services.md` (4.2K) - AI services guide
- [ ] `docs/integrations/meta-business.md` (1.4K) - Meta Business guide

### Setup Documentation
- [ ] `docs/setup/claude-code-setup.md` (2.9K) - Claude Code setup

### API Documentation
- [ ] `docs/api/openapi-plant-store.json` (5.1K) - OpenAPI spec

## ✅ API Keys Configuration

### Figma Integration
- [ ] `FIGMA_ACCESS_TOKEN` set in `.env`
- [ ] `FIGMA_FILE_KEY` set in `.env`
- [ ] Token has valid permissions
- [ ] File key is accessible

### Google Gemini
- [ ] `GEMINI_API_KEY` set in `.env`
- [ ] `GEMINI_PROJECT_ID` set in `.env`
- [ ] API key is active
- [ ] Project ID is correct

### Google Cloud Platform
- [ ] `GOOGLE_CLOUD_PROJECT_ID` set in `.env`
- [ ] `GOOGLE_APPLICATION_CREDENTIALS` path set in `.env`
- [ ] Service account JSON file exists
- [ ] `GOOGLE_API_KEY` set in `.env`
- [ ] Required APIs enabled in GCP

### OpenAI
- [ ] `OPENAI_API_KEY` set in `.env`
- [ ] `OPENAI_ORGANIZATION_ID` set in `.env` (if applicable)
- [ ] API key is active
- [ ] Organization has credits/quota

### HubSpot
- [ ] `HUBSPOT_API_KEY` set in `.env`
- [ ] `HUBSPOT_ACCESS_TOKEN` set in `.env`
- [ ] `HUBSPOT_PORTAL_ID` set in `.env`
- [ ] Token has required scopes

## ✅ GitHub Configuration

### Repository Secrets
- [ ] `DEPLOY_VISUAL_CI_KEY` added to GitHub secrets
- [ ] `SONAR_TOKEN` added to GitHub secrets (if using SonarQube)

### Repository Settings
- [ ] Branch protection enabled (optional)
- [ ] Actions enabled
- [ ] Dependabot enabled (optional)

## ✅ Security Validation

### File Permissions
- [ ] `.env` file not tracked by git
- [ ] `.env` file has secure permissions (600)
- [ ] No secrets in committed files
- [ ] `.gitignore` includes all sensitive patterns

### API Key Security
- [ ] All API keys are valid
- [ ] Keys are not shared or exposed
- [ ] Keys have minimal required permissions
- [ ] Separate keys for dev/staging/prod (recommended)

## ✅ Testing & Validation

### Environment Variables
Run these checks to verify environment variables are loaded:

```bash
# Check if .env file exists
test -f .env && echo "✅ .env exists" || echo "❌ .env missing"

# Check if key variables are set (without showing values)
python3 << 'EOF'
import os
keys = ['GEMINI_API_KEY', 'OPENAI_API_KEY', 'FIGMA_ACCESS_TOKEN', 'HUBSPOT_API_KEY']
for key in keys:
    status = '✅' if os.getenv(key) else '❌'
    print(f"{status} {key}: {'SET' if os.getenv(key) else 'MISSING'}")
EOF
```

### Integration Tests
- [ ] Figma API connection test passed
- [ ] Gemini API connection test passed
- [ ] OpenAI API connection test passed
- [ ] HubSpot API connection test passed
- [ ] Google Cloud API connection test passed

### CI/CD Tests
- [ ] GitHub Actions workflow can be triggered manually
- [ ] SSH keys are configured correctly
- [ ] Dependencies install successfully
- [ ] Tests run successfully (if applicable)

## ✅ Documentation Review

### Read Key Documentation
- [ ] Read `README.md` for project overview
- [ ] Read `QUICKSTART.md` for setup instructions
- [ ] Read `SECRETS.md` for security best practices
- [ ] Review `ARCHITECTURE.md` for system understanding
- [ ] Check `IMPLEMENTATION.md` for implementation details

### Service-Specific Documentation
- [ ] Review AI services integration guide
- [ ] Review Meta Business integration guide (if needed)
- [ ] Review Claude Code setup guide (if needed)

## ✅ Code Quality Setup

### SonarQube Configuration
- [ ] SonarQube server URL configured
- [ ] SonarQube token configured
- [ ] Project key matches repository
- [ ] Exclusions are appropriate
- [ ] Coverage paths are correct

### Local Quality Checks
- [ ] Linters configured (if applicable)
- [ ] Formatters configured (if applicable)
- [ ] Pre-commit hooks installed (optional)

## ✅ Operational Readiness

### Development Environment
- [ ] Can run application locally
- [ ] Can make API calls successfully
- [ ] Can access all integrated services
- [ ] Logs show no credential errors

### Monitoring Setup
- [ ] API usage monitoring configured (recommended)
- [ ] Error tracking setup (recommended)
- [ ] Alert notifications configured (recommended)

### Backup & Recovery
- [ ] Credentials backed up securely
- [ ] Recovery procedure documented
- [ ] Backup keys available for rotation

## Validation Commands

Run these commands to validate your setup:

```bash
# 1. Check repository structure
cd /path/to/Commercial-View
find . -type f ! -path './.git/*' | wc -l
# Expected: 13 files

# 2. Verify .gitignore is working
git status
# Expected: .env should NOT appear in untracked files

# 3. Check environment variables are loadable
python3 -c "from dotenv import load_dotenv; load_dotenv(); import os; print('✅ Environment loaded')" 2>/dev/null || echo "Install python-dotenv: pip install python-dotenv"

# 4. Verify GitHub Actions workflow syntax
cd .github/workflows
grep -q "DEPLOY_VISUAL_CI_KEY" ci-ssh-checkout.yml && echo "✅ SSH key reference found" || echo "❌ SSH key reference missing"

# 5. Check SonarQube config
grep -q "sonar.projectKey=Jeninefer_Dashboard" ../../sonar-project.properties && echo "✅ SonarQube configured" || echo "❌ SonarQube config issue"
```

## Troubleshooting

If any checks fail, refer to:

1. **Configuration issues**: Check `QUICKSTART.md`
2. **Security issues**: Check `SECRETS.md`
3. **Integration issues**: Check `docs/integrations/ai-services.md`
4. **CI/CD issues**: Check `.github/workflows/ci-ssh-checkout.yml`
5. **Architecture questions**: Check `ARCHITECTURE.md`

## Sign Off

When all items are checked:

- [ ] All configuration complete
- [ ] All documentation reviewed
- [ ] All integrations tested
- [ ] Security measures validated
- [ ] Ready for development

**Date Completed**: _____________

**Validated By**: _____________

---

## Quick Reference

**Total Files**: 13
**Documentation Pages**: 8
**Configuration Files**: 5
**Integrations**: 5 (Figma, Gemini, Google Cloud, OpenAI, HubSpot)
**CI/CD Workflows**: 1

## Support

If you need help:
1. Review the documentation in the `docs/` directory
2. Check the troubleshooting sections
3. Create an issue on GitHub (without sensitive information)
4. Contact the development team
