# Commercial-View
Principal KPI Dashboard with Dynamic Target Tracking

## Overview

This repository contains a complete ETL pipeline and Figma Widget for tracking commercial KPIs with dynamic target comparisons. The system processes loan data from Excel/CSV files and Google Sheets, calculates key metrics, compares them against quarterly targets with tolerance checks, and provides a visual dashboard in Figma.

## Key Features

### 1. Dynamic Target Tracking
- **Percentage Calculation**: Automatically calculates achievement percentage (e.g., if Oct EOM = $7.61M and target = $7.80M, displays 97.5%)
- **Tolerance Checks**: Validates if APR, tenor mix, and NPL are within acceptable tolerances (default 1%)
- **Configurable Targets**: Q4 targets stored in `Q4_Targets.csv` for easy month-to-month updates

### 2. Executive KPIs
- Outstanding Portfolio with target comparison
- Active Clients count
- Weighted APR with tolerance validation
- NPL ≥180 days (non-performing loans)
- Top-10 Client Concentration

### 3. Time Series Analysis
- Monthly disbursements with line chart visualization
- Active, new, recurrent, and recovered client tracking
- Revenue collection rates

### 4. Segmentation
- KAM (Key Account Manager) breakdown
- Tenor mix by bucket (≤30, 31-60, 61-90, >90 days)
- Industry/sector distribution

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Google Cloud service account with Sheets API access
- Figma account (for widget deployment)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Jeninefer/Commercial-View.git
cd Commercial-View
```

2. **Create and activate virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your actual values:
# - GOOGLE_SHEETS_CREDS_PATH: path to your service account JSON
# - AUX_SHEET_ID: your Google Sheets ID
# - DESEMBOLSOS_RANGE: range for KAM mappings
# - DATA_SHEET_NAME: sheet name for LineaCredito data
```

5. **Prepare data files**
Place the following files in the project root:
- `Abaco - Loan Tape_Loan Data_Table*.xlsx` (or .csv)
- `Abaco - Loan Tape_Payment Schedule_Table*.xlsx` (or .csv)
- `Abaco - Loan Tape_Historic Real Payment_Table*.xlsx` (or .csv)

6. **Configure targets**
Edit `Q4_Targets.csv` with your quarterly targets:
- Outstanding_Target: Target portfolio value
- Disbursement_Target: Target monthly disbursements
- APR_Target: Target weighted APR percentage
- NPL_Target: Target NPL percentage
- Tenor_*_Target: Target tenor mix percentages

## Usage

### Running the ETL Pipeline

```bash
python build_dashboard_payload.py
```

This will:
1. Load the latest loan data files
2. Connect to Google Sheets for KAM and LineaCredito mappings
3. Calculate all KPIs and comparisons
4. Generate `dashboard_payload.json`
5. Display a summary in the console

**Output example:**
```
OK → /path/to/dashboard_payload.json

KPI Summary:
  Outstanding Portfolio: $7,610,000.00
  Active Clients: 145
  Outstanding vs Target: 97.5% (7,610,000.00 / 7,800,000.00)
  Within Tolerance: False
```

### Using the Figma Widget

1. **Open Figma** and create a new Widget project
2. **Copy the contents** of `code.tsx`
3. **Paste into** Figma Widget code editor
4. **Run the widget** in your Figma file
5. **Copy the contents** of `dashboard_payload.json`
6. **Paste into** the text area in the widget
7. **Click "Apply JSON"** to render the dashboard

The widget will display:
- Executive KPI tiles with color-coded target status (green = within tolerance, yellow = outside tolerance)
- Monthly disbursements line chart
- KAM breakdown table
- Tenor mix with target comparisons
- Target status summary panel

## File Structure

```
Commercial-View/
├── README.md                        # This file
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variable template
├── .gitignore                       # Git ignore rules
├── Q4_Targets.csv                   # Quarterly targets configuration
├── build_dashboard_payload.py       # Main ETL script
├── code.tsx                         # Figma Widget code
├── dashboard_payload.json           # Generated output (gitignored)
└── [Data files]                     # Loan tape files (gitignored)
```

## Target Tolerance Logic

The system uses a `within_tolerance()` function with 1% default tolerance:

```python
within_tolerance(value, target, tol=0.01)
# Returns True if: |value - target| ≤ tol × target
```

This applies to:
- **APR**: Current weighted APR vs target APR
- **NPL**: Current NPL percentage vs target NPL percentage  
- **Tenor Mix**: Each bucket's percentage vs target percentage

## Q4 Targets CSV Format

```csv
Month,Outstanding_Target,Disbursement_Target,APR_Target,NPL_Target,Tenor_30_Target,Tenor_60_Target,Tenor_90_Target,Tenor_90plus_Target
2025-10-01,7800000,450000,18.5,2.5,25,35,25,15
2025-11-01,8200000,450000,18.5,2.5,25,35,25,15
2025-12-01,8500000,370000,18.5,2.5,25,35,25,15
```

## Google Sheets Requirements

### DESEMBOLSOS Sheet
Required columns:
- Customer ID (or ClienteID, CustomerID, customer_id)
- KAM (or Ejecutivo, Account Manager)

### Data Sheet
Required columns:
- Customer ID (or CustomerID, customer_id)
- LineaCredito (or Line of Credit, LineaCreditoUSD)

## Troubleshooting

### Missing files error
Ensure all three loan tape files are present with the correct naming pattern:
- `Abaco - Loan Tape_Loan Data_Table*`
- `Abaco - Loan Tape_Payment Schedule_Table*`
- `Abaco - Loan Tape_Historic Real Payment_Table*`

### Google Sheets authentication error
- Verify service account JSON path in `.env`
- Ensure service account has access to the specified Google Sheet
- Check that the sheet ID and ranges are correct

### Invalid JSON in Figma
- Ensure `dashboard_payload.json` is valid JSON
- Check for any encoding issues
- Copy the entire file contents without modification

## Maintenance

### Monthly Updates
1. Place new loan tape files in the project directory
2. Run `python build_dashboard_payload.py`
3. Update Figma widget with new JSON

### Quarterly Target Updates
1. Edit `Q4_Targets.csv` with new targets
2. Re-run the ETL pipeline
3. Dashboard will automatically reflect new comparisons

## License

This project is proprietary and confidential.

## Support

For issues or questions, please contact the repository maintainer.
