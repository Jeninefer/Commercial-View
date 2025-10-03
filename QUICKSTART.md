# ABACO Core - Quick Reference

## Installation

```bash
pip install -e .
pip install -e ".[alerts,ingestion,dev]"  # All optional dependencies
```

## Common Imports

```python
from abaco_core import bucket_apr, bucket_line, classify_client
from abaco_core.optimizer import DisbursementOptimizer
from abaco_core.alerts import AlertEngine
from abaco_core.ingestion.google_drive import download_folder
```

## Quick Examples

### 1. Classify Portfolio Items

```python
from abaco_core import bucket_apr, bucket_line, bucket_payer

apr_bucket = bucket_apr(18.5)           # "15-20%"
line_bucket = bucket_line(350_000)      # "250k-500k"
payer = bucket_payer(12.0)              # "B"
```

### 2. Optimize Disbursements

```python
optimizer = DisbursementOptimizer(
    target_apr_mix={"15-20%": 30, "20-25%": 40, "25-30%": 30},
    payer_a_min=0.30,
    top_client_max=0.15,
)

selected, report = optimizer.optimize(
    requests=pending_df,
    current_portfolio=portfolio_df,
    aum_target=10_000_000,
)

print(f"Selected: {report['selected_count']} requests")
print(f"Amount: ${report['selected_amount']:,.0f}")
```

### 3. Generate Alerts

```python
engine = AlertEngine()

alerts = []
alerts += engine.concentration_alerts(exposures_by_client)
alerts += engine.risk_alerts(npl180_mom_bps=75)
alerts += engine.yield_alerts(apr_mix, target_apr_mix)
alerts += engine.liquidity_alerts(collections_vs_plan=0.85, bank_shortfall=False)

engine.post_to_slack(alerts)  # Requires SLACK_WEBHOOK_URL env var
```

### 4. Download from Google Drive

```python
from pathlib import Path
from abaco_core.ingestion.google_drive import download_folder

files = download_folder(
    folder_id="YOUR_FOLDER_ID",
    out_dir=Path("./data"),
    client_secret_json=Path("./client_secret.json"),
)
```

## DataFrame Schema

### Portfolio / Requests DataFrame

```python
pd.DataFrame({
    "amount": [100_000, 250_000],          # Required
    "apr": [18.5, 22.0],                   # Required
    "industry": ["Tech", "Retail"],        # Required
    "payer_grade": ["A", "B"],             # Required (A, B, C, or D)
    "customer_id": ["C001", "C002"],       # Required
})
```

## Environment Variables

Create `.env` from `.env.template`:

```bash
cp .env.template .env
```

Required for Slack alerts:
```
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```

Required for Google Drive (alternative to OAuth):
```
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

## Buckets Reference

### APR Buckets
- 0-15%
- 15-20%
- 20-25%
- 25-30%
- 30%+

### Line Amount Buckets
- 0-100k
- 100k-250k
- 250k-500k
- 500k-1M
- 1M-5M
- 5M+

### Payer Grades
- A: 0-5% DPD history (Excellent)
- B: 5-15% DPD history (Good)
- C: 15-30% DPD history (Fair)
- D: 30%+ DPD history (Poor)

### Client Types
- **Startup**: Revenue < $5M, Years ≤ 3
- **Growing**: $5M ≤ Revenue < $50M, Years > 3
- **Enterprise**: Revenue ≥ $50M

## Hard Limits (Default)

```python
DisbursementOptimizer(
    payer_a_min=0.30,           # Min 30% A-grade payers
    payer_d_max=0.15,           # Max 15% D-grade payers
    industry_max_share=0.25,    # Max 25% per industry
    top_client_max=0.15,        # Max 15% for top client
)
```

## Alert Thresholds (Default)

```python
AlertEngine(
    ewma_alpha=0.3,             # EWMA smoothing factor
    cusum_threshold=5.0,        # CUSUM shift detection
    mad_z_threshold=3.0,        # MAD z-score threshold
)
```

## Running Examples

```bash
# Daily portfolio report
python examples/daily_report.py

# Google Drive ingestion (configure first)
python examples/drive_ingestion.py
```

## Running Tests

```bash
pytest tests/ -v                    # All tests
pytest tests/ -v --cov=abaco_core   # With coverage
```

## Project Structure

```
abaco_core/
├── __init__.py          # Package exports
├── manifest.py          # Buckets & classification
├── optimizer.py         # Disbursement optimization
├── alerts.py            # Alert engine
└── ingestion/
    └── google_drive.py  # Google Drive integration
```

## Support

- Full documentation: `README.md`
- Implementation details: `IMPLEMENTATION.md`
- Examples: `examples/`
- Tests: `tests/`

## Security Notes

⚠️ **Never commit:**
- `.env` (environment variables)
- `token.json` (Google OAuth token)
- `client_secret.json` (Google OAuth client)
- Any API keys or credentials

✅ **Always:**
- Use `.env.template` as a reference
- Rotate any exposed keys immediately
- Keep `.gitignore` up to date
