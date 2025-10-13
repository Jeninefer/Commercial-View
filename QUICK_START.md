# Commercial-View Quick Start Guide

## 🏦 Production-Ready Abaco Integration

**Status**: ✅ **100% VALIDATED** for 48,853 Abaco records

## 🚀 Quick Setup

### 1. Activate Environment

```bash

# Make activation script executable and run

chmod +x activate_commercial_view.sh
./activate_commercial_view.sh

```bash

### 2. Install Dependencies (in activated environment)

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt

```bash

1. Run setup script

```bash
python setup_project.py

```bash

### 4. Validate Production Readiness

```bash
python scripts/production_validation_complete.py

```bash

## 📊 Process Abaco Data

### With Sample Data

```bash

# Create sample data

python scripts/create_complete_abaco_sample.py

# Process portfolio

python portfolio.py --config config

```bash

### With Real Abaco Data

1. Place your CSV files in `data/` directory:

   - `Abaco - Loan Tape_Loan Data_Table.csv` (16,205 records)

   - `Abaco - Loan Tape_Historic Real Payment_Table.csv` (16,443 records)

   - `Abaco - Loan Tape_Payment Schedule_Table.csv` (16,205 records)

2. Run processing:

```bash
python portfolio.py --config config --abaco-only

```bash

3. Check results in `abaco_runtime/exports/`

## ✅ Validated Features

- **Exact Schema**: 48,853 records (16,205 + 16,443 + 16,205)

- **Spanish Names**: "SERVICIOS TECNICOS MEDICOS, S.A. DE C.V."

- **USD Currency**: Factoring products exclusively

- **Interest Rates**: 29.47% - 36.99% APR validated

- **Companies**: Abaco Technologies & Abaco Financial

- **Terms**: 30-120 days with bullet payments

- **Export System**: CSV and JSON formats

- **Risk Analytics**: 7-tier delinquency + risk scoring

## 🆘 Troubleshooting

### Environment Issues

```bash

# Recreate virtual environment

rm -rf .venv
python -m venv .venv
./activate_commercial_view.sh
pip install -r requirements.txt

```bash

### Git Issues

```bash

# Reset if needed

git reset --soft HEAD~1
./sync_github.sh

```bash

### Import Issues

```bash

# Fix Python path

export PYTHONPATH="${PWD}/src:${PYTHONPATH}"
python -c "import src.data_loader; print('✅ DataLoader working')"

```bash

## 🎯 Production Ready

Your Commercial-View platform is **validated and ready** for processing the complete Abaco loan tape with 48,853 records featuring Spanish client names and USD factoring products.
