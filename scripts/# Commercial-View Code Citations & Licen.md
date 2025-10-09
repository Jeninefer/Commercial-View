# Commercial-View Code Citations & License Compliance

This document tracks third-party code usage and license compliance for the Commercial-View commercial lending platform.

## Project License
**Commercial-View Platform**: MIT License
**Repository**: https://github.com/Jeninefer/Commercial-View
**Copyright**: 2024 Commercial-View Contributors

---

## Third-Party Code Citations

### Development Tooling Configuration
**Description**: Standard ESLint and Prettier configuration for JavaScript/TypeScript projects
**License**: MIT Compatible
**Usage**: Development tooling only (not included in production builds)
**Source**: Community best practices for linting and formatting

```json
{
  "scripts": {
    "lint": "eslint . --ext .js,.jsx,.ts,.tsx",
    "lint:fix": "eslint . --ext .js,.jsx,.ts,.tsx --fix",
    "format": "prettier --write \"**/*.{js,jsx,ts,tsx,json,md}\"",
    "format:check": "prettier --check \"**/*.{js,jsx,ts,tsx,json,md}\""
  }
}
```

**Modifications**: Adapted for Commercial-View project structure and commercial lending platform requirements.

---

## Commercial-View Original Components

The following components are original work developed specifically for the Commercial-View platform:

### Core Commercial Lending Engine
- **Payment Processing System** (`src/payment_processor.py`)
- **Days Past Due (DPD) Calculator** (`src/dpd/`)
- **Commercial Loan Risk Assessment** (`src/risk/`)
- **KPI Generation and Analytics** (`src/kpi/`)
- **Portfolio Management Tools** (`src/portfolio/`)

### Frontend Dashboard
- **Commercial Lending Dashboard** (`frontend/src/`)
- **Real-time Analytics Components** (`frontend/src/components/`)
- **Interactive Data Visualizations** (`frontend/src/charts/`)

### Infrastructure & Scripts
- **Environment Management** (`scripts/Activate-Project.ps1`)
- **Data Upload Pipeline** (`scripts/upload_to_drive.py`)
- **Figma Integration Tools** (`scripts/fix_figma_token.py`)
- **Complete Resolution System** (`execute_complete_resolution.py`)

---

## License Compliance Summary

| Component Type | License | Status | Notes |
|---------------|---------|--------|-------|
| ESLint/Prettier Config | MIT | ✅ Compatible | Development tools only |
| Core Platform | MIT | ✅ Original Work | Commercial-View proprietary |
| Dependencies | MIT/BSD | ✅ Compatible | Standard npm/pip packages |

### License Compatibility
- **MIT License**: Fully compatible with Commercial-View's MIT license
- **Development Tools**: Standard configurations not included in production
- **No GPL Dependencies**: Avoided GPL code to maintain license compatibility

---

## Attribution Notes

### Standard Dependencies
All third-party libraries (FastAPI, React, pandas, etc.) are properly attributed through their respective package managers (npm, pip) and maintain their original licenses.

### Configuration Templates
The ESLint/Prettier configuration represents standard industry practices and has been customized for Commercial-View's specific requirements.

---

## Commercial Platform Disclaimer

Commercial-View contains proprietary algorithms and business logic for:
- Commercial loan origination and pricing
- Risk assessment and portfolio analytics
- Regulatory compliance and reporting
- Real-time KPI monitoring and alerts

These components represent original work and intellectual property of the Commercial-View project.

---

**Document Version**: 1.0
**Last Updated**: December 2024
**Review Schedule**: Quarterly license compliance review
**Maintainer**: Commercial-View Development Team
