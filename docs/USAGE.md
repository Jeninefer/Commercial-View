# Usage Examples

## Quick Start

### 1. Basic Setup

```bash
# Clone repository
git clone https://github.com/Jeninefer/Commercial-View.git
cd Commercial-View

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your API keys and settings
```

### 2. Run Analysis

```python
from ingestion import load_sample_data
from analysis import calculate_portfolio_kpis

# Load data
data = load_sample_data()

# Calculate KPIs
kpis = calculate_portfolio_kpis(data['loan_tape'])

print(f"Portfolio APR: {kpis['portfolio_apr']*100:.2f}%")
print(f"Active Loans: {kpis['active_loans']}")
print(f"Total Principal: ${kpis['total_principal']:,.2f}")
```

### 3. Run Optimization

```python
from optimization import optimize_disbursements

# Set available cash
available_cash = 1_000_000

# Optimize disbursements
result = optimize_disbursements(
    requests=data['disbursement_requests'],
    portfolio=data['loan_tape'],
    available_cash=available_cash,
    method='greedy'
)

print(f"Recommended {result['num_loans']} loans")
print(f"Total: ${result['total_disbursement']:,.2f}")
```

## Command Line Interface

### Run Main Application

```bash
# Run full analysis
python main.py --mode all

# Run only analysis
python main.py --mode analysis

# Run only optimization
python main.py --mode optimize

# Launch dashboard
python main.py --dashboard

# Start scheduler
python main.py --scheduler
```

### Run Dashboard Directly

```bash
streamlit run dashboard/app.py
```

Access at: http://localhost:8501

Default login:
- Admin: any username (not starting with "kam")
- KAM: username starting with "kam" (e.g., "kam1")

### Run Scheduler

```bash
# Run job immediately
python scheduler.py --now

# Start daily scheduler
python scheduler.py
```

## Docker Usage

### Build and Run

```bash
# Build image
docker build -t commercial-view .

# Run dashboard
docker run -p 8501:8501 -v $(pwd)/.env:/app/.env commercial-view

# Or use docker-compose
docker-compose up -d
```

### View Logs

```bash
docker-compose logs -f dashboard
docker-compose logs -f scheduler
```

## Google Drive Integration

### Setup Authentication

1. **Get OAuth Credentials:**
   - Go to Google Cloud Console
   - Create project and enable Drive API
   - Create OAuth 2.0 credentials (Desktop app)
   - Download as `credentials.json`

2. **Authenticate:**
   ```python
   from ingestion import GoogleDriveClient
   
   client = GoogleDriveClient()
   client.authenticate()  # Opens browser for auth
   ```

3. **Download Files:**
   ```python
   from ingestion import download_data_from_drive
   from pathlib import Path
   
   folder_url = "https://drive.google.com/drive/folders/your-folder-id"
   output_dir = Path("./data")
   
   result = download_data_from_drive(folder_url, output_dir)
   print(f"Downloaded {result['successful']} files")
   ```

### Read Google Sheets

```python
from ingestion import read_google_sheet

# Read entire sheet
data = read_google_sheet(
    sheet_id="your-sheet-id",
    worksheet_name="Sheet1"
)

# Convert to DataFrame
import pandas as pd
df = pd.DataFrame(data)
```

## AI Analysis

### Multi-Persona Insights

```python
from analysis import AIAnalyzer

# Create analyzer
analyzer = AIAnalyzer()

# Prepare data summary
data_summary = {
    'kpis': {
        'portfolio_apr': 0.18,
        'active_loans': 120,
        'total_principal': 5000000
    },
    'timestamp': '2024-01-15T08:00:00'
}

# Generate insights from specific persona
ceo_insight = analyzer.analyze_from_persona(
    persona_key='ceo',
    data_summary=data_summary
)

print(ceo_insight['analysis'])

# Or generate from all personas
insights = analyzer.generate_multi_persona_insights(data_summary)

# Get summary
summary = analyzer.summarize_insights(insights)
print(summary)
```

### Available Personas

- **ceo**: Strategic leadership perspective
- **cfo**: Financial oversight
- **cto**: Technology strategy
- **head_of_growth**: Customer acquisition
- **head_of_sales**: Revenue generation
- **head_of_marketing**: Brand and leads
- **treasury_manager**: Cash flow management
- **data_engineer**: Data infrastructure
- **bi_analyst**: Business intelligence

## Optimization Workflows

### Basic Optimization

```python
from optimization import DisbursementOptimizer

# Create optimizer
optimizer = DisbursementOptimizer(
    disbursement_requests=requests_df,
    current_portfolio=portfolio_df,
    available_cash=1_000_000
)

# Run optimization
result = optimizer.generate_recommendation(method='greedy')

# Format output
output = optimizer.format_recommendation(result)
print(output)
```

### Advanced: Custom Constraints

```python
# Filter requests by sector
tech_requests = requests_df[requests_df['sector'] == 'Technology']

# Optimize tech sector only
result = optimize_disbursements(
    requests=tech_requests,
    portfolio=portfolio_df,
    available_cash=500_000,
    method='lp'  # Linear programming for optimal solution
)
```

### Export Recommendations

```python
# Export to CSV
result['selected_loans'].to_csv('recommendations.csv', index=False)

# Export to Excel
result['selected_loans'].to_excel('recommendations.xlsx', index=False)

# Export to Google Sheets (requires setup)
from ingestion import GoogleSheetsClient

client = GoogleSheetsClient()
client.authenticate()
# Upload logic here
```

## KPI Analysis

### Calculate Specific KPIs

```python
from analysis import KPICalculator

calculator = KPICalculator(loan_tape_df)

# Individual KPIs
apr = calculator.calculate_portfolio_apr()
rotation = calculator.calculate_rotation_speed()
concentration = calculator.calculate_concentration_risk()
dpd = calculator.calculate_dpd_metrics()

print(f"APR: {apr*100:.2f}%")
print(f"Rotation: {rotation:.0f} days")
print(f"Client Concentration: {concentration['client']*100:.1f}%")
print(f"Average DPD: {dpd['avg_dpd']:.1f} days")
```

### Generate KPI Report

```python
# Get summary text
summary = calculator.get_kpi_summary()
print(summary)

# Save to file
with open('kpi_report.txt', 'w') as f:
    f.write(summary)
```

## Scheduling & Automation

### Configure Daily Job

Edit `.env`:
```bash
DAILY_JOB_TIME=08:00
TIMEZONE=America/Mexico_City
OUTPUT_FORMAT=csv
OUTPUT_DESTINATION=google_drive
```

### Custom Job Logic

```python
from scheduler import run_daily_job

# Run custom job
success = run_daily_job()

if success:
    print("Job completed successfully")
else:
    print("Job failed")
```

### Email Notifications

Configure in `.env`:
```bash
SENDGRID_API_KEY=your-key
NOTIFICATION_EMAIL_FROM=alerts@yourdomain.com
NOTIFICATION_EMAIL_TO=team@yourdomain.com
```

Notifications are sent automatically after each job.

## Dashboard Features

### Role-Based Access

```python
# In dashboard/app.py
def filter_data_by_role(data, user):
    if user['role'] == 'admin':
        return data
    elif user['role'] == 'kam':
        # KAM sees only their clients
        return data[data['kam'] == user['kam_id']]
    return data
```

### Custom Visualizations

```python
import plotly.express as px

# Sector distribution
fig = px.pie(
    sector_data,
    values='principal',
    names='sector',
    title='Portfolio Distribution'
)

# Timeline chart
fig = px.line(
    historical_data,
    x='date',
    y='revenue',
    title='Revenue Trend'
)
```

## Integration Examples

### HubSpot Integration

```python
import requests

HUBSPOT_API_KEY = "your-key"

# Create contact
url = "https://api.hubapi.com/contacts/v1/contact"
headers = {"Authorization": f"Bearer {HUBSPOT_API_KEY}"}

data = {
    "properties": [
        {"property": "firstname", "value": "John"},
        {"property": "phone", "value": "+1234567890"}
    ]
}

response = requests.post(url, json=data, headers=headers)
```

### AtomChat Messaging

```python
ATOMCHAT_API_KEY = "your-key"

# Send WhatsApp message
url = "https://api.atomchat.io/v1/messages/send"
headers = {"apiKey": ATOMCHAT_API_KEY}

data = {
    "to": "+1234567890",
    "template": "loan_approval",
    "variables": ["John", "$50000", "L12345"]
}

response = requests.post(url, json=data, headers=headers)
```

## Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test

```bash
pytest tests/test_optimization.py -v
```

### Run with Coverage

```bash
pytest tests/ --cov=. --cov-report=html
open htmlcov/index.html
```

## Troubleshooting

### Common Issues

**Module not found:**
```bash
pip install -r requirements.txt
```

**Port already in use:**
```bash
lsof -i :8501
kill -9 <PID>
```

**Google auth failed:**
```bash
rm token.json
python -c "from ingestion import GoogleDriveClient; GoogleDriveClient().authenticate()"
```

**API rate limit:**
- Implement exponential backoff
- Use caching
- Reduce concurrent requests

### Debug Mode

```python
import logging

logging.basicConfig(level=logging.DEBUG)

# Your code here
```

### Check Configuration

```python
from config import validate_config, get_config_summary

is_valid, errors = validate_config()
if not is_valid:
    print("Errors:", errors)

print(get_config_summary())
```

## Production Deployment

### Environment Setup

```bash
# Production .env
cp .env.example .env.production

# Set production values
export ENV=production
export DEBUG=false
export LOG_LEVEL=WARNING
```

### Deploy to Cloud

```bash
# Google Cloud Run
gcloud run deploy commercial-view \
  --source . \
  --platform managed \
  --region us-central1

# Render
git push origin main
# Auto-deploys from GitHub
```

### Monitoring

```python
import logging
import json

logger = logging.getLogger(__name__)

# Structured logging
logger.info(json.dumps({
    "event": "optimization_complete",
    "loans_approved": 15,
    "total_amount": 1000000,
    "timestamp": datetime.now().isoformat()
}))
```

## Advanced Usage

### Custom Optimization Weights

Edit `.env`:
```bash
WEIGHT_APR=0.30
WEIGHT_ROTATION_SPEED=0.25
WEIGHT_CONCENTRATION_RISK=0.20
WEIGHT_MOM_GROWTH=0.15
WEIGHT_DPD_MINIMIZATION=0.10
```

### Batch Processing

```python
import pandas as pd
from pathlib import Path

# Process multiple files
data_dir = Path("./data")

for file in data_dir.glob("*.csv"):
    df = pd.read_csv(file)
    kpis = calculate_portfolio_kpis(df)
    
    # Save results
    output = f"kpis_{file.stem}.json"
    pd.Series(kpis).to_json(output)
```

### API Endpoints (Future)

```python
from fastapi import FastAPI

app = FastAPI()

@app.post("/optimize")
async def optimize_endpoint(cash: float):
    data = load_sample_data()
    result = optimize_disbursements(
        data['disbursement_requests'],
        data['loan_tape'],
        cash
    )
    return result
```

## Support & Resources

- **Documentation**: See `/docs` folder
- **Examples**: See `examples/` (coming soon)
- **Issues**: Open on GitHub
- **Questions**: Contact team

---

**Built with ❤️ for ABACO - Standard is Excellence**
