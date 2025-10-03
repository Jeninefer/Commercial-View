# Quick Reference: PaymentProcessor vs FeatureEngineer

## At a Glance

| Feature | PaymentProcessor | FeatureEngineer |
|---------|-----------------|-----------------|
| **Primary Purpose** | Accounting/Regulatory | Risk Management |
| **Default Threshold** | 180 days | 90 days |
| **Flag Name** | `default_flag` | `is_default` |
| **Output Columns** | dpd_bucket<br>dpd_bucket_description<br>default_flag | dpd_bucket<br>dpd_risk_category<br>is_default |
| **Configurable?** | ✅ Yes (dpd_threshold) | ✅ Yes (risk_threshold) |

## When Each Flag is True

| Days Past Due | default_flag (PaymentProcessor) | is_default (FeatureEngineer) |
|--------------|--------------------------------|------------------------------|
| 0-89 | ❌ False | ❌ False |
| 90-179 | ❌ False | ✅ **True** |
| 180+ | ✅ **True** | ✅ **True** |

## Quick Example

```python
from src import PaymentProcessor, FeatureEngineer
import pandas as pd

# Sample data
df = pd.DataFrame({
    'loan_id': [1, 2, 3],
    'days_past_due': [50, 100, 200]
})

# Accounting view (180-day threshold)
processor = PaymentProcessor()
accounting = processor.assign_dpd_buckets(df.copy())

# Risk view (90-day threshold)
engineer = FeatureEngineer()
risk = engineer.assign_dpd_buckets(df.copy())

# Compare results
print(accounting[['loan_id', 'days_past_due', 'default_flag']])
print(risk[['loan_id', 'days_past_due', 'is_default']])
```

**Output**:
```
# Accounting View (180-day threshold)
   loan_id  days_past_due  default_flag
0        1             50         False  <- Not default
1        2            100         False  <- Not default (but high risk!)
2        3            200          True  <- Default

# Risk View (90-day threshold)
   loan_id  days_past_due  is_default
0        1             50       False  <- Not high risk
1        2            100        True  <- High risk!
2        3            200        True  <- High risk + default
```

## Decision Tree

```
Is the loan >= 90 days past due?
│
├─ NO (0-89 days)
│  ├─ default_flag = False
│  ├─ is_default = False
│  └─ Status: Current or Early Delinquency
│
└─ YES (90+ days)
   │
   ├─ Is the loan >= 180 days past due?
   │
   ├─ NO (90-179 days)
   │  ├─ default_flag = False (not accounting default)
   │  ├─ is_default = True (high risk!)
   │  └─ Status: HIGH RISK - Early Intervention Zone
   │
   └─ YES (180+ days)
      ├─ default_flag = True (accounting default)
      ├─ is_default = True (high risk)
      └─ Status: DEFAULT - Charge-off consideration
```

## Common Use Cases

### Use Case 1: Financial Reporting
```python
processor = PaymentProcessor()
result = processor.assign_dpd_buckets(loans_df)

# Count accounting defaults for financial statements
accounting_defaults = result[result['default_flag'] == True]
print(f"Loans in default: {len(accounting_defaults)}")
print(f"Total provision required: ${accounting_defaults['amount'].sum():,.2f}")
```

### Use Case 2: Risk Monitoring Dashboard
```python
engineer = FeatureEngineer()
result = engineer.assign_dpd_buckets(loans_df)

# Monitor high-risk loans for collection priority
high_risk = result[result['is_default'] == True]
risk_summary = high_risk.groupby('dpd_risk_category').agg({
    'loan_id': 'count',
    'amount': 'sum'
})
print(risk_summary)
```

### Use Case 3: Early Intervention Strategy
```python
processor = PaymentProcessor()
engineer = FeatureEngineer()

accounting = processor.assign_dpd_buckets(loans_df.copy())
risk = engineer.assign_dpd_buckets(loans_df.copy())

# Find loans in the intervention zone (90-179 days)
intervention = risk[
    (risk['is_default'] == True) & 
    (accounting['default_flag'] == False)
]

print(f"Loans for early intervention: {len(intervention)}")
print(f"Potential recovery amount: ${intervention['amount'].sum():,.2f}")
```

## Bucket Labels (Both Use Same Labels)

| Bucket | Days Past Due Range |
|--------|-------------------|
| Current | 0-29 |
| DPD_30 | 30-59 |
| DPD_60 | 60-89 |
| DPD_90 | 90-119 |
| DPD_120 | 120-179 |
| DPD_180 | 180+ |

## Important Notes

1. **Consistent Buckets**: Both methods use identical bucket labels for consistency
2. **Different Flags**: `default_flag` ≠ `is_default` (different thresholds, different purposes)
3. **Configurable**: Both thresholds can be customized via constructor parameters
4. **Complementary**: Use both methods together for comprehensive analysis
5. **No Conflict**: The different thresholds serve different business needs

## Testing

Run all tests:
```bash
python3 -m unittest discover tests -v
```

Expected: 28 tests, all passing ✅

## Need Help?

- See `README.md` for detailed documentation
- See `ARCHITECTURE.md` for technical details
- Run `python3 example_usage.py` for a demonstration
- Check `tests/` directory for usage examples
