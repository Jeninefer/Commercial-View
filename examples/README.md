# Commercial-View Examples

This directory contains example scripts demonstrating how to use the Commercial-View portfolio monitoring system.

## Running Examples

Make sure you have installed the dependencies first:

```bash
pip install -r requirements.txt
```

Then run any example from the repository root:

```bash
python examples/01_config_basics.py
python examples/02_alert_detection.py
python examples/03_portfolio_optimization.py
```

## Example Scripts

### 01_config_basics.py
Demonstrates how to load and access the manifest configuration including:
- Bucket definitions (APR, line size, client types)
- Optimizer constraints (target mix, hard limits, priority weights)
- Alert thresholds (concentration, risk, yield, liquidity, growth)

**Usage:**
```bash
python examples/01_config_basics.py
```

### 02_alert_detection.py
Shows how to use the AlertEngine for detecting portfolio anomalies:
- Concentration alerts (client exposure limits)
- Risk alerts (NPL growth, roll-rate spikes)
- Yield alerts (APR mix deviation, effective APR drops)
- Liquidity alerts (collections vs plan)
- Growth alerts (CAC/LTV ratio, payback period)

**Usage:**
```bash
python examples/02_alert_detection.py
```

### 03_portfolio_optimization.py
Demonstrates portfolio optimization with deal selection:
- Current portfolio analysis
- Candidate deal scoring
- Constraint-respecting selection
- Projected portfolio analysis
- Comparison to target mix

**Usage:**
```bash
python examples/03_portfolio_optimization.py
```

### 04_gdrive_integration.py
Shows Google Drive OAuth integration for file ingestion:
- Authentication flow
- Listing files with filters
- Downloading individual files
- Downloading entire folders

**Prerequisites:**
1. Install Google API libraries: `pip install google-auth google-auth-oauthlib google-api-python-client`
2. Create credentials.json from Google Cloud Console
3. Set GOOGLE_CREDENTIALS_PATH in .env

**Usage:**
```bash
python examples/04_gdrive_integration.py
```

## Output

Each example prints its results to the console. Some examples demonstrate:
- Alert detection output with severity levels
- Portfolio composition analysis
- Optimization results and recommendations
- API authentication and file listings

## Customization

Feel free to modify these examples to:
- Load actual portfolio data
- Adjust alert thresholds
- Test different optimization scenarios
- Integrate with your data sources
