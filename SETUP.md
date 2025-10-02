# Quick Setup Guide

## For Development/Testing

### Step 1: Environment Setup
```bash
# Clone and navigate
git clone https://github.com/Jeninefer/Commercial-View.git
cd Commercial-View

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment
```bash
# Copy template
cp .env.example .env

# Edit .env with your values
# Required:
#   GOOGLE_SHEETS_CREDS_PATH - path to service account JSON
#   AUX_SHEET_ID - Google Sheets ID
#   DESEMBOLSOS_RANGE - range for KAM data (e.g., DESEMBOLSOS!A1:AV5000)
#   DATA_SHEET_NAME - sheet name for LineaCredito (e.g., Data)
```

### Step 3: Test Features (No Data Required)
```bash
# Run the feature demonstration
python demo_features.py
```

This will show:
- ✓ Dynamic percentage calculations
- ✓ Tolerance check examples
- ✓ Target comparison scenarios
- ✓ Tenor mix analysis

### Step 4: Prepare Data Files

Place these files in the project root:
```
Abaco - Loan Tape_Loan Data_Table*.xlsx
Abaco - Loan Tape_Payment Schedule_Table*.xlsx
Abaco - Loan Tape_Historic Real Payment_Table*.xlsx
```

**Note:** Files can have suffixes like `(3).xlsx` - the script will find the newest.

### Step 5: Configure Targets

Edit `Q4_Targets.csv` with your actual targets:
```csv
Month,Outstanding_Target,Disbursement_Target,APR_Target,NPL_Target,Tenor_30_Target,Tenor_60_Target,Tenor_90_Target,Tenor_90plus_Target
2025-10-01,7800000,450000,18.5,2.5,25,35,25,15
```

### Step 6: Run ETL
```bash
python build_dashboard_payload.py
```

Expected output:
```
OK → /path/to/dashboard_payload.json

KPI Summary:
  Outstanding Portfolio: $7,610,000.00
  Active Clients: 145
  Outstanding vs Target: 97.5% (7,610,000.00 / 7,800,000.00)
  Within Tolerance: False
```

### Step 7: Deploy to Figma

1. Open Figma
2. Go to Widgets → New Widget
3. Copy all contents from `code.tsx`
4. Paste into Figma Widget editor
5. Save and run the widget
6. Copy contents of `dashboard_payload.json`
7. Paste into widget's text area
8. Click "Apply JSON"

## Troubleshooting

### Issue: "Missing one or more input files"
**Solution:** Ensure all three loan tape files are present with correct naming:
- Check file names start with expected prefixes
- Script looks for newest file with pattern matching

### Issue: Google Sheets authentication error
**Solution:** 
- Verify service account JSON path in `.env`
- Ensure service account has "Viewer" access to the sheet
- Check sheet ID is correct (from URL)

### Issue: No targets showing
**Solution:**
- Verify `Q4_Targets.csv` exists
- Check date format is `YYYY-MM-DD` (e.g., 2025-10-01)
- Ensure current month matches a row in the CSV

### Issue: All targets showing "outside tolerance"
**Solution:**
- Check if values are significantly different from targets
- Default tolerance is 1% - may need adjustment
- Review tolerance calculation in FEATURES.md

## File Checklist

After setup, your directory should contain:

```
Commercial-View/
├── .env                              ✓ Your configuration (not committed)
├── .env.example                      ✓ Template
├── .gitignore                        ✓ Excludes data files
├── Q4_Targets.csv                    ✓ Your targets
├── README.md                         ✓ Main documentation
├── FEATURES.md                       ✓ Feature reference
├── SETUP.md                          ✓ This file
├── requirements.txt                  ✓ Dependencies
├── build_dashboard_payload.py        ✓ ETL script
├── code.tsx                          ✓ Figma widget
├── demo_features.py                  ✓ Test script
├── dashboard_payload.json            ✓ Generated (not committed)
└── [Data files]                      ✓ Your loan tapes (not committed)
```

## Monthly Workflow

### 1st of each month:
1. Receive new loan tape files
2. Place in project directory
3. Update `Q4_Targets.csv` if targets changed
4. Run: `python build_dashboard_payload.py`
5. Copy new JSON to Figma widget
6. Review target status indicators
7. Share dashboard with stakeholders

### Quick Commands
```bash
# Update and run (all in one)
python build_dashboard_payload.py && cat dashboard_payload.json | pbcopy
# (On Linux use: xclip -selection clipboard)

# Check what changed
git diff Q4_Targets.csv
git log --oneline -5
```

## Customization

### Change Tolerance
Edit `build_dashboard_payload.py`:
```python
# Line 217 (APR)
within_tolerance(apr_pct, apr_target, tol=0.02)  # 2% tolerance

# Line 227 (NPL)
within_tolerance(npl_pct, npl_target, tol=0.005)  # 0.5% tolerance

# Line 291 (Tenor)
within_tolerance(current_val, target_val, tol=0.015)  # 1.5% tolerance
```

### Add New KPI
1. Calculate in `build_dashboard_payload.py`
2. Add to `payload` dictionary
3. Update `Payload` type in `code.tsx`
4. Add tile in Figma widget render
5. Update `Q4_Targets.csv` with new target column

### Change Colors
Edit `code.tsx`:
```typescript
// Line 77-81: Tile status colors
const statusColors = {
    good: "#10B981",    // Green
    warning: "#F59E0B", // Amber
    bad: "#EF4444"      // Red
};

// Line 3: Brand colors
// #030E19 (Dark Navy)
// #221248 (Purple)
// #6D7D8E (Gray)
// #FFFFFF (White)
```

## Support

For detailed feature documentation, see `FEATURES.md`
For general information, see `README.md`
For testing without data, run `demo_features.py`

## Next Steps

1. ✓ Run demo script to verify setup
2. ✓ Configure .env file
3. ✓ Edit Q4_Targets.csv
4. ✓ Place loan tape files
5. ✓ Run ETL script
6. ✓ Deploy to Figma
7. ✓ Share with team
