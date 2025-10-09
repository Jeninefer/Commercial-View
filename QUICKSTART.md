# Commercial-View Quick Start Guide

## Prerequisites

1. **Python 3.11+** with virtual environment activated:
   ```bash
   source .venv/bin/activate  # macOS/Linux
   .\.venv\Scripts\Activate.ps1  # Windows PowerShell
   ```

2. **Required packages installed**:
   ```bash
   pip install pandas numpy plotly xgboost scikit-learn jupyter
   ```

## Quick Test Run

### Option 1: Run Test Script (Fastest)

```bash
# From project root
python run_portfolio_analysis.py
```

This will:
- Test data loading (creates sample data if files not found)
- Run basic analytics
- Generate test outputs in `output/test_results/`

### Option 2: Run Jupyter Notebook

```bash
# Start Jupyter
jupyter notebook

# Open: notebooks/portfolio_analytics_pipeline.ipynb
# Run All Cells
```

### Option 3: Run Schema Parser Tests

```bash
# Test schema parser
python test_schema_parser.py

# Or view specific dataset
python -m src.utils.schema_parser Downloads/abaco_schema_autodetected.json --dataset "Loan Data"
```

## Expected Outputs

After running tests, check:
- `output/test_results/` - KPIs, visualizations, reports
- `docs/schema_documentation.md` - Auto-generated schema docs

## Troubleshooting

### Import Errors
```bash
# Ensure project root is in Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"  # Linux/macOS
$env:PYTHONPATH += ";$(pwd)"  # PowerShell
```

### Data Not Found
The test script will create sample data automatically. For real data:
1. Place CSV files in `data/pricing/`
2. Update `CONFIG` in the notebook with your file paths

### Module Not Found
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

## Next Steps

1. ✅ **Customize Configuration**: Edit notebook cell 4 (CONFIG dictionary)
2. ✅ **Add Your Data**: Place CSVs in `data/pricing/`
3. ✅ **Run Full Analysis**: Execute all notebook cells
4. ✅ **Review Outputs**: Check `output/dashboards/`

## Getting Help

- Review error messages in test output
- Check `TESTING.md` for detailed testing guide
- Ensure all prerequisites are met

## Quick Commands Reference

```bash
# Activate environment
source .venv/bin/activate

# Run tests
python run_portfolio_analysis.py

# Run schema parser
python test_schema_parser.py

# Start Jupyter
jupyter notebook

# Check Python environment
which python
python --version
pip list | grep -E "(pandas|plotly|xgboost)"
```

## Success Indicators

✅ You're ready when:
- Test script runs without errors
- Sample visualizations generate in `output/test_results/`
- KPIs export to CSV successfully
- You see "🎉 All tests passed!"
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

| File | Purpose | Priority |
|------|---------|----------|
| `config/column_maps.yml` | Map your field names | HIGH - Must customize |
| `config/pricing_config.yml` | Pricing grid setup | HIGH - Must configure |
| `config/dpd_policy.yml` | DPD thresholds & buckets | MEDIUM - Review required |
| `config/export_config.yml` | Export paths & formats | LOW - Optional |

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
