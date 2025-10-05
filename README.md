# Commercial View

Enterprise-grade portfolio analytics for Abaco Capital.

## Setup and Installation

### Prerequisites

- Python 3.11+
- Virtual environment tool (venv)

### Installation

1. Clone the repository

```bash
git clone https://github.com/Jeninefer/Commercial-View.git
cd Commercial-View
```

1. Create and activate a virtual environment

```bash
# Create virtual environment
python -m venv .venv

# Activate on macOS/Linux
source .venv/bin/activate

# Activate on Windows
.venv\Scripts\activate
```

1. Install dependencies

```bash
pip install -r requirements.txt
```

### Important Note About Python Environment

Always use the Python interpreter from the virtual environment (.venv), not the system Python.

✅ Correct:

```bash
# Activate virtual environment first
source .venv/bin/activate

# Then run any commands
python run.py
pytest tests/
```

❌ Incorrect:

```bash
# Don't use system Python directly
/opt/homebrew/bin/python3 run.py
```

## Running the Application

```bash
# Activate virtual environment
source .venv/bin/activate

# Start the API server
uvicorn run:app --reload

# Or use the Python file directly
python run.py
```

## Running Tests

```bash
# Activate virtual environment
source .venv/bin/activate

# Run all tests
pytest

# Run specific tests
pytest tests/test_api.py -v

# Run tests with coverage
pytest --cov=src tests/
```

## API Documentation

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

### Test Coverage

```bash
pytest tests/ -v --cov=src
```

### Code Formatting

```bash
black src/ tests/
```

### Type Checking

```bash
mypy src/
```

## Deployment

### Docker

```bash
docker build -t commercial-view .
docker run -p 8000:8000 -v $(pwd)/data:/app/data commercial-view
```

### Production

For production deployment, use environment variables for configuration and ensure proper security measures are in place.

## Architecture

The application follows a modular architecture:

- `src/data_loader.py` - Data loading utilities
- `src/pipeline.py` - Data processing pipeline
- `run.py` - FastAPI application
- `tests/` - Comprehensive test suite

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is proprietary to Abaco Capital.

## Support

For issues or questions, please contact the development team.
  kpi_json: "./abaco_runtime/exports/kpi/json"
  kpi_csv: "./abaco_runtime/exports/kpi/csv"

```yaml

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

### Testing and Validation

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

## Contributing Guidelines

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
