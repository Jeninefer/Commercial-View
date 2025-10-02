# Commercial-View
Principal KPI Dashboard

## Overview
A TypeScript-based KPI dashboard for commercial lending that dynamically calculates key performance indicators from CSV data files.

## Features

### Dynamic KPI Calculations
The dashboard pulls real data from CSV files and calculates:

1. **Outstanding Portfolio** - Sum of EOM balances from Payment Schedule
2. **Weighted APR** - APR weighted by current balance (sum of APR × balance / sum of balance)
3. **Tenor Mix** - Loan distribution across tenor buckets (0-12, 13-24, 25-36, 37+ months)
4. **Concentration** - Top customers by outstanding balance with percentage of portfolio
5. **NPL (Non-Performing Loans)** - Loans with Days Past Due > 90 days
6. **DPD (Days Past Due)** - Current vs late payments with average DPD
7. **Client Goals** - Total, new, recurring, and recovered clients

### Progress Tracking
Uses the corrected formula: `Math.round((current / target) * 100)` to calculate progress against Q4 targets.

## Data Files

The system reads from three CSV files in the `data/` directory:

- **payment_schedule.csv** - Payment history with EOM balances
- **loan_data.csv** - Loan details including APR, tenor, and customer information
- **historic_real_payment.csv** - Payment performance data with days past due

## Installation

```bash
npm install
```

## Usage

### Build the project
```bash
npm run build
```

### Run the KPI dashboard
```bash
npm start
```

### Run tests
```bash
npm test
```

## Project Structure

```
Commercial-View/
├── src/
│   ├── csvParser.ts         # CSV file parsing utilities
│   ├── kpiCalculations.ts   # KPI calculation functions
│   └── index.ts             # Main dashboard application
├── data/
│   ├── payment_schedule.csv
│   ├── loan_data.csv
│   └── historic_real_payment.csv
├── tests/
│   └── kpiCalculations.test.ts
└── README.md
```

## Key Functions

### `calcProgress(current: number, target: number): number`
Calculates progress percentage with proper rounding.

### `calculateOutstandingPortfolio(dataDir: string): number`
Sums the most recent EOM balance for each loan from Payment Schedule.

### `calculateWeightedAPR(dataDir: string): number`
Computes weighted average APR based on current balances.

### `calculateTenorMix(dataDir: string): { [bucket: string]: number }`
Groups active loans by tenor buckets.

### `calculateConcentration(dataDir: string)`
Identifies top customers by outstanding balance.

### `calculateNPL(dataDir: string)`
Counts and calculates percentage of non-performing loans (DPD > 90).

### `calculateDPD(dataDir: string)`
Analyzes payment performance and calculates average days past due.

### `calculateClientGoals(dataDir: string)`
Tracks client acquisition and retention metrics.

## License
ISC

