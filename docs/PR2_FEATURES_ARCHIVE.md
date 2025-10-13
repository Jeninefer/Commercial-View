# PR #2 Features Archive - TypeScript KPI Dashboard

## Overview

PR #2 implemented dynamic KPI calculations from CSV data sources (now closed).

## Key Features Implemented (TypeScript)

- **Dynamic CSV Integration**: payment_schedule.csv, loan_data.csv, historic_real_payment.csv
- **Outstanding Portfolio**: Sum of EOM balances from payment schedule
- **Weighted APR**: Balance-weighted average using formula: sum(APR × balance) / sum(balance)
- **Tenor Mix**: Loan distribution across tenor buckets (0-12, 13-24, 25-36, 37+ months)
- **Concentration Risk**: Customer ranking by outstanding balance
- **NPL Analysis**: Loans >90 days past due identification
- **DPD Metrics**: Days past due tracking and analysis
- **Progress Formula**: `Math.round((current / target) * 100)`

## Current Status

- PR #2: CLOSED (TypeScript implementation)
- Current System: Python-based (operational on main branch)

## Potential Integration

These KPI calculation concepts could be adapted for the current Python system if needed for future enhancements.
