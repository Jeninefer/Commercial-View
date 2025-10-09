# Quick Start Guide for Commercial-View

**Ábaco Capital - Portfolio Analytics Platform**  
Version: 2.0.0 | Last Updated: 2025-01-09

---

## 🚀 Immediate Setup Steps

### 1. Prerequisites

Ensure you have:

- ✅ Python 3.11+ installed
- ✅ Git installed
- ✅ Virtual environment tool (venv)
- ✅ (Optional) Node.js 18+ for dashboard frontend

**Check your Python version:**

```bash
python --version  # Should show 3.11 or higher
```

### 2. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/Jeninefer/Commercial-View.git
cd Commercial-View

# Create and activate virtual environment
python -m venv .venv

# Activate (choose based on your OS/shell)
source .venv/bin/activate          # macOS/Linux (bash/zsh)
source .venv/bin/activate.csh      # macOS/Linux (csh/tcsh)
.venv\Scripts\activate             # Windows (PowerShell)
.venv\Scripts\activate.bat         # Windows (CMD)

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure VS Code (Recommended)

The project includes VS Code configuration. Just open in VS Code:

```bash
code .
```

**Select Python Interpreter:**

1. Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows)
2. Type "Python: Select Interpreter"
3. Choose the interpreter from `.venv`

### 4. Project Structure Overview

Familiarize yourself with the project structure:

```plaintext
Commercial-View/
│
├── .venv/                  # Virtual environment
│
├── config/                 # Configuration files
│   ├── column_maps.yml
│   ├── pricing_config.yml
│   ├── dpd_policy.yml
│   └── export_config.yml
│
├── data/                   # Data files
│   ├── pricing/            # Pricing files
│   └── raw/                # Raw data files
│
├── docs/                   # Documentation
│   ├── performance_slos.md
│   └── security_constraints.md
│
├── src/                    # Source code
│   ├── process_portfolio.py
│   └── utils/
│
├── tests/                  # Test cases
│   ├── unit/
│   └── integration/
│
├── .gitignore              # Git ignore file
├── README.md                # Main README file
└── QUICKSTART.md            # Quick start guide
```

### 5. Validate Configuration

Run the schema validator to ensure all configuration files are correct:

```bash
python validators/schema_validator.py
```

Expected output:

```
✅ All validations passed!
```

### 6. Customize Configuration

#### A. Column Mappings (REQUIRED)

Edit `config/column_maps.yml` to match your data schema:

```bash
# Open in your editor
nano config/column_maps.yml  # or vi, vim, code, etc.
```

Update field mappings:

```yaml
loan_data:
  loan_id: "your_actual_loan_id_column"
  customer_id: "your_customer_id_column"
  loan_amount: "your_amount_column"
  # ... etc
```

#### B. Pricing Files (REQUIRED)

1. Review example pricing files in `data/pricing/`
2. Either modify them or create your own following the same structure
3. Update paths in `config/pricing_config.yml` if needed

Example pricing file structure:

```csv
tenor_min,tenor_max,amount_min,amount_max,base_rate,margin,total_rate
0,90,0,50000,0.0500,0.0200,0.0700
```

#### C. DPD Policy (REVIEW REQUIRED)

Choose your default threshold in `config/dpd_policy.yml`:

```yaml
default_threshold:
  days: 180 # Options: 90, 120, or 180
```

Review and adjust DPD buckets if needed.

#### D. Export Path (OPTIONAL)

Default export path is `./abaco_runtime/exports`. To change:

```yaml
# In config/export_config.yml
export_paths:
  base_path: "/your/preferred/path"
```

### 7. Validate Your Changes

After customization, run validation again:

```bash
python validators/schema_validator.py
```

### 8. Directory Setup

Create the export directories:

```bash
mkdir -p abaco_runtime/exports/{kpi/json,kpi/csv,dpd_frame,buckets,reports,archive}
```

### 9. Test Run (When Implementation Ready)

Once your processing code is implemented:

```bash
# Example command structure
# python src/process_portfolio.py --config config/
```

### 10. Set Up Pre-commit Hooks (Development)

If you're developing:

```bash
pip install pre-commit
pre-commit install
```

Test pre-commit:

```bash
pre-commit run --all-files
```

## Configuration Checklist

Before running in production:

- [ ] Column mappings updated for your data schema
- [ ] Pricing files created/updated in `data/pricing/`
- [ ] Pricing file paths configured in `config/pricing_config.yml`
- [ ] DPD default threshold set (90, 120, or 180 days)
- [ ] DPD buckets reviewed
- [ ] Export paths configured
- [ ] Export directories created
- [ ] Schema validation passes
- [ ] Performance settings reviewed (see `docs/performance_slos.md`)
- [ ] Security controls reviewed (see `docs/security_constraints.md`)

## Quick Reference

### Configuration Files

| File                        | Purpose                  | Priority                 |
| --------------------------- | ------------------------ | ------------------------ |
| `config/column_maps.yml`    | Map your field names     | HIGH - Must customize    |
| `config/pricing_config.yml` | Pricing grid setup       | HIGH - Must configure    |
| `config/dpd_policy.yml`     | DPD thresholds & buckets | MEDIUM - Review required |
| `config/export_config.yml`  | Export paths & formats   | LOW - Optional           |

### Commands

```bash
# Validate configuration
python validators/schema_validator.py

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies
pip install -r requirements-dev.txt

# Run pre-commit checks
pre-commit run --all-files

# Check Python version
python --version  # Should be 3.8+
```

### Outputs

After processing, find results in:

- KPI JSON: `./abaco_runtime/exports/kpi/json/`
- KPI CSV: `./abaco_runtime/exports/kpi/csv/`
- DPD Frame: `./abaco_runtime/exports/dpd_frame/`
- Buckets: `./abaco_runtime/exports/buckets/`

## Need Help?

1. **Configuration Issues**: Run `python validators/schema_validator.py` for detailed error messages
2. **Documentation**: Check `docs/` directory for detailed guides
3. **Examples**: Review example pricing files in `data/pricing/`
4. **Issues**: Open an issue on GitHub

## Next Steps

1. Complete the configuration checklist above
2. Review documentation in `docs/` folder
3. Test with a small dataset first
4. Scale up to production portfolio sizes
5. Set up monitoring and alerts

For detailed information, see the main [README.md](README.md).
