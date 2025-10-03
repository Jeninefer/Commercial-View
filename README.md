# ABACO Core Library

**ABACO Core** is a Python library for commercial lending operations, providing:
- **Portfolio Optimization**: Disbursement planning with target mix and hard limits
- **Alert Engine**: Statistical anomaly detection (EWMA, CUSUM, MAD-z) with Slack integration
- **Data Ingestion**: Google Drive OAuth integration for secure file downloads

## Installation

```bash
pip install -e .
```

### Optional Dependencies

For Google Drive ingestion:
```bash
pip install -e ".[ingestion]"
```

For Slack alerts:
```bash
pip install -e ".[alerts]"
```

For development:
```bash
pip install -e ".[dev]"
```

## Quick Start

### 1. Manifest & Buckets

```python
from abaco_core import bucket_apr, bucket_line, classify_client, map_naics

# Classify APR and line amounts
apr_bucket = bucket_apr(18.5)  # "15-20%"
line_bucket = bucket_line(350_000)  # "250k-500k"

# Classify clients
client_type = classify_client(revenue=25_000_000, years_in_business=5)  # "growing"

# Map NAICS codes
industry = map_naics("541512")  # "Professional, Scientific, and Technical Services"
```

### 2. Disbursement Optimizer

```python
import pandas as pd
from abaco_core.optimizer import DisbursementOptimizer

# Define target portfolio mix
optimizer = DisbursementOptimizer(
    target_apr_mix={"15-20%": 30, "20-25%": 40, "25-30%": 30},
    payer_a_min=0.30,  # Minimum 30% A-grade payers
    payer_d_max=0.15,  # Maximum 15% D-grade payers
    industry_max_share=0.25,  # Max 25% per industry
    top_client_max=0.15,  # Max 15% for top client
)

# Prepare request data
requests = pd.DataFrame({
    "amount": [100_000, 250_000, 500_000],
    "apr": [18.0, 22.5, 28.0],
    "industry": ["Manufacturing", "Retail", "Services"],
    "payer_grade": ["A", "B", "A"],
    "customer_id": ["C001", "C002", "C003"],
})

current_portfolio = pd.DataFrame()  # Your existing portfolio

# Optimize selection
selected, report = optimizer.optimize(
    requests=requests,
    current_portfolio=current_portfolio,
    aum_target=5_000_000,
)

print(f"Selected {report['selected_count']} requests totaling ${report['selected_amount']:,.0f}")
print(f"Budget utilization: {report['utilization']:.1f}%")
```

### 3. Alert Engine

```python
import pandas as pd
from abaco_core.alerts import AlertEngine

engine = AlertEngine()

# Concentration alerts
exposures = pd.Series({"C001": 1_500_000, "C002": 800_000, "C003": 600_000})
alerts = engine.concentration_alerts(exposures)

# Risk alerts
alerts += engine.risk_alerts(
    npl180_mom_bps=75,  # NPL 180+ increased 75 bps
    dpd_7d_growth=1.8,  # DPD growing 1.8x
)

# Yield alerts
apr_mix = pd.Series({"15-20%": 25, "20-25%": 35, "25-30%": 40})
alerts += engine.yield_alerts(
    apr_mix=apr_mix,
    target_apr_mix={"15-20%": 30, "20-25%": 40, "25-30%": 30},
)

# Liquidity alerts
alerts += engine.liquidity_alerts(
    collections_vs_plan=0.85,  # 85% of plan
    bank_shortfall=False,
)

# Growth alerts
alerts += engine.growth_alerts(
    ltv_over_3_cac=True,
    payback_months=16,
)

# Post to Slack
engine.post_to_slack(alerts)  # Uses SLACK_WEBHOOK_URL env var
```

### 4. Google Drive Ingestion

```python
from pathlib import Path
from abaco_core.ingestion.google_drive import download_folder

# First run opens browser for OAuth consent
# Subsequent runs use cached token.json
files = download_folder(
    folder_id="1qIg_BnIf_IWYcWqCuvLaYU_Gu4C2-Dj8",
    out_dir=Path("./abaco_runtime/drive_sync"),
    client_secret_json=Path("./client_secret.json"),
)

print(f"Downloaded {len(files)} files")
```

## Configuration

Create a `.env` file from `.env.template`:

```bash
cp .env.template .env
```

Fill in required values:
- `SLACK_WEBHOOK_URL`: For posting alerts
- `GOOGLE_APPLICATION_CREDENTIALS`: Optional, for service account auth

**Important**: Never commit `.env`, `token.json`, or `client_secret.json` to version control.

## Core Concepts

### Buckets & Classification

- **APR Buckets**: 0-15%, 15-20%, 20-25%, 25-30%, 30%+
- **Line Buckets**: 0-100k, 100k-250k, 250k-500k, 500k-1M, 1M-5M, 5M+
- **Payer Grades**: A (excellent), B (good), C (fair), D (poor)
- **Client Types**: startup, growing, enterprise

### Optimizer Hard Limits

- **Top Client Max**: Maximum exposure to single client (default 15%)
- **Industry Max**: Maximum exposure to single industry (default 25%)
- **Payer A Min**: Minimum A-grade payers in portfolio (default 30%)
- **Payer D Max**: Maximum D-grade payers in portfolio (default 15%)

### Alert Detection Methods

- **EWMA**: Exponentially Weighted Moving Average for trend detection
- **CUSUM**: Cumulative Sum for detecting sustained shifts
- **MAD-z**: Median Absolute Deviation z-score (robust to outliers)

## Project Structure

```
abaco_core/
├── __init__.py          # Package exports
├── manifest.py          # Buckets, client types, NAICS scheme
├── optimizer.py         # Disbursement optimization
├── alerts.py            # Alert engine with Slack integration
└── ingestion/
    ├── __init__.py
    └── google_drive.py  # Google Drive OAuth integration
```

## Security Notes

1. **No secrets in code**: Use environment variables
2. **Rotate exposed keys**: Any keys in problem statement should be rotated
3. **OAuth best practice**: User OAuth for Drive, not service accounts in code
4. **RBAC**: Enforce role-based access at application layer (not library)

## License

MIT
