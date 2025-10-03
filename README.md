# Commercial-View
<<<<<<< HEAD

A comprehensive dashboard for monitoring and analyzing principal Key Performance Indicators (KPIs) in commercial operations.

## Description

Commercial-View provides real-time insights into business performance metrics, enabling data-driven decision making through intuitive visualizations and analytics.

## Features

- 📊 Real-time KPI monitoring
- 📈 Interactive data visualizations
- 🎯 Performance tracking
- 📱 Responsive design
- 🔍 Advanced filtering and search

## Installation
=======
Principal KPI Analytics System for Commercial Lending

## Overview

Commercial-View is a comprehensive analytics system for commercial lending portfolios that provides:
- **DPD (Days Past Due) Analysis**: Calculate and track payment delinquency
- **Risk Bucketing**: Classify loans into risk buckets based on DPD
- **KPI Generation**: Generate key performance indicators for portfolio monitoring
- **Pricing Management**: Configurable pricing grids with interval bands
- **Data Export**: Export analytics results in multiple formats (JSON, CSV, Parquet)

## Table of Contents

- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Documentation](#documentation)
- [Development](#development)
- [CI/CD](#cicd)
- [Contributing](#contributing)
- [License](#license)

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

### Installation
>>>>>>> pr-50

```bash
# Clone the repository
git clone https://github.com/Jeninefer/Commercial-View.git
<<<<<<< HEAD

# Navigate to project directory
cd Commercial-View

# Install dependencies
npm install
```

## Usage

```bash
# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test
```

## Project Structure

```
Commercial-View/
├── src/
│   ├── components/
│   ├── pages/
│   ├── services/
│   └── utils/
├── public/
├── tests/
└── docs/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For questions or support, please open an issue on GitHub.
=======
cd Commercial-View

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt

# Install pre-commit hooks (optional, for contributors)
pip install pre-commit
pre-commit install
```

### Running the System

```bash
# Validate configuration files
python validators/schema_validator.py

# Process portfolio data (placeholder - implement your processing script)
# python src/process_portfolio.py --config config/

# View exports
ls -la abaco_runtime/exports/
```

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

**How to customize:**
- Update the values (right side) to match your data field names
- Keep the keys (left side) unchanged
- See [Column Mapping Documentation](docs/column_mapping_guide.md) for details

#### 2. Pricing Configuration (`config/pricing_config.yml`)

Defines pricing grids and interval bands:

```yaml
band_keys:
  tenor_days:
    lower_bound: "tenor_min"
    upper_bound: "tenor_max"
  amount:
    lower_bound: "amount_min"
    upper_bound: "amount_max"
```

**Pricing Files:**
- Located in `data/pricing/`
- Example files provided:
  - `main_pricing.csv`: Primary pricing grid
  - `commercial_loans_pricing.csv`: Commercial loan pricing
  - `retail_loans_pricing.csv`: Retail loan pricing
  - `risk_based_pricing.csv`: Risk-adjusted pricing

#### 3. DPD Policy (`config/dpd_policy.yml`)

Configures Days Past Due thresholds and bucketing:

```yaml
default_threshold:
  days: 180  # Default threshold for loan default classification

dpd_buckets:
  - bucket: "Current"
    min_dpd: 0
    max_dpd: 0
    default_flag: false
  - bucket: "1-30 Days"
    min_dpd: 1
    max_dpd: 30
    default_flag: false
  # ... more buckets
```

**Customization options:**
- Change `default_threshold.days` to 90, 120, or 180 based on your policy
- Add or modify DPD buckets
- Adjust risk levels and descriptions

#### 4. Export Configuration (`config/export_config.yml`)

Controls output paths and export formats:

```yaml
export_paths:
  base_path: "./abaco_runtime/exports"
  kpi_json: "./abaco_runtime/exports/kpi/json"
  kpi_csv: "./abaco_runtime/exports/kpi/csv"
```

**Customization:**
- Change `base_path` to your preferred export directory
- Configure file naming patterns
- Enable/disable specific export formats

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Performance SLOs](docs/performance_slos.md)**: Expected performance characteristics and scalability
- **[Security Constraints](docs/security_constraints.md)**: PII masking, data protection, and compliance
- **[Versioning Strategy](docs/versioning.md)**: Release workflow, tagging conventions, and version management

## Output Specifications

### DPD Frame Output

CSV/Parquet file with the following columns:

| Column | Type | Description |
|--------|------|-------------|
| `past_due_amount` | Numeric | Amount overdue |
| `days_past_due` | Integer | Days since payment due |
| `first_arrears_date` | Date | Date of first missed payment |
| `last_payment_date` | Date | Date of last payment received |
| `last_due_date` | Date | Last payment due date |
| `is_default` | Boolean | Default flag (based on DPD threshold) |
| `reference_date` | Date | Analysis reference date |

### Buckets Output

CSV/JSON file with loan risk buckets:

| Column | Type | Description |
|--------|------|-------------|
| `dpd_bucket` | String | Bucket name (e.g., "1-30 Days") |
| `dpd_bucket_value` | Integer | Numeric bucket identifier |
| `dpd_bucket_description` | String | Bucket description |
| `default_flag` | Boolean | Whether bucket represents default |

### KPI Exports

Located in `./abaco_runtime/exports/kpi/`:

- **JSON format**: Structured metrics for API consumption
- **CSV format**: Tabular metrics for reporting

## Development

### Project Structure

```
Commercial-View/
├── config/                      # Configuration files
│   ├── column_maps.yml
│   ├── pricing_config.yml
│   ├── dpd_policy.yml
│   └── export_config.yml
├── data/                        # Data files
│   └── pricing/                 # Pricing grid CSVs
├── docs/                        # Documentation
│   ├── performance_slos.md
│   ├── security_constraints.md
│   └── versioning.md
├── validators/                  # Configuration validators
│   └── schema_validator.py
├── .github/                     # GitHub configuration
│   └── workflows/
│       └── ci.yml               # CI/CD pipeline
├── .pre-commit-config.yaml      # Pre-commit hooks
├── .gitignore                   # Git ignore patterns
├── README.md                    # This file
└── VERSION                      # Version number
```

### Running Tests

```bash
# Validate configuration
python validators/schema_validator.py

# Run unit tests (when implemented)
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Code Quality

```bash
# Format code with Black
black src/ validators/

# Sort imports with isort
isort src/ validators/

# Lint with Flake8
flake8 src/ validators/

# Type checking with mypy
mypy src/ validators/
```

## CI/CD

The project includes a comprehensive CI/CD pipeline (`.github/workflows/ci.yml`) that:

1. **Validates** version tags and configuration files
2. **Lints** code with Black, isort, Flake8, and Pylint
3. **Tests** across Python 3.8, 3.9, and 3.10
4. **Scans** for security vulnerabilities
5. **Builds** package artifacts
6. **Deploys** to staging (develop branch) and production (tags)

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

See [Versioning Documentation](docs/versioning.md) for detailed release workflow.

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

The project uses pre-commit hooks to ensure code quality:

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

**Version**: 1.0.0  
**Last Updated**: 2024-12-03  
**Maintainer**: Jeninefer
>>>>>>> pr-50
