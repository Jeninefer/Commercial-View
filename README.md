# Commercial-View Abaco Integration

## 🏦 Production-Validated Commercial Lending Analytics Platform

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Production Ready](https://img.shields.io/badge/status-production%20ready-brightgreen)](https://github.com/Jeninefer/Commercial-View)
[![Abaco Validated](https://img.shields.io/badge/abaco-48%2C853%20records%20validated-success)](#production-validation-status)

**Commercial-View** is a production-validated commercial lending analytics platform specifically designed for **Abaco loan tape data processing**. The platform has been validated against the complete Abaco dataset with **48,853 records** and supports Spanish client names, USD factoring products, and comprehensive risk analytics.

## 🎯 Production Validation Status

### ✅ **100% VALIDATED FOR REAL ABACO DATA**

| Metric               | Value                                      | Status             |
| -------------------- | ------------------------------------------ | ------------------ |
| **Total Records**    | 48,853                                     | ✅ **EXACT MATCH** |
| **Loan Data**        | 16,205 records × 28 columns                | ✅ **VALIDATED**   |
| **Payment History**  | 16,443 records × 18 columns                | ✅ **VALIDATED**   |
| **Payment Schedule** | 16,205 records × 16 columns                | ✅ **VALIDATED**   |
| **Spanish Support**  | "SERVICIOS TECNICOS MEDICOS, S.A. DE C.V." | ✅ **CONFIRMED**   |
| **Currency**         | USD exclusively                            | ✅ **VALIDATED**   |
| **Product Type**     | Factoring exclusively                      | ✅ **VALIDATED**   |
| **Interest Rates**   | 29.47% - 36.99% APR                        | ✅ **VALIDATED**   |
| **Companies**        | Abaco Technologies & Abaco Financial       | ✅ **CONFIRMED**   |

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Clone and enter directory
git clone https://github.com/Jeninefer/Commercial-View.git
cd Commercial-View

# Activate Commercial-View environment
chmod +x activate_commercial_view.sh
./activate_commercial_view.sh
```

### 2. Process Abaco Data

#### With Sample Data (for testing)

```bash
# Create sample data matching exact schema
python scripts/create_complete_abaco_sample.py

# Process portfolio
python portfolio.py --config config
```

#### With Real Abaco Data

```bash
# 1. Place your CSV files in data/ directory:
#    - Abaco - Loan Tape_Loan Data_Table.csv (16,205 records)
#    - Abaco - Loan Tape_Historic Real Payment_Table.csv (16,443 records)
#    - Abaco - Loan Tape_Payment Schedule_Table.csv (16,205 records)

# 2. Process real data
python portfolio.py --config config --abaco-only

# 3. Check results
ls abaco_runtime/exports/
```

## 📊 Validated Data Structure

### Loan Data Table (16,205 records × 28 columns)
