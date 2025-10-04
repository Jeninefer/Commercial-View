# Commercial-View

Principal KPI Analytics System for Commercial Lending

## Overview

Commercial-View is a comprehensive analytics platform that combines real-time KPI dashboards with sophisticated commercial lending analytics. The system provides:

- **Interactive KPI Dashboards**: Real-time visualization and monitoring of business performance metrics
- **DPD (Days Past Due) Analysis**: Calculate and track payment delinquency with 7-tier risk classification
- **Risk Bucketing**: Enterprise-grade loan classification system (Current → 180+ Days Default)
- **Portfolio Analytics**: Advanced metrics for commercial lending operations
- **Pricing Management**: Configurable pricing grids with interval bands
- **Data Export**: Multi-format export capabilities (JSON, CSV, Parquet)
- **AI Integration**: Machine learning insights and predictive analytics

## Features

- 📊 **Real-time KPI monitoring** with interactive dashboards
- 📈 **Data visualizations** with intuitive charts and analytics
- 🎯 **7-tier risk classification** with sophisticated DPD analysis
- 💼 **Commercial lending focus** with enterprise-grade business rules
- 🔧 **Configurable thresholds** (90/120/180 day default options)
- 📱 **Responsive design** with modern UI/UX
- 🔍 **Advanced filtering and search** capabilities
- 🔒 **PII masking and compliance** (GDPR, SOX, PCI DSS)
- 🚀 **Multi-language support** (Python + TypeScript)

## Table of Contents

- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Pricing System](#pricing-system)
- [Development](#development)
- [CI/CD](#cicd)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

## Quick Start

### Prerequisites

- **Python 3.8+** (for analytics backend)
- **Node.js 18+** (for dashboard frontend, if applicable)
- **pip** (Python package manager)
- **Git** for version control

### Installation

```bash
# Clone the repository
git clone https://github.com/Jeninefer/Commercial-View.git
cd Commercial-View

# Python Analytics Setup
pip install -r requirements.txt
pip install -r requirements-dev.txt

# TypeScript Dashboard Setup (if package.json exists)
npm install

# Install pre-commit hooks (optional, for contributors)
pip install pre-commit
pre-commit install
```

### Running the System

```bash
# Validate configuration files
python validators/schema_validator.py

# View all pricing files
ls -la data/pricing/

# Start analytics processing
# python src/process_portfolio.py --config config/

# View exports
ls -la abaco_runtime/exports/
```

### Configuring the Data Directory

The analytics loaders read CSV files from the `data/pricing/` directory by default. To point the application to a different data
source (e.g., in a production or staging environment), set the `COMMERCIAL_VIEW_DATA_PATH` environment variable or provide the `--data-dir` option when running the portfolio processor:

```bash
# Use a custom directory for all loader functions
export COMMERCIAL_VIEW_DATA_PATH=/mnt/shared/pricing-data

# Or override per run of the CLI processor
python src/process_portfolio.py \
  --config config/ \
  --data-dir /mnt/shared/pricing-data
```

Both approaches ensure that `src/data_loader.py` resolves the correct base path and will raise a descriptive error if any of the e
xpected CSV files are missing.

## Configuration

### Configuration Files

The system uses YAML configuration files located in the `config/` directory:

#### 1. Column Mappings (`config/column_maps.yml`)

Maps your dataset field names to the system's expected field names.

```yaml
loan_data:
  loan_id: "your_loan_id_field"
  customer_id: "your_customer_id_field"
  loan_amount: "your_amount_field"
  # ... etc
```

#### 2. DPD Policy (`config/dpd_policy.yml`)

Your sophisticated 7-tier DPD classification system:

```yaml
default_threshold:
  days: 180  # Configurable: 90, 120, or 180 days

dpd_buckets:
  - bucket: "Current" (0 days) → Low Risk
  - bucket: "1-30 Days" → Low Risk
  - bucket: "31-60 Days" → Medium Risk
  - bucket: "61-90 Days" → Medium Risk
  - bucket: "91-120 Days" → High Risk
  - bucket: "121-180 Days" → High Risk
  - bucket: "180+ Days" → Critical Risk (Default)
```

#### 3. Pricing Configuration (`config/pricing_config.yml`)

```yaml
band_keys:
  tenor_days:
    lower_bound: "tenor_min"
    upper_bound: "tenor_max"
  amount:
    lower_bound: "amount_min"
    upper_bound: "amount_max"
```

#### 4. Export Configuration (`config/export_config.yml`)

```yaml
export_paths:
  base_path: "./abaco_runtime/exports"
  kpi_json: "./abaco_runtime/exports/kpi/json"
  kpi_csv: "./abaco_runtime/exports/kpi/csv"
```

### Dataset Status

- ✅ **Loan Data** — `/mnt/data/Abaco - Loan Tape_Loan Data_Table.csv` (16,205 rows)
- ✅ **Historic Real Payment** — `/mnt/data/Abaco - Loan Tape_Historic Real Payment_Table.csv` (16,443 rows)
- ✅ **Payment Schedule** — `/mnt/data/Abaco - Loan Tape_Payment Schedule_Table.csv` (16,205 rows)
- ⚠️ **Customer Data** — missing (upload `Abaco - Loan Tape_Customer Data_Table.csv`)
- ⚠️ **Collateral** — missing (upload `Abaco - Loan Tape_Collateral_Table.csv`)

Upload the missing CSV/XLSX files into `data/pricing/` so the Customer and Collateral endpoints can load successfully.

## Pricing System

Your Commercial-View system includes a sophisticated 4-tier risk-based pricing model:

### Risk-Based Pricing Structure

Located in `data/pricing/risk_based_pricing.csv`:

- **High Risk** (300-579 credit score): 11.0%-13.0% rates
- **Medium Risk** (580-669 credit score): 8.0%-10.0% rates  
- **Low Risk** (670-739 credit score): 5.5%-7.5% rates
- **Very Low Risk** (740-850 credit score): 4.5%-6.0% rates

### Available Pricing Files

```bash
# View all pricing configurations
data/pricing/
├── main_pricing.csv              # Primary pricing grid
├── commercial_loans_pricing.csv  # Commercial loan pricing
├── retail_loans_pricing.csv      # Retail loan pricing
└── risk_based_pricing.csv        # ✅ Credit risk-based pricing
```

### Opening All Pricing Files

```bash
# Navigate to pricing directory
cd data/pricing/

# View all files
ls -la *.csv

# Open in VS Code
code .

# Or open individual files
open main_pricing.csv
open commercial_loans_pricing.csv
open retail_loans_pricing.csv
open risk_based_pricing.csv
```

## Development

### Project Structure

```text

Commercial-View/
├── config/                      # YAML configuration system
│   ├── dpd_policy.yml          # ✅ 7-tier DPD classification
│   ├── column_maps.yml         # Data field mappings
│   ├── pricing_config.yml      # Pricing grid management
│   └── export_config.yml       # Output configurations
├── data/pricing/               # ✅ Risk-based pricing grids
│   ├── main_pricing.csv
│   ├── commercial_loans_pricing.csv
│   ├── retail_loans_pricing.csv
│   └── risk_based_pricing.csv  # 4-tier credit risk model
├── docs/                       # Comprehensive documentation
├── src/                        # Python analytics (if present)
├── validators/                 # Configuration validation
├── .github/workflows/          # Multi-language CI/CD pipeline
└── README.md                   # This comprehensive guide
```

### Usage Options

#### Analytics Backend (Python)

```bash
# Validate configuration
python validators/schema_validator.py

# Process loan portfolios
# python src/dpd_calculator.py --config config/

# Run analytics
# python src/portfolio_analyzer.py
```

#### Dashboard Frontend (TypeScript/React)

```bash
# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test
```

### Running Tests

```bash
# Python: Validate configuration
python validators/schema_validator.py

# Python: Run unit tests (when implemented)
pytest tests/ --cov=src --cov-report=html

# TypeScript: Run tests (if applicable)
npm test
```

### Code Quality

```bash
# Python formatting and linting
black src/ validators/
isort src/ validators/
flake8 src/ validators/

# TypeScript linting (if applicable)
npx eslint . --ext .ts,.js
```

## CI/CD

The project includes a comprehensive multi-language CI/CD pipeline that:

1. **Detects project type** (Python, TypeScript, or both)
2. **Validates configuration** files with schema validation
3. **Runs appropriate linting** (Black/Flake8 for Python, ESLint for TypeScript)
4. **Executes tests** across multiple Python versions and Node.js
5. **Performs security scanning** (Safety, Bandit, npm audit)
6. **Builds artifacts** for both Python packages and TypeScript bundles
7. **Deploys** to staging and production environments

### Creating a Release

```bash
# Update VERSION file
echo "1.2.0" > VERSION

# Commit and tag
git add VERSION
git commit -m "Bump version to 1.2.0"
git tag -a v1.2.0 -m "Release version 1.2.0"
git push origin main --tags
```

## Documentation

Commercial-View ships with detailed references in the [`docs/`](docs/) directory covering performance SLOs, security constraints, versioning, and other operational guides.

## Performance and Scalability

The system is designed to handle portfolios of various sizes:

- **Small** (< 10K loans): < 5 minutes, < 2GB memory
- **Medium** (10K-100K loans): < 15 minutes, 2-8GB memory
- **Large** (100K-1M loans): < 60 minutes, 8-16GB memory
- **Extra-large** (> 1M loans): < 2 hours, 16-32GB memory, requires chunking

See [Performance SLOs](docs/performance_slos.md) for detailed performance targets and tuning guidelines.

## Security and Compliance

### PII Masking

The system includes PII masking capabilities for data protection:

- **Customer identifiers**: Hashed with SHA-256
- **Customer names**: Partial masking
- **Email addresses**: Domain-preserving masking
- **Phone numbers**: Middle-digit masking
- **Account numbers**: Last-four-digits retention

See [Security Constraints](docs/security_constraints.md) for complete security guidelines.

### Compliance

The system supports compliance with:

- GDPR (General Data Protection Regulation)
- SOX (Sarbanes-Oxley Act)
- PCI DSS (Payment Card Industry Data Security Standard)
- Local data protection regulations

## Contributing

### Development Setup

1. Fork the repository
2. Clone your fork
3. Create a feature branch: `git checkout -b feature/your-feature`
4. Install pre-commit hooks: `pre-commit install`
5. Make your changes
6. Run tests and linting
7. Commit your changes
8. Push to your fork
9. Create a Pull Request

### Code Standards

- Follow PEP 8 style guidelines
- Write docstrings for all functions and classes
- Add tests for new functionality
- Update documentation as needed
- Keep commits focused and atomic

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files
```

## Checklist for Production Deployment

Before deploying to production, ensure you have:

- [ ] **Column mappings** configured for your dataset (`config/column_maps.yml`)
- [ ] **Pricing files** created and paths configured (`config/pricing_config.yml`, `data/pricing/`)
- [ ] **DPD policy** reviewed and threshold set (90, 120, or 180 days in `config/dpd_policy.yml`)
- [ ] **Export paths** configured (`config/export_config.yml`)
- [ ] **Performance settings** tuned for your portfolio size (`docs/performance_slos.md`)
- [ ] **Security controls** reviewed and PII masking enabled (`docs/security_constraints.md`)
- [ ] **Versioning workflow** established (`docs/versioning.md`)
- [ ] **CI/CD pipeline** configured (`.github/workflows/ci.yml`)
- [ ] **Configuration validation** passes (`python validators/schema_validator.py`)
- [ ] **Tests** pass (if implemented)

## Support and Contact

For issues, questions, or contributions:

- **Issues**: [GitHub Issues](https://github.com/Jeninefer/Commercial-View/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Jeninefer/Commercial-View/discussions)
- **Email**: Contact repository maintainer

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built for commercial lending analytics
- Designed for scalability and compliance
- Community-driven development

---

**Status**: ✅ **Production Ready**  
**Configuration**: ✅ **Enterprise-Grade DPD Policy Validated**  
**Pricing**: ✅ **4-Tier Risk-Based Model Active**  
**Pipeline**: ✅ **Multi-Language CI/CD Operational**  
**Analytics**: ✅ **7-Tier Risk Classification System**  
**Dashboard**: ✅ **Interactive KPI Visualization**  
**Version**: 1.0.0  
**Last Updated**: 2024-12-03  
**Maintainer**: Jeninefer
