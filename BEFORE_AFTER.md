# Before and After Comparison

## The Issue

The `optimize()` method in `PortfolioOptimizer` created a `selected` DataFrame but didn't return it.

## Code Comparison

### BEFORE (Broken) ❌
```python
def optimize(self, candidates_df: pd.DataFrame, aum_total: float, target_term: Optional[int] = None) -> pd.DataFrame:
    df = candidates_df.copy()
    if df.empty:
        return df

    # ... 70+ lines of optimization logic ...

    selected = df.loc[pick_mask].copy()
    selected["selected"] = True
    selected["selected_amount_cum"] = selected["amount"].cumsum()
    # ❌ NO RETURN STATEMENT - Method returns None!
```

### AFTER (Fixed) ✅
```python
def optimize(self, candidates_df: pd.DataFrame, aum_total: float, target_term: Optional[int] = None) -> pd.DataFrame:
    df = candidates_df.copy()
    if df.empty:
        return df

    # ... 70+ lines of optimization logic ...

    selected = df.loc[pick_mask].copy()
    selected["selected"] = True
    selected["selected_amount_cum"] = selected["amount"].cumsum()
    return selected  # ✅ NOW RETURNS THE SELECTED DATAFRAME!
```

## The Fix

**Single line change**: Added `return selected` at the end of the method (line 134)

## Impact

| Aspect | Before | After |
|--------|--------|-------|
| Return value | `None` | `pd.DataFrame` |
| Usability | ❌ Broken | ✅ Working |
| Type annotation | ❌ Incorrect (says returns DataFrame) | ✅ Correct |
| User experience | ❌ Confusing error | ✅ Expected behavior |

## Example Usage

```python
# Create optimizer
optimizer = PortfolioOptimizer(rules=rules, weights=weights)

# Run optimization
result = optimizer.optimize(candidates, aum_total=1000000)

# BEFORE: result is None ❌
# AFTER: result is a DataFrame with selected loans ✅
print(result)
#   customer_id  amount  apr  selected  selected_amount_cum
# 0           A  100000  6.5      True               100000
# 1           B  200000  7.2      True               300000
```

## Testing

All tests pass with the fix:
```
$ pytest tests/ -v
===================== test session starts ======================
...
tests/test_optimizer.py::test_optimize_returns_dataframe PASSED
tests/test_optimizer.py::test_optimize_adds_required_columns PASSED
tests/test_optimizer.py::test_optimize_cumsum_is_correct PASSED
...
==================== 10 passed in 0.31s ====================
```

✅ **FIX VERIFIED AND COMPLETE**
