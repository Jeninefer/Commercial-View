# Configuration Summary for Production Deployment

This document provides direct answers to the configuration questions for finalizing the Commercial-View deployment.

## 1. Column Maps

**Location**: `config/column_maps.yml`

The column mapping configuration includes sections for:

- `loan_data`: Core loan and customer fields
- `payment_data`: Payment transaction fields
- `dpd_frame_output`: DPD calculation output (contract-compliant)
- `buckets_output`: Risk bucket output (contract-compliant)
- `customer_data`: Customer/entity information

### Contract Output Fields (Pre-configured)

**DPD Frame Output** (`dpd_frame_output` section):

- `past_due_amount`
- `days_past_due`
- `first_arrears_date`
- `last_payment_date`
- `last_due_date`
- `is_default`
- `reference_date`

**Buckets Output** (`buckets_output` section):

- `dpd_bucket`
- `dpd_bucket_value`
- `dpd_bucket_description`
- `default_flag`

### How to Customize

If your field names differ from the defaults, update the **right-hand side** values in `config/column_maps.yml`:

```yaml
loan_data:
  loan_id: "YOUR_LOAN_ID_FIELD"      # Update this
  customer_id: "YOUR_CUSTOMER_FIELD"  # Update this
  loan_amount: "YOUR_AMOUNT_FIELD"    # Update this

  # Keep left side unchanged, update right side

```bash
## 2. Pricing Files

### Pricing File Paths

**Location**: `config/pricing_config.yml`

**Configured paths**:

```yaml
pricing_files:
  main_pricing_csv: "./data/pricing/main_pricing.csv"
  commercial_loans: "./data/pricing/commercial_loans_pricing.csv"
  retail_loans: "./data/pricing/retail_loans_pricing.csv"
  risk_based_pricing: "./data/pricing/risk_based_pricing.csv"
```bash
### Interval Bands (Grid Ranges)

**Configured as requested**:

```yaml
band_keys:
  tenor_days:
    lower_bound: "tenor_min"
    upper_bound: "tenor_max"
  
  amount:
    lower_bound: "amount_min"
    upper_bound: "amount_max"
```bash
This matches the specification: `{feature: (low_col, high_col)}`

- tenor_days: ("tenor_min", "tenor_max")
- amount: ("amount_min", "amount_max")

### Example Pricing Files Provided

Four example pricing CSV files are included in `data/pricing/`:

1. **main_pricing.csv**: General pricing with tenor and amount bands
2. **commercial_loans_pricing.csv**: Commercial/term loan specific pricing
3. **retail_loans_pricing.csv**: Retail/consumer loan pricing
4. **risk_based_pricing.csv**: Credit score-based pricing

**Standard CSV structure**:

```csv
tenor_min,tenor_max,amount_min,amount_max,base_rate,margin,total_rate,product_type,customer_segment
0,90,0,50000,0.0500,0.0200,0.0700,Commercial,Standard
```bash
### How to Use Your Own Files

1. **Option A**: Replace example files with your own (keep same filenames)
2. **Option B**: Add new files to `data/pricing/` and update paths in `config/pricing_config.yml`
3. **Option C**: Provide files and we'll integrate them

## 3. DPD Policy

**Location**: `config/dpd_policy.yml`

### Default Threshold Configuration

**Current setting**: 180 days

```yaml
default_threshold:
  days: 180  # Standard default threshold
  description: "Loans with DPD >= 180 days are considered defaulted"
```bash
### Alternative Thresholds Available

```yaml
alternatives:
  conservative: 90   # More conservative approach
  moderate: 120      # Moderate approach
  standard: 180      # Current setting
```bash
### Recommendation

- **Keep 180 days**: For standard Basel III compliance and industry practice
- **Change to 120 days**: For more conservative risk management
- **Change to 90 days**: For very strict default classification

**To change**: Update the `days` value in `config/dpd_policy.yml`

### DPD Buckets

Pre-configured with 7 buckets:

1. Current (0 days)
2. 1-30 Days
3. 31-60 Days
4. 61-90 Days
5. 91-120 Days
6. 121-180 Days
7. 180+ Days (Default)

Only the last bucket (180+) is marked as default. Adjust the threshold to change this behavior.

## 4. Export Path

**Location**: `config/export_config.yml`

### Current Configuration

**Base path**: `./abaco_runtime/exports`

```yaml
export_paths:
  base_path: "./abaco_runtime/exports"
  kpi_json: "./abaco_runtime/exports/kpi/json"
  kpi_csv: "./abaco_runtime/exports/kpi/csv"
  dpd_frame: "./abaco_runtime/exports/dpd_frame"
  buckets: "./abaco_runtime/exports/buckets"
  reports: "./abaco_runtime/exports/reports"
  archive: "./abaco_runtime/exports/archive"
```bash
### Output File Locations

After processing, files will be located at:

- **KPI JSON**: `./abaco_runtime/exports/kpi/json/kpi_metrics_{date}_{time}.json`
- **KPI CSV**: `./abaco_runtime/exports/kpi/csv/kpi_metrics_{date}_{time}.csv`
- **DPD Frame**: `./abaco_runtime/exports/dpd_frame/dpd_frame_{date}_{time}.csv`
- **Buckets**: `./abaco_runtime/exports/buckets/buckets_{date}_{time}.csv`

### To Change Export Path

Update `base_path` in `config/export_config.yml` to your preferred location:

```yaml
export_paths:
  base_path: "/your/custom/path"
```bash
### Recommendation

✅ **Keep default path** `./abaco_runtime/exports` - Already configured and .gitignore excludes it

## 5. Performance SLOs

**Location**: `docs/performance_slos.md`

### Expected Portfolio Sizes

| Portfolio Size | Record Count | Processing Time | Memory | Chunking |
|----------------|--------------|-----------------|--------|----------|
| Small | < 10,000 | < 5 minutes | < 2GB | Not required |
| Medium | 10K - 100K | < 15 minutes | 2-8GB | Recommended (10K/chunk) |
| Large | 100K - 1M | < 60 minutes | 8-16GB | Required (10K/chunk) |
| Extra-Large | > 1M | < 2 hours | 16-32GB | Required (5K/chunk) |

### Chunking Configuration

For large portfolios, chunking is automatically enabled:

```yaml
chunking:
  enabled: true
  default_chunk_size: 10000
  adaptive_chunking: true
```bash
### What We Need

Please provide:

- **Current portfolio size**: Number of loans in your typical batch
- **Expected growth**: Anticipated portfolio growth over next 12 months
- **Peak processing**: Maximum number of loans in a single batch

This helps us:

- Tune memory allocation
- Optimize chunk sizes
- Configure parallel processing
- Set appropriate timeouts

## 6. Security Constraints

**Location**: `docs/security_constraints.md`

### PII Masking Before Export

Pre-configured masking strategies:

| Field Type | Strategy | Example |
|------------|----------|---------|
| Customer ID | SHA-256 Hash | "HSH-89AB4F2E" |
| Customer Name | Full mask | "J*** S****" |
| Email | Domain-preserving | "j***@example.com" |
| Phone | Middle digits | "+1-555-XXX-XX67" |
| Account Number | Last 4 digits | "************3456" |

### Export Security Levels

**KPI Exports** (JSON/CSV):

- Security Level: Internal
- PII Masking: Required
- All identifiers hashed

**DPD Frame Exports**:

- Security Level: Confidential
- PII Masking: Required
- Customer data masked

**Buckets Exports**:

- Security Level: Internal
- PII Masking: Required
- Aggregated data only

### What We Need

Confirm:

- [ ] Is PII masking required for your use case? (Recommended: Yes)
- [ ] Which fields contain PII in your dataset?
- [ ] Are there additional masking requirements beyond what's documented?

## 7. Versioning

**Location**: `docs/versioning.md`

### Tag Format

**Format**: `v{MAJOR}.{MINOR}.{PATCH}[-{PRERELEASE}]`

**Examples**:

- `v1.0.0` - Production release
- `v1.2.3` - Regular update
- `v2.0.0-beta.1` - Pre-release
- `v1.5.4-hotfix` - Hotfix

### Release Workflow

**Regular Release**:

1. Create release branch: `release/1.2.0`
2. Update VERSION file: `echo "1.2.0" > VERSION`
3. Update CHANGELOG.md
4. Test and merge to `main`
5. Tag: `git tag -a v1.2.0 -m "Release 1.2.0"`
6. Push: `git push origin main --tags`

**Hotfix Release**:

1. Create hotfix branch: `hotfix/1.2.1` from `main`
2. Apply fix
3. Merge to `main` and tag
4. Merge back to `develop`

### CI/CD Automation

The CI/CD pipeline automatically:

- Validates tag format on push
- Checks VERSION file consistency
- Runs tests and security scans
- Deploys to staging (develop branch)
- Deploys to production (version tags)
- Creates GitHub releases

## Summary Checklist

Use this checklist to confirm you're ready for deployment:

### Configuration

- [ ] Column mappings reviewed and customized (`config/column_maps.yml`)
- [ ] Pricing files provided or example files confirmed (`data/pricing/`)
- [ ] Pricing paths configured (`config/pricing_config.yml`)
- [ ] DPD threshold confirmed (90/120/180 days) (`config/dpd_policy.yml`)
- [ ] Export path confirmed or changed (`config/export_config.yml`)

### Documentation

- [ ] Portfolio size expectations provided (for performance tuning)
- [ ] Security/PII requirements confirmed (`docs/security_constraints.md`)
- [ ] Versioning workflow reviewed (`docs/versioning.md`)

### Technical

- [ ] Schema validation passes (`python validators/schema_validator.py`)
- [ ] Export directories created (`mkdir -p abaco_runtime/exports`)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] CI/CD pipeline reviewed (`.github/workflows/ci.yml`)
- [ ] Pre-commit hooks set up (optional) (`pre-commit install`)

### Testing

- [ ] Test with small dataset first
- [ ] Verify output file formats
- [ ] Confirm PII masking works correctly
- [ ] Check export paths are correct

## Next Steps

1. **Review this document** and confirm all settings
2. **Provide feedback** on any items that need adjustment
3. **Test with sample data** to validate configuration
4. **Deploy to staging** environment first
5. **Monitor performance** and adjust settings as needed
6. **Deploy to production** after successful staging tests

## Contact

For questions or clarifications on any of these items, please:

- Open an issue in the GitHub repository
- Contact the development team
- Review the detailed documentation in the `docs/` folder

---

**Document Version**: 1.0.0  
**Last Updated**: 2024-12-03  
**Status**: Ready for Review
