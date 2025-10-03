# Commercial-View
Principal KPI - DPD Bucket Classification System

## Overview

This repository provides a consistent and well-documented system for classifying commercial loans based on Days Past Due (DPD). The system implements two complementary approaches for different analytical purposes:

1. **PaymentProcessor** - Accounting/Regulatory Default (180+ days)
2. **FeatureEngineer** - Risk Analysis/High Risk (90+ days)

## DPD Classification Framework

### PaymentProcessor (Accounting Default: 180+ Days)

The `PaymentProcessor` class uses a **dpd_threshold of 180 days** (configurable) to mark `default_flag`. This represents the technical accounting and regulatory definition of default.

**Purpose**: Financial reporting and regulatory compliance

**Key Features**:
- `default_flag`: Set to `True` for loans >= 180 days past due
- Detailed bucket descriptions for reporting
- Configurable threshold for different accounting standards

**Bucket Structure**:
- **Current** (0-29 days): No delinquency
- **DPD_30** (30-59 days): Early delinquency
- **DPD_60** (60-89 days): Early delinquency
- **DPD_90** (90-119 days): **High Risk** (but not accounting default)
- **DPD_120** (120-179 days): **High Risk** (but not accounting default)
- **DPD_180** (180+ days): **Technical Default** (accounting/regulatory)

**Usage**:
```python
from src.payment_processor import PaymentProcessor
import pandas as pd

# Initialize with default 180-day threshold
processor = PaymentProcessor()

# Or customize the threshold
processor = PaymentProcessor(dpd_threshold=150)

# Apply to your loan data
df = pd.DataFrame({
    'loan_id': [1, 2, 3],
    'days_past_due': [50, 100, 200]
})

result = processor.assign_dpd_buckets(df)
# Returns: dpd_bucket, dpd_bucket_description, default_flag
```

### FeatureEngineer (Risk Analysis: 90+ Days)

The `FeatureEngineer` class uses a **risk_threshold of 90 days** (configurable) to mark `is_default`. This is a more aggressive definition used for risk segmentation and early intervention.

**Purpose**: Risk analysis and portfolio management

**Key Features**:
- `is_default`: Set to `True` for loans >= 90 days past due (High Risk)
- Risk categories for portfolio segmentation
- Early identification of problematic loans

**Risk Categories**:
- **Current** (0-29 days): No risk
- **Early Delinquency** (30-89 days): Monitoring required
- **High Risk** (90-179 days): `is_default = True` - Intervention needed
- **Default** (180+ days): `is_default = True` - Technical default

**Usage**:
```python
from src.feature_engineer import FeatureEngineer
import pandas as pd

# Initialize with default 90-day risk threshold
engineer = FeatureEngineer()

# Or customize the threshold
engineer = FeatureEngineer(risk_threshold=120)

# Apply to your loan data
df = pd.DataFrame({
    'loan_id': [1, 2, 3],
    'days_past_due': [50, 100, 200]
})

result = engineer.assign_dpd_buckets(df)
# Returns: dpd_bucket, dpd_risk_category, is_default
```

## Key Differences and Consistency

### Threshold Distinction

| Days Past Due | PaymentProcessor (`default_flag`) | FeatureEngineer (`is_default`) | Rationale |
|--------------|-----------------------------------|--------------------------------|-----------|
| 0-89 days | False | False | Not yet high risk |
| 90-179 days | False | **True** | High Risk for early intervention |
| 180+ days | **True** | **True** | Accounting default reached |

### Why Two Thresholds?

1. **DEFAULT (180+ days)**: Used for accounting, financial reporting, and regulatory compliance. This is the point at which a loan is considered technically in default and may require write-offs or provisioning.

2. **HIGH RISK (90+ days)**: Used for risk management and portfolio analysis. This allows earlier identification of problematic loans for intervention strategies, collection efforts, and risk mitigation.

### Design Decisions

- **Consistent bucket labels**: Both methods use the same bucket naming (Current, DPD_30, DPD_60, DPD_90, DPD_120, DPD_180)
- **Different flag names**: `default_flag` vs `is_default` to clearly indicate their different purposes
- **Configurable thresholds**: Both classes accept threshold parameters for flexibility
- **Clear documentation**: Each method includes extensive docstrings explaining the threshold differences

## Installation and Testing

### Requirements
```bash
pip install pandas numpy
```

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test files
python -m unittest tests/test_payment_processor.py
python -m unittest tests/test_feature_engineer.py
python -m unittest tests/test_consistency.py
```

### Test Coverage

The test suite includes:
- Individual tests for each class
- Boundary value testing (29/30, 89/90, 179/180 days)
- Consistency tests between both methods
- Custom threshold validation
- Error handling tests

## Best Practices

### When to Use PaymentProcessor
- Financial reporting and accounting statements
- Regulatory compliance reporting
- Loan loss provisioning calculations
- Charge-off decisions
- External auditing requirements

### When to Use FeatureEngineer
- Portfolio risk analysis and segmentation
- Early warning systems for collections
- Risk-adjusted pricing models
- Strategic intervention planning
- Internal risk monitoring dashboards

### Using Both Together
```python
from src import PaymentProcessor, FeatureEngineer
import pandas as pd

# Your loan portfolio
loans_df = pd.DataFrame({
    'loan_id': range(1, 1001),
    'days_past_due': [...],  # Your DPD data
    'amount': [...]
})

# Apply both classifications
processor = PaymentProcessor()
engineer = FeatureEngineer()

# Get accounting view
accounting_view = processor.assign_dpd_buckets(loans_df.copy())
accounting_defaults = accounting_view[accounting_view['default_flag'] == True]

# Get risk view
risk_view = engineer.assign_dpd_buckets(loans_df.copy())
high_risk_loans = risk_view[risk_view['is_default'] == True]

print(f"Accounting defaults (180+ days): {len(accounting_defaults)}")
print(f"High risk loans (90+ days): {len(high_risk_loans)}")
print(f"Early intervention opportunities: {len(high_risk_loans) - len(accounting_defaults)}")
```

## Contributing

When contributing to this repository:
1. Maintain the threshold distinction (90 vs 180)
2. Keep bucket labels consistent between both methods
3. Update tests for any changes
4. Document any new thresholds or categories
5. Ensure backward compatibility

## License

This project is part of the Commercial-View analytics platform.
