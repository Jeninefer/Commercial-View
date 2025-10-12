# Requirements Documentation - Abaco Integration

## System Requirements

### Python Version
- Python 3.11 or higher (recommended for optimal performance)
- Virtual environment recommended

### Hardware Requirements (for 48,853 records)
- RAM: 8GB minimum (16GB recommended for full dataset processing)
- Storage: 2GB available space (includes exports and runtime data)
- CPU: Multi-core recommended for large dataset processing

## Core Dependencies

### Production Dependencies (requirements.txt)
```txt
pandas>=2.0.0          # Data processing (Abaco dataset handling)
numpy>=1.24.0          # Numerical computing (risk calculations)
PyYAML>=6.0            # Configuration file processing
jsonschema>=4.0.0      # Schema validation (Abaco schema compliance)
python-dateutil>=2.8.0 # Date processing (payment dates, schedules)
```

### Development Dependencies (requirements-dev.txt)
```txt
pytest>=7.0.0          # Testing framework
black>=23.0.0          # Code formatting
flake8>=6.0.0          # Code linting
mypy>=1.0.0            # Type checking
jupyter>=1.0.0         # Data analysis notebooks
```

## Abaco Data Requirements

### Required CSV Files (Exact Schema)
The platform expects three CSV files with the exact structure:

1. **Abaco - Loan Tape_Loan Data_Table.csv** (16,205 records, 28 columns)
   - Spanish client names: "SERVICIOS TECNICOS MEDICOS, S.A. DE C.V."
   - USD currency exclusively
   - Factoring products only
   - Bullet payment frequency
   - Companies: Abaco Technologies, Abaco Financial

2. **Abaco - Loan Tape_Historic Real Payment_Table.csv** (16,443 records, 18 columns)
   - Payment status: Late, On Time, Prepayment
   - USD currency exclusively
   - Principal, Interest, Fee breakdowns

3. **Abaco - Loan Tape_Payment Schedule_Table.csv** (16,205 records, 16 columns)
   - Future payment schedules in USD
   - Outstanding loan values (typically $0 for completed)

### Schema Validation
The platform validates against the exact schema file:
- `config/abaco_schema_autodetected.json` - Complete schema definition
- Total records must equal 48,853 (16,205 + 16,443 + 16,205)
- All Spanish names and USD currency validated

## Installation & Setup

### Quick Installation
```bash
# Clone repository
git clone https://github.com/Jeninefer/Commercial-View.git
cd Commercial-View

# Set up environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Validate installation
python setup_project.py
```

### Configuration Files Required
- `config/abaco_column_maps.yml` - Abaco column mapping
- `config/pricing_config.yml` - Interest rate and pricing settings
- `config/dpd_policy.yml` - Delinquency policy (factoring-specific)
- `config/export_config.yml` - Export format settings

## Production Deployment Checklist

- [ ] Python 3.11+ environment verified
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Abaco CSV files placed in `data/` directory
- [ ] Schema validation passed (48,853 records confirmed)
- [ ] Spanish client names processing tested
- [ ] USD currency validation confirmed
- [ ] Export directories configured
- [ ] Risk scoring algorithm calibrated for factoring

## Performance Considerations

### Memory Usage (48,853 records)
- **Minimum**: 4GB RAM for basic processing
- **Recommended**: 8GB RAM for optimal performance
- **Large datasets**: 16GB RAM for multiple concurrent processing

### Processing Time Estimates
- **Schema validation**: < 1 minute
- **Data loading**: 2-5 minutes (depending on hardware)
- **Risk scoring**: 3-8 minutes for full dataset
- **Export generation**: 1-3 minutes
- **Total processing**: 10-20 minutes for complete pipeline

This documentation ensures optimal setup and performance for processing real Abaco loan tape data with 48,853 records.
