# Refactoring: Avoiding Redundant Standardization

## Problem

Previously, the `calculate_payment_timeline` and `calculate_dpd` methods were both calling `standardize_dataframes`, causing double processing of the same data. This was inefficient, especially for large datasets, as it involved:

1. Duplicate column name detection
2. Duplicate column renaming operations
3. Duplicate date type conversions

## Solution

The refactoring implements a two-part strategy:

### 1. Smart Detection in `calculate_payment_timeline`

The method now checks if data is already standardized before calling `standardize_dataframes`:

```python
# Check if data is already standardized by looking for required columns
raw = not {"loan_id", "due_date", "due_amount"}.issubset(schedule_df.columns)

if raw:
    # Data needs standardization
    sched, pays = self.standardize_dataframes(schedule_df, payments_df)
else:
    # Data is already standardized, just make copies
    sched, pays = schedule_df.copy(), payments_df.copy()
```

This allows `calculate_payment_timeline` to work with both:
- Raw data (will standardize automatically)
- Already-standardized data (skips redundant standardization)

### 2. Single Standardization in `calculate_dpd`

The method now standardizes data once and passes the standardized DataFrames to `calculate_payment_timeline`:

```python
def calculate_dpd(self, schedule_df, payments_df, reference_date=None):
    # Standardize dataframes once at the start
    sched, pays = self.standardize_dataframes(schedule_df, payments_df)
    
    # Use standardized data for timeline calculation
    # Pass already-standardized data to avoid re-standardization
    timeline = self.calculate_payment_timeline(sched, pays, reference_date)
    
    # ... proceed with DPD calculations ...
```

## Benefits

1. **Performance**: Eliminates duplicate processing, improving performance especially for large datasets
2. **Clarity**: Makes the data flow more explicit and easier to understand
3. **Flexibility**: `calculate_payment_timeline` can now work with both raw and standardized data
4. **Maintainability**: Reduces code complexity and potential for bugs

## Testing

The refactoring includes a specific test (`test_no_redundant_standardization`) that verifies `standardize_dataframes` is called exactly once when `calculate_dpd` is invoked, confirming the optimization is working correctly.

## Usage

No changes are required for existing code using these methods:

```python
analyzer = PaymentAnalyzer()

# Works exactly as before, but more efficiently
dpd_df = analyzer.calculate_dpd(raw_schedule_df, raw_payments_df)
```
