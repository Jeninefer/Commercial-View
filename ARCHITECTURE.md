# DPD Classification Architecture

## Overview

This document provides a technical overview of the DPD (Days Past Due) Bucket Classification System, explaining the architectural decisions and the rationale behind having two separate classification methods.

## System Components

### 1. PaymentProcessor (src/payment_processor.py)

**Purpose**: Accounting and regulatory compliance

**Threshold**: 180 days (configurable)

**Flag**: `default_flag`

**Use Cases**:
- Financial statements and regulatory reporting
- Loan loss provisioning calculations
- Charge-off determinations
- External auditing and compliance
- GAAP/IFRS reporting requirements

### 2. FeatureEngineer (src/feature_engineer.py)

**Purpose**: Risk analysis and portfolio management

**Threshold**: 90 days (configurable)

**Flag**: `is_default`

**Use Cases**:
- Early warning systems
- Risk-based pricing models
- Collection strategy optimization
- Portfolio segmentation
- Proactive risk management

## DPD Timeline

```
Days Past Due:    0      30      60      90      120     150     180     210+
                  |------|-------|-------|-------|-------|-------|-------|
                  
Buckets:         Current  DPD_30  DPD_60  DPD_90  DPD_120         DPD_180
                  
PaymentProcessor: ✓       ✓       ✓       ✓       ✓       ✓       ⚠️ DEFAULT
default_flag:     False   False   False   False   False   False   True    True

FeatureEngineer:  ✓       ✓       ✓      ⚠️ HIGH RISK ⚠️           ⚠️ DEFAULT
is_default:       False   False   False   True    True    True    True    True

Risk Category:    Current Early Delinq.  High Risk              Default
```

## Critical Thresholds

### 90 Days - High Risk Threshold (FeatureEngineer)

**Rationale**:
- Industry standard for identifying high-risk loans
- Allows time for intervention before accounting default
- Aligns with credit risk management best practices
- Provides early warning for portfolio managers

**Actions**:
- Escalate to collections
- Implement workout strategies
- Review collateral positions
- Adjust risk ratings

### 180 Days - Accounting Default Threshold (PaymentProcessor)

**Rationale**:
- Common regulatory and accounting standard
- Aligns with charge-off policies
- Meets external reporting requirements
- Represents point of likely loss recognition

**Actions**:
- Establish loan loss provisions
- Initiate charge-off procedures
- Update regulatory reports
- Assess legal remedies

## The 90-179 Day Window: Early Intervention Zone

This critical window represents loans that are:
- **High Risk** (is_default = True in FeatureEngineer)
- **Not yet accounting defaults** (default_flag = False in PaymentProcessor)

**Business Value**:
- Identifies $730,000 in the example portfolio
- Represents 3 loans requiring urgent attention
- Opportunity for recovery before charge-off
- Cost-effective intervention point

**Strategic Actions**:
1. Priority collection efforts
2. Loan restructuring negotiations
3. Collateral liquidation planning
4. Guarantee enforcement
5. Legal action consideration

## Consistency Guarantees

### Bucket Label Consistency
Both methods use identical bucket labels:
- Current
- DPD_30
- DPD_60
- DPD_90
- DPD_120
- DPD_180

### Flag Consistency
- All loans >= 180 days have both flags set to True
- All loans < 90 days have both flags set to False
- Only the 90-179 day range differs by design

### Configurable Thresholds
Both classes support custom thresholds:
```python
# Custom accounting threshold
processor = PaymentProcessor(dpd_threshold=150)

# Custom risk threshold
engineer = FeatureEngineer(risk_threshold=120)
```

## Implementation Patterns

### Pattern 1: Dual Classification
```python
from src import PaymentProcessor, FeatureEngineer

processor = PaymentProcessor()
engineer = FeatureEngineer()

# Apply both classifications
accounting_view = processor.assign_dpd_buckets(loans_df.copy())
risk_view = engineer.assign_dpd_buckets(loans_df.copy())

# Identify intervention opportunities
intervention_zone = risk_view[
    (risk_view['is_default'] == True) & 
    (accounting_view['default_flag'] == False)
]
```

### Pattern 2: Unified Reporting
```python
# Merge both perspectives
unified = pd.merge(
    accounting_view[['loan_id', 'default_flag', 'dpd_bucket_description']],
    risk_view[['loan_id', 'is_default', 'dpd_risk_category']],
    on='loan_id'
)

# Generate management report
report = unified.groupby(['dpd_risk_category']).agg({
    'loan_id': 'count',
    'default_flag': 'sum',
    'is_default': 'sum'
})
```

### Pattern 3: Custom Thresholds
```python
# Align to specific regulatory requirements
# Example: Some jurisdictions use 150 days
processor = PaymentProcessor(dpd_threshold=150)
engineer = FeatureEngineer(risk_threshold=75)

# Apply customized classification
result = processor.assign_dpd_buckets(loans_df)
```

## Testing Strategy

### Test Coverage
- Unit tests for each class (9 tests each)
- Integration tests for consistency (9 tests)
- Total: 28 tests, all passing

### Key Test Scenarios
1. Boundary value testing (29/30, 89/90, 179/180 days)
2. Flag accuracy at thresholds
3. Bucket label consistency
4. Custom threshold support
5. Error handling for invalid data

## Performance Considerations

### Computational Complexity
- O(n) time complexity for both methods
- Single pass through data
- Vectorized pandas operations
- Suitable for large portfolios

### Memory Usage
- Creates copy of input DataFrame
- Adds 3 columns per method
- Minimal memory overhead
- No intermediate data structures

## Migration Guide

### From Manual DPD Classification
```python
# Before: Manual conditions
df['is_default'] = df['days_past_due'] >= 90

# After: Structured classification
from src import FeatureEngineer
engineer = FeatureEngineer()
df = engineer.assign_dpd_buckets(df)
# Now includes: dpd_bucket, dpd_risk_category, is_default
```

### From Single Threshold System
```python
# Before: Single 180-day threshold
df['default'] = df['days_past_due'] >= 180

# After: Dual threshold system
from src import PaymentProcessor, FeatureEngineer

processor = PaymentProcessor()
engineer = FeatureEngineer()

accounting = processor.assign_dpd_buckets(df.copy())  # 180-day threshold
risk = engineer.assign_dpd_buckets(df.copy())         # 90-day threshold
```

## Glossary

**DPD**: Days Past Due - the number of days a payment is overdue

**default_flag**: Boolean indicator used by PaymentProcessor for accounting default (>= 180 days)

**is_default**: Boolean indicator used by FeatureEngineer for high risk classification (>= 90 days)

**High Risk**: Loans in the 90-179 day range, flagged for intervention but not yet accounting defaults

**Technical Default**: Loans >= 180 days, meeting accounting and regulatory default criteria

**Bucket**: A categorical grouping of loans based on DPD ranges

**Threshold**: The DPD value at which a flag transitions from False to True

## References

- Basel III Framework on credit risk
- IFRS 9 - Financial Instruments
- US GAAP ASC 310 - Receivables
- Industry best practices for credit risk management

## Version History

- v1.0.0 (2025-10-03): Initial implementation with dual threshold system
  - PaymentProcessor with 180-day default threshold
  - FeatureEngineer with 90-day risk threshold
  - Comprehensive test coverage
  - Full documentation
