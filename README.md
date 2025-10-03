# Commercial View Platform 💼

> A comprehensive cashflow management and disbursement optimization system for financial institutions

[![CI/CD Pipeline](https://github.com/Jeninefer/Commercial-View/actions/workflows/ci.yml/badge.svg)](https://github.com/Jeninefer/Commercial-View/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Deployment](#deployment)
- [API Integration](#api-integration)
- [Contributing](#contributing)
- [Support](#support)

## 🎯 Overview

Commercial View Platform is an enterprise-grade financial analysis and optimization system designed for ABACO. It provides:

- **Multi-objective disbursement optimization** - Intelligently recommends loan approvals based on APR, rotation speed, concentration risk, growth, and credit quality
- **AI-powered insights** - Multi-persona analysis from Executive, Financial, Growth, and Technical perspectives using OpenAI, Anthropic Claude, and Google Gemini
- **Real-time dashboards** - Interactive Streamlit-based interface with role-based access control
- **Automated workflows** - Daily batch processing with scheduled data ingestion and analysis
- **Native integrations** - Direct HubSpot-AtomChat connection for CRM and communication workflows

## ✨ Features

### Core Capabilities

#### 📊 Portfolio Analytics
- Real-time KPI calculations (APR, rotation speed, concentration risk, DPD metrics)
- Interactive visualizations with sector and status distributions
- Historical trend analysis and MoM growth tracking
- Risk assessment and concentration monitoring

#### 🎯 Disbursement Optimization
- Multi-objective optimization engine balancing 5 key KPIs
- Linear programming and greedy algorithm options
- Cash availability constraints
- Client and sector concentration limits
- Credit quality scoring integration

#### 🤖 AI Analysis
- Multi-LLM integration (OpenAI GPT-4, Anthropic Claude, Google Gemini)
- 9 distinct business personas:
  - **Executive**: CEO, CFO, CTO perspectives
  - **Growth**: Head of Growth, Sales, Marketing
  - **Operations**: Treasury Manager
  - **Technical**: Data Engineer, BI Analyst
- Automated insight generation and executive summaries

#### 🔐 Security & Access Control
- Role-based access control (RBAC)
- View-only role for Key Account Managers (KAMs)
- Secure credential management via .env
- OAuth 2.0 for Google Drive/Sheets integration

#### 📅 Automation
- Daily batch job at 8:00 AM
- Automated data ingestion from Google Drive
- Email notifications via SendGrid
- Export to "Firma Code" format
- Docker containerization for consistent deployment

## 🏗️ Architecture

```
Commercial-View/
├── config/              # Configuration and settings
├── ingestion/           # Data ingestion modules
│   ├── google_drive.py  # Google Drive OAuth & download
│   ├── google_sheets.py # Google Sheets API integration
│   └── csv_reader.py    # CSV fallback reader
├── analysis/            # Analytics and AI modules
│   ├── ai_analyzer.py   # Multi-LLM AI analysis
│   └── kpi_calculator.py # KPI computation
├── optimization/        # Disbursement optimization
│   └── disbursement_optimizer.py
├── dashboard/           # Streamlit dashboard
│   └── app.py
├── scheduler.py         # Daily batch job scheduler
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Multi-container orchestration
└── requirements.txt     # Python dependencies
```

## 🚀 Installation

### Prerequisites

- Python 3.11 or higher
- Docker (optional, for containerized deployment)
- Google Cloud account (for Drive/Sheets access)
- API keys for OpenAI, Anthropic, and/or Google Gemini

### Local Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Jeninefer/Commercial-View.git
   cd Commercial-View
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

### Docker Installation

1. **Build the image**
   ```bash
   docker build -t commercial-view .
   ```

2. **Run with docker-compose**
   ```bash
   docker-compose up -d
   ```

## ⚙️ Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

#### Google Drive & Sheets
```env
GOOGLE_DRIVE_FOLDER_URL=https://drive.google.com/drive/folders/your-folder-id
GOOGLE_SHEETS_ID=your-google-sheets-id
```

#### AI API Keys
```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_CLOUD_PROJECT_ID=your-project-id
```

#### HubSpot & AtomChat
```env
HUBSPOT_API_KEY=your-key
ATOMCHAT_API_KEY=your-key
```

#### Optimization Parameters
```env
WEIGHT_APR=0.25
WEIGHT_ROTATION_SPEED=0.20
WEIGHT_CONCENTRATION_RISK=0.20
WEIGHT_MOM_GROWTH=0.20
WEIGHT_DPD_MINIMIZATION=0.15

MAX_CLIENT_CONCENTRATION=0.15
MAX_SECTOR_CONCENTRATION=0.30
```

### Google Drive Authentication

First-time setup requires OAuth 2.0 authentication:

1. **Get OAuth credentials**
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a project and enable Drive API and Sheets API
   - Create OAuth 2.0 credentials (Desktop app)
   - Download as `credentials.json` and place in project root

2. **Authenticate**
   ```bash
   python -c "from ingestion import GoogleDriveClient; client = GoogleDriveClient(); client.authenticate()"
   ```
   This will open a browser for authentication. After approval, a `token.json` file is saved for future use.

## 📖 Usage

### Running the Dashboard

```bash
streamlit run dashboard/app.py
```

Access at `http://localhost:8501`

**Default Login:**
- Admin user: Any username/password (not starting with "kam")
- KAM user: Username starting with "kam" (e.g., "kam1")

### Running the Daily Batch Job

**Run immediately:**
```bash
python scheduler.py --now
```

**Start scheduler (runs daily at configured time):**
```bash
python scheduler.py
```

### Using the Optimization Engine

```python
from optimization import optimize_disbursements
from ingestion import load_sample_data

# Load data
data = load_sample_data()
loan_tape = data['loan_tape']
requests = data['disbursement_requests']

# Optimize
result = optimize_disbursements(
    requests=requests,
    portfolio=loan_tape,
    available_cash=1000000,
    method='greedy'  # or 'lp'
)

print(f"Recommended {result['num_loans']} loans")
print(f"Total: ${result['total_disbursement']:,.2f}")
```

### Generating AI Insights

```python
from analysis import analyze_data

data_summary = {
    'kpis': {
        'portfolio_apr': 0.18,
        'active_loans': 120,
        'total_principal': 5000000
    }
}

insights = analyze_data(data_summary)
print(insights['summary'])
```

## 🐳 Deployment

### Docker Deployment

The application is fully containerized for consistent deployment:

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Cloud Deployment Options

#### Streamlit Community Cloud
1. Push to GitHub
2. Connect at [share.streamlit.io](https://share.streamlit.io)
3. Add secrets in dashboard settings

#### Render
1. Connect GitHub repository
2. Select "Web Service"
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `streamlit run dashboard/app.py`
5. Add environment variables

#### Google Cloud Run
```bash
gcloud run deploy commercial-view \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## 🔗 API Integration

### HubSpot-AtomChat Native Integration

The platform documents native integration workflows between HubSpot and AtomChat.io for automated conversational campaigns:

**Workflow Setup:**
1. Configure AtomChat integration in HubSpot
2. Create workflow in HubSpot with trigger conditions
3. Add AtomChat action (WhatsApp Business message)
4. Map HubSpot contact properties to message templates

**Benefits:**
- Real-time CRM synchronization
- No third-party connectors needed
- Maximum reliability and data consistency

### Example Automation Workflows

#### 1. Lead Generation (Facebook/Instagram → HubSpot)
- Trigger: New lead form submission on Meta ads
- Action: Create/update HubSpot contact
- Result: Instant notification to sales team

#### 2. Email Tracking (Gmail ↔ HubSpot)
- Use HubSpot Sales Chrome Extension
- Automatically log emails to CRM
- Real-time open notifications
- View contact info in Gmail sidebar

#### 3. Design Handoff (Figma → HubSpot)
- Trigger: Design marked #approved in Figma
- Action: Create task in HubSpot for marketing team
- Result: Seamless design-to-campaign workflow

## 🎨 Brand Guidelines

The platform adheres to ABACO's official brand guidelines:

### Color Palette
- **Primary Dark**: `#030E19`, `#221248`
- **Neutrals**: `#6D7D8E`, `#9EA9B3`, `#CED4D9`
- **Contrast**: `#FFFFFF`

### Logo Usage
- Use official ABACO logo and isotype as specified in brand guide
- Maintain proper spacing and sizing
- Never distort or recolor

## 🧪 Testing

Run tests with pytest:

```bash
pytest tests/ -v
```

Run with coverage:

```bash
pytest tests/ --cov=. --cov-report=html
```

## 📝 Contributing

This is a proprietary project for ABACO. For internal contributors:

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and commit: `git commit -am 'Add feature'`
3. Push to branch: `git push origin feature/your-feature`
4. Create Pull Request

### Code Standards
- Follow PEP 8 style guide
- Use Black for formatting
- Add docstrings to all functions
- Write tests for new features

## 🐛 Troubleshooting

### Common Issues

**Google Drive Authentication Failed**
- Ensure `credentials.json` is in project root
- Delete `token.json` and re-authenticate
- Verify APIs are enabled in Google Cloud Console

**API Rate Limits**
- OpenAI: Reduce concurrent requests
- Google: Implement exponential backoff
- Anthropic: Check quota limits

**Docker Container Fails**
- Check logs: `docker-compose logs`
- Verify `.env` file is present
- Ensure ports are not in use

## 📊 KPI Definitions

### Portfolio APR
Weighted average Annual Percentage Rate across active loans, weighted by principal amount.

### Rotation Speed
Average term length (in days) of active loans, indicating how quickly capital rotates through the portfolio.

### Concentration Risk
Maximum exposure to any single client or sector as percentage of total portfolio.

### DPD (Days Past Due)
Average number of days loans are overdue. Lower is better.

### MoM Growth
Month-over-Month revenue growth percentage.

## 📧 Support

For questions or support:
- **Technical Issues**: Create an issue on GitHub
- **Business Inquiries**: Contact ABACO team
- **Security Concerns**: Email security@abaco.com

## 📄 License

Proprietary and confidential. © 2024 ABACO. All rights reserved.

---

**Built with ❤️ for ABACO - Standard is Excellence**
