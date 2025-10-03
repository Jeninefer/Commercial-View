# Fix Summary: Missing Return Statement in optimize() Method

## Problem

The `optimize()` method in the `PortfolioOptimizer` class was creating a DataFrame called `selected` with the optimized portfolio results, but it **was not returning it**. This meant callers of the method received `None` instead of the expected DataFrame.

### Original Code (Problem)

```python
def optimize(self, candidates_df: pd.DataFrame, aum_total: float, target_term: Optional[int] = None) -> pd.DataFrame:
    # ... selection logic ...
    
    selected = df.loc[pick_mask].copy()
    selected["selected"] = True
    selected["selected_amount_cum"] = selected["amount"].cumsum()
    # Missing: return selected
```

## Solution

Add a `return selected` statement at the end of the method to return the DataFrame containing the selected loans.

### Fixed Code

```python
def optimize(self, candidates_df: pd.DataFrame, aum_total: float, target_term: Optional[int] = None) -> pd.DataFrame:
    # ... selection logic ...
    
    selected = df.loc[pick_mask].copy()
    selected["selected"] = True
    selected["selected_amount_cum"] = selected["amount"].cumsum()
    return selected  # ← THE FIX
```

## Impact

- **Before**: Method returned `None`, making it impossible to access the selected loans
- **After**: Method returns a DataFrame with:
  - All columns from the input candidates
  - Additional scoring columns (apr_bucket, line_bucket, payer_bucket, score)
  - `selected` column (boolean, always True for returned rows)
  - `selected_amount_cum` column (cumulative sum of loan amounts)

## Verification

The fix has been verified through:

1. **Unit Tests**: 10 comprehensive test cases in `tests/test_optimizer.py`
   - All tests pass ✓
   - Verify return type is DataFrame
   - Verify required columns are present
   - Verify cumulative amounts are calculated correctly

2. **Integration Test**: `demonstrate_fix.py` shows the method working end-to-end
   - Returns proper DataFrame
   - Contains expected columns
   - Values are computed correctly

3. **Example Usage**: `example.py` demonstrates real-world usage

## Files Changed

- `src/commercial_view/optimizer.py`: Added `return selected` statement (line 134)
- No other logic changes were necessary

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run demonstration
python demonstrate_fix.py
```

All tests pass successfully! ✓
