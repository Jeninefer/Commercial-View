# Commercial-View

A production-quality portfolio monitoring and optimization framework for commercial lending portfolios. Provides real-time alert detection, risk metrics, portfolio optimization, and automated reporting.

## Features

- **Portfolio Schema & Constraints**: Comprehensive bucket definitions for APR, line size, client types, industries, and payers
- **Alert Detection**: Statistical anomaly detection using EWMA, CUSUM, and MAD-z methods
- **Slack Integration**: Automated alert posting using Slack Block Kit
- **Portfolio Optimizer**: Dependency-light optimizer honoring target mix and hard limits
- **Google Drive Integration**: Local-first OAuth ingestion (no hardcoded secrets)
- **Production-Ready**: Clean architecture, comprehensive documentation, no demo data

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Jeninefer/Commercial-View.git
cd Commercial-View
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.template .env
# Edit .env with your Slack webhook URL and Google credentials path
```

## Configuration

### Manifest Schema

The `abaco_manifest.json` file defines the portfolio structure and constraints:

- **Buckets**: APR ranges (15-20% to >70%), line sizes (<=3k to >250k)
- **Client Types**: NEW, RECURRENT, RECOVERED, MICRO, SMALL, MEDIUM, CORPORATE
- **Industry Scheme**: Custom or NAICS2 classification
- **Payer Buckets**: Concentration tracking (Top1, Top10, Rest, by percentage)

### Optimizer Constraints

- **Target Mix**: Desired distribution across APR, line size, industry, and payers
- **Hard Limits**: Maximum concentration thresholds that cannot be violated
- **Priority Weights**: Relative importance of APR fit (60%), term fit (35%), and diversification (5%)

### Alert Thresholds

- **Concentration**: Top-1 client max 4%, growth tracking at 25 bps
- **Risk**: NPL≥180 monitoring, roll-rate spike detection, DPD growth alerts
- **Yield**: APR mix deviation (3σ), EWMA bands with 100 bps drop threshold
- **Liquidity**: Collections vs plan (-10%), bank shortfall flags
- **Growth**: CAC/LTV ratio monitoring, payback period thresholds

## Usage

### Configuration Management

```python
from abaco_core import Config

# Load manifest
config = Config()

# Access buckets
apr_buckets = config.get("apr_buckets")
client_types = config.get("client_type")

# Access optimizer constraints
optimizer_config = config.optimizer
target_mix = optimizer_config["target_mix"]
hard_limits = optimizer_config["hard_limits"]

# Access alert thresholds
alert_rules = config.alerts
concentration_rules = alert_rules["concentration"]
```

### Alert Detection

```python
from abaco_core import AlertEngine
import pandas as pd

# Initialize alert engine
engine = AlertEngine()

# Concentration alerts
exposures = pd.Series({"client_A": 50000, "client_B": 30000, "client_C": 20000})
alerts = engine.concentration_alerts(exposures)

# Risk alerts
rollrates_hist = pd.DataFrame({
    "from_bucket": ["30-60", "30-60", "30-60", "60-90", "60-90", "60-90"],
    "to_bucket": ["60-90", "60-90", "60-90", "90-120", "90-120", "90-120"],
    "value": [0.05, 0.06, 0.15, 0.10, 0.12, 0.25]  # Last value is spike
})
alerts = engine.risk_alerts(
    npl180_mom_bps=60,
    rollrates_hist=rollrates_hist,
    dpd_7d_growth_amt=0.25
)

# Yield alerts
apr_mix = pd.Series([35.5, 36.0, 35.8, 38.5])  # Last value deviates
apr_effective = pd.Series([34.2, 34.5, 34.3, 32.1])  # Last value drops
alerts = engine.yield_alerts(apr_mix, apr_effective)

# Post to Slack
engine.post_to_slack(alerts)
```

### Portfolio Optimization

```python
from abaco_core.optimizer import PortfolioOptimizer
import pandas as pd

# Initialize optimizer
optimizer = PortfolioOptimizer()

# Prepare candidate deals
candidates = pd.DataFrame({
    "deal_id": ["D001", "D002", "D003"],
    "amount": [25000, 50000, 75000],
    "apr_bucket": ["35-40", "40-45", "30-35"],
    "line_bucket": ["<=50k", "<=100k", ">100k"],
    "industry": ["Manufacturing", "Retail", "Services"],
    "payer_id": ["P1", "P2", "P3"],
    "term_months": [12, 18, 15]
})

# Current portfolio
current = pd.DataFrame({
    "deal_id": ["D100", "D101"],
    "amount": [100000, 150000],
    "apr_bucket": ["35-40", "40-45"],
    "line_bucket": ["<=100k", ">100k"],
    "industry": ["Manufacturing", "Services"],
    "payer_id": ["P10", "P11"],
    "term_months": [12, 15]
})

# Optimize selection
selected = optimizer.optimize(candidates, current, max_amount=100000)

# Analyze portfolio
analysis = optimizer.analyze_portfolio(pd.concat([current, selected]))
print(analysis)
```

### Google Drive Ingestion

```python
from abaco_core.gdrive_ingest import GoogleDriveIngestor
from pathlib import Path

# Initialize (will prompt for OAuth on first use)
ingestor = GoogleDriveIngestor()

# List files in a folder
files = ingestor.list_files(
    folder_id="your_folder_id",
    mime_type="text/csv",
    name_contains="portfolio"
)

# Download a specific file
content = ingestor.download_file(
    file_id="your_file_id",
    output_path=Path("./data/portfolio.csv")
)

# Download entire folder
downloaded = ingestor.download_folder(
    folder_id="your_folder_id",
    output_dir=Path("./data"),
    mime_type="text/csv"
)
```

## Security

### Environment Variables

All secrets must be stored in `.env` (never committed):

```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
GOOGLE_CREDENTIALS_PATH=credentials.json
```

### Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google Drive API
4. Create OAuth 2.0 credentials (Desktop application)
5. Download credentials as `credentials.json`
6. Place in project root (excluded from git by `.gitignore`)

### Slack Webhook Setup

1. Go to [Slack API](https://api.slack.com/messaging/webhooks)
2. Create an incoming webhook for your workspace
3. Copy webhook URL to `.env`

## Architecture

```
Commercial-View/
├── abaco_manifest.json       # Portfolio schema and constraints
├── abaco_core/               # Core package
│   ├── __init__.py           # Package initialization
│   ├── config.py             # Configuration management
│   ├── alerts.py             # Alert detection engine
│   ├── optimizer.py          # Portfolio optimizer
│   └── gdrive_ingest.py      # Google Drive integration
├── requirements.txt          # Python dependencies
├── .env.template             # Environment variables template
├── .gitignore                # Git exclusions (secrets, artifacts)
└── README.md                 # This file
```

## Alert Detection Methods

### EWMA (Exponentially Weighted Moving Average)
Detects deviations from historical trends with recent data weighted more heavily. Used for yield monitoring and APR tracking.

### CUSUM (Cumulative Sum Control Chart)
Detects subtle shifts in process mean. Used for roll-rate spike detection where changes accumulate over time.

### MAD-z (Median Absolute Deviation Z-score)
Robust outlier detection resistant to extreme values. Used for APR mix deviation alerts.

## Optimizer Algorithm

The portfolio optimizer uses a greedy selection algorithm with multi-factor scoring:

1. **Scoring**: Each candidate deal receives a composite score based on:
   - APR fit (60%): How well it moves portfolio toward target mix
   - Term fit (35%): Preference for 12-18 month terms
   - Diversification (5%): Preference for smaller deals

2. **Selection**: Deals are selected in score order while:
   - Respecting maximum allocation budget
   - Honoring all hard limit constraints
   - Maintaining concentration limits

3. **Validation**: Final portfolio checked against all constraints

## License

Copyright (c) 2024. All rights reserved.

## Support

For issues and questions, please open an issue on GitHub.
