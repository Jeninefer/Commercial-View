# Commercial-View

Enterprise Commercial Lending Analytics Platform with Abaco Integration

## Overview

Commercial-View is a comprehensive analytics system for commercial lending portfolios that provides:

- **DPD (Days Past Due) Analysis**: Calculate and track payment delinquency
- **Risk Bucketing**: Classify loans into risk buckets based on DPD
- **KPI Generation**: Generate key performance indicators for portfolio monitoring
- **Abaco Loan Tape Integration**: Full support for Abaco CSV processing with automated risk scoring
- **Pricing Management**: Configurable pricing grids with interval bands
- **Data Export**: Export analytics results in multiple formats (JSON, CSV, Parquet)

## Table of Contents

- [Quick Start](#quick-start)
- [Abaco Integration](#abaco-integration)
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

```bash
# Clone the repository
git clone https://github.com/Jeninefer/Commercial-View.git
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

# Process Abaco loan tape data
python -c "
from src.data_loader import DataLoader
loader = DataLoader()
data = loader.load_abaco_data()
print(f'Loaded tables: {list(data.keys())}')
"

# View exports
ls -la abaco_runtime/exports/
```

## Abaco Integration

### Features

Commercial-View now includes comprehensive Abaco loan tape integration:

- ✅ **Complete CSV Processing**: Support for Loan Data, Payment History, and Payment Schedule tables
- ✅ **Automated Risk Scoring**: Multi-factor risk assessment with configurable weights
- ✅ **Delinquency Bucketing**: 7-tier classification system (current → NPL)
- ✅ **Schema Mapping**: Flexible YAML-based column mapping system
- ✅ **Data Transformation**: Automatic date parsing, type conversion, and validation

### Supported Data Tables

1. **Loan Data** (16,205+ records): Core loan information, terms, and current status
2. **Historic Real Payment** (16,443+ records): Actual payment history and performance
3. **Payment Schedule** (16,205+ records): Scheduled payments and projections

### Quick Abaco Setup

```bash
# 1. Place Abaco CSV files in data/ directory:
#    - Abaco - Loan Tape_Loan Data_Table.csv
#    - Abaco - Loan Tape_Historic Real Payment_Table.csv
#    - Abaco - Loan Tape_Payment Schedule_Table.csv

# 2. Load and process Abaco data
python -c "
from src.data_loader import DataLoader
loader = DataLoader()
abaco_data = loader.load_abaco_data()

for table_name, df in abaco_data.items():
    print(f'{table_name}: {len(df)} rows')
    if 'risk_score' in df.columns:
        print(f'  - Risk scores calculated')
    if 'delinquency_bucket' in df.columns:
        print(f'  - Delinquency buckets assigned')
"
```

## Configuration

### Configuration Files

The system uses YAML configuration files located in the `config/` directory:

#### 1. Abaco Column Mappings (`config/abaco_column_maps.yml`)

```yaml
loan_data:
  customer_id: "Customer ID"
  loan_id: "Loan ID"
  outstanding_balance: "Outstanding Loan Value"
  days_past_due: "Days in Default"
  # ...additional mappings
```

#### 2. Standard Column Mappings (`config/column_maps.yml`)

Maps your dataset field names to the system's expected field names.

#### 3. Pricing Configuration (`config/pricing_config.yml`)

Defines pricing grids and interval bands for risk-based pricing.

#### 4. DPD Policy (`config/dpd_policy.yml`)

Configures Days Past Due thresholds and bucketing rules.

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Testing Guide](docs/TESTING.md)**: Complete test suite with 45+ test cases
- **[Architecture](docs/ARCHITECTURE.md)**: System design and technical decisions
- **[API Reference](docs/API_REFERENCE.md)**: Complete API documentation
- **[Performance SLOs](docs/performance_slos.md)**: Expected performance characteristics
- **[Security Constraints](docs/security_constraints.md)**: PII masking and compliance
- **[Versioning Strategy](docs/versioning.md)**: Release workflow and tagging

## Development

### Project Structure

```text
Commercial-View/
├── config/                      # Configuration files
│   ├── abaco_column_maps.yml    # Abaco schema mapping
│   ├── column_maps.yml          # Standard column mapping
│   ├── pricing_config.yml       # Pricing configuration
│   └── dpd_policy.yml           # DPD policy rules
├── src/                         # Source code
│   ├── __init__.py              # Package initialization
│   ├── data_loader.py           # DataLoader with Abaco support
│   └── ...                      # Additional modules
├── data/                        # Data files
│   └── pricing/                 # Pricing grid CSVs
├── docs/                        # Documentation
├── tests/                       # Test suite
└── abaco_runtime/               # Runtime exports
    └── exports/                 # Generated reports
```

### Running Tests

```bash
# Run all tests including Abaco integration
pytest tests/ -v --cov=src

# Run specific Abaco tests
pytest tests/test_abaco_integration.py -v

# Run with coverage reporting
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

## Performance and Scalability

The system is designed to handle portfolios of various sizes:

- **Small** (< 10K loans): < 5 minutes, < 2GB memory
- **Medium** (10K-100K loans): < 15 minutes, 2-8GB memory
- **Large** (100K-1M loans): < 60 minutes, 8-16GB memory
- **Extra-large** (> 1M loans): < 2 hours, 16-32GB memory, requires chunning

## Security and Compliance

### PII Masking

The system includes PII masking capabilities for data protection:

- **Customer identifiers**: Hashed with SHA-256
- **Customer names**: Partial masking
- **Email addresses**: Domain-preserving masking
- **Phone numbers**: Middle-digit masking

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

## Production Deployment Checklist

Before deploying to production, ensure you have:

- [ ] **Column mappings** configured for your dataset (`config/column_maps.yml`)
- [ ] **Abaco integration** configured if using Abaco loan tapes (`config/abaco_column_maps.yml`)
- [ ] **Pricing files** created and paths configured (`config/pricing_config.yml`)
- [ ] **DPD policy** reviewed and threshold set (`config/dpd_policy.yml`)
- [ ] **Export paths** configured (`config/export_config.yml`)
- [ ] **Performance settings** tuned for your portfolio size
- [ ] **Security controls** reviewed and PII masking enabled
- [ ] **Configuration validation** passes (`python validators/schema_validator.py`)
- [ ] **Tests** pass (`pytest tests/ -v`)

## Support and Contact

For issues, questions, or contributions:

- **Issues**: [GitHub Issues](https://github.com/Jeninefer/Commercial-View/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Jeninefer/Commercial-View/discussions)
- **Email**: Contact repository maintainer

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built for commercial lending analytics with enterprise-grade Abaco integration
- Designed for scalability, compliance, and production use
- Community-driven development with comprehensive testing

---

**Version**: 1.1.0  
**Last Updated**: 2024-12-19  
**Maintainer**: Jeninefer  
**Latest**: Full Abaco loan tape integration with automated risk scoring
