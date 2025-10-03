# Commercial-View

Financial Dashboard for loan portfolio analysis and risk management.

## Overview

Commercial-View is a comprehensive platform for monitoring Principal KPIs and financial metrics.

## Features

- **AI Integration**: Support for Google Gemini, OpenAI, and Google Cloud AI services
- **Design Integration**: Figma API integration for design workflows
- **CRM Integration**: HubSpot integration for customer relationship management
- **Code Quality**: SonarQube integration for continuous code quality monitoring
- **CI/CD**: Automated testing and deployment workflows

## Setup

### Prerequisites

- Python 3.9 or higher
- Node.js (for optional tooling)
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Jeninefer/Commercial-View.git
   cd Commercial-View
   ```

2. Copy the environment template and configure your credentials:
   ```bash
   cp .env.example .env
   ```

3. Edit `.env` and add your API keys and secrets for:
   - Figma
   - Google Gemini
   - Google Cloud Platform
   - OpenAI
   - HubSpot

### Environment Variables

All sensitive configuration should be stored in environment variables. See `.env.example` for the complete list of required variables.

**Important**: Never commit the `.env` file to version control.

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- [AI Services Integration](docs/integrations/ai-services.md)
- [Meta Business Integration](docs/integrations/meta-business.md)
- [Claude Code Setup](docs/setup/claude-code-setup.md)
- [API Documentation](docs/api/openapi-plant-store.json)

## CI/CD

The project uses GitHub Actions for continuous integration:

- **SSH Checkout Test**: Validates SSH access and runs tests
- See `.github/workflows/ci-ssh-checkout.yml` for details

## Code Quality

SonarQube is configured for code quality monitoring. Configuration is in `sonar-project.properties`.

To run SonarQube analysis:
```bash
sonar-scanner
```

## Security

- All secrets are managed via environment variables
- `.gitignore` is configured to exclude sensitive files
- Follow the security best practices documented in the integration guides

## Contributing

1. Create a feature branch
2. Make your changes
3. Ensure tests pass
4. Submit a pull request

## License

This project is proprietary software. All rights reserved.

## Contact

For questions or support, please contact the project maintainers.
