# Feature Implementation Reference

## 1. Dynamic Percentage Calculation (EOM vs Target)

**Location:** `build_dashboard_payload.py` lines 53-59

```python
def calculate_percentage_vs_target(current: float, target: float) -> float:
    """Calculate percentage achievement vs target (e.g., 7.61M / 7.80M = 97.5%)."""
    if pd.isna(target) or target == 0:
        return None
    return (current / target) * 100
```

**Usage Example:**
If Oct current EOM = $7.61M and target = $7.80M:
- Calculation: (7,610,000 / 7,800,000) * 100 = 97.5%
- Result appears in `target_comparisons.outstanding.percentage`

**Output in JSON:**
```json
{
  "target_comparisons": {
    "outstanding": {
      "current": 7610000.00,
      "target": 7800000.00,
      "percentage": 97.5,
      "within_tolerance": false
    }
  }
}
```

## 2. Tolerance Checks (APR, Tenor Mix, NPL)

**Location:** `build_dashboard_payload.py` lines 49-54

```python
def within_tolerance(value: float, target: float, tol: float = 0.01) -> bool:
    """Check if value is within tolerance of target."""
    if pd.isna(value) or pd.isna(target) or target == 0:
        return False
    return abs(value - target) <= tol * target
```

**Default Tolerance:** 1% (tol = 0.01)

**Applied to:**

### APR Tolerance (lines 213-220)
```python
target_comparisons["apr"] = {
    "current": round(apr_pct, 2),
    "target": round(apr_target, 2),
    "percentage": round(calculate_percentage_vs_target(apr_pct, apr_target), 2),
    "within_tolerance": within_tolerance(apr_pct, apr_target, tol=0.01)
}
```

### NPL Tolerance (lines 223-230)
```python
target_comparisons["npl"] = {
    "current": round(npl_pct, 2),
    "target": round(npl_target, 2),
    "percentage": round(calculate_percentage_vs_target(npl_pct, npl_target), 2),
    "within_tolerance": within_tolerance(npl_pct, npl_target, tol=0.01)
}
```

### Tenor Mix Tolerance (lines 282-293)
```python
for bucket, target_col in tenor_mapping.items():
    if target_col in target_row and bucket in tenor_mix:
        current_val = tenor_mix[bucket]
        target_val = target_row[target_col]
        tenor_target_comparisons[bucket] = {
            "current": round(current_val, 2),
            "target": round(target_val, 2),
            "within_tolerance": within_tolerance(current_val, target_val, tol=0.01)
        }
```

**Tolerance Logic:**
- Returns `True` if: |current - target| ≤ (tolerance × target)
- Example: If target = 18.5% APR and tolerance = 1%
  - Acceptable range: 18.315% to 18.685%
  - Value of 18.4% → within_tolerance = True
  - Value of 19.0% → within_tolerance = False

## 3. Q4 Targets from CSV

**Location:** `Q4_Targets.csv`

**Format:**
```csv
Month,Outstanding_Target,Disbursement_Target,APR_Target,NPL_Target,Tenor_30_Target,Tenor_60_Target,Tenor_90_Target,Tenor_90plus_Target
2025-10-01,7800000,450000,18.5,2.5,25,35,25,15
2025-11-01,8200000,450000,18.5,2.5,25,35,25,15
2025-12-01,8500000,370000,18.5,2.5,25,35,25,15
```

**Loading Function:** `build_dashboard_payload.py` lines 61-69

```python
def load_q4_targets():
    """Load quarterly targets from CSV file."""
    if not os.path.exists(Q4_TARGETS_FILE):
        print(f"Warning: {Q4_TARGETS_FILE} not found, using empty targets")
        return pd.DataFrame()
    
    targets = pd.read_csv(Q4_TARGETS_FILE)
    targets["Month"] = pd.to_datetime(targets["Month"])
    return targets
```

**Benefits:**
- Single source of truth for all target values
- Easy monthly updates without code changes
- Prevents drift between Python ETL and React/Figma
- Can be version controlled for audit trail

**Usage in Code:**
```python
# Line 164
q4_targets = load_q4_targets()

# Lines 187-191
current_month = asof.replace(day=1)
current_targets = q4_targets[q4_targets["Month"] == current_month]

if not current_targets.empty:
    target_row = current_targets.iloc[0]
    # Use target_row["Outstanding_Target"], etc.
```

## 4. Figma Widget Visual Indicators

**Location:** `code.tsx`

### Target Status Colors (lines 104-112)
```typescript
const outstandingStatus = tc?.outstanding?.within_tolerance ? "good" : 
                          tc?.outstanding ? "warning" : undefined;

const aprStatus = tc?.apr?.within_tolerance ? "good" : 
                 tc?.apr ? "warning" : undefined;

const nplStatus = tc?.npl?.within_tolerance ? "good" : 
                 tc?.npl ? "warning" : undefined;
```

### Tile Component with Status (lines 69-95)
```typescript
function Tile({ 
  title, 
  value, 
  subtitle,
  target,
  status
}: { 
  title: string; 
  value: string; 
  subtitle?: string;
  target?: string;
  status?: "good" | "warning" | "bad";
}) {
  const statusColors = {
    good: "#10B981",    // Green border
    warning: "#F59E0B", // Yellow border
    bad: "#EF4444"      // Red border
  };
  
  return (
    <AutoLayout 
      stroke={status ? statusColors[status] : "#CED4D9"}
      strokeWidth={status ? 2 : 1}
      // ... rest of component
    />
  );
}
```

### Tenor Mix with Tolerance Indicators (lines 178-204)
```typescript
const tmRows = Object.entries(tm).map(([k, v], i) => {
  const target = ttc[k];
  const status = target?.within_tolerance ? "✓" : target ? "⚠" : "";
  
  return (
    <AutoLayout 
      stroke={target?.within_tolerance ? "#10B981" : target ? "#F59E0B" : "#ECEFF2"}
      // Shows ✓ or ⚠ based on tolerance
    />
  );
});
```

### Target Status Summary Panel (lines 238-266)
Shows a highlighted summary of all target comparisons with color-coded status.

## Data Flow

1. **Input:** Loan tape Excel/CSV files + Google Sheets + Q4_Targets.csv
2. **Processing:** `build_dashboard_payload.py`
   - Loads data from all sources
   - Calculates KPIs
   - Compares against targets from CSV
   - Applies tolerance checks
   - Outputs `dashboard_payload.json`
3. **Visualization:** `code.tsx` in Figma
   - Parses JSON
   - Renders tiles with color-coded borders
   - Shows percentage achievements
   - Displays tolerance status indicators

## Example Tolerance Scenarios

### Scenario 1: Outstanding within tolerance
- Current: $7,750,000
- Target: $7,800,000
- Percentage: 99.4%
- Tolerance check: |7,750,000 - 7,800,000| = 50,000 ≤ 78,000 (1% of target)
- Result: `within_tolerance = True` → Green border in Figma

### Scenario 2: APR outside tolerance
- Current: 17.5%
- Target: 18.5%
- Percentage: 94.6%
- Tolerance check: |17.5 - 18.5| = 1.0 > 0.185 (1% of target)
- Result: `within_tolerance = False` → Yellow border in Figma

### Scenario 3: Tenor Mix 31-60 days
- Current: 37%
- Target: 35%
- Percentage: 105.7%
- Tolerance check: |37 - 35| = 2 > 0.35 (1% of target)
- Result: `within_tolerance = False` → Yellow border, ⚠ indicator

## Customization

### Adjust Tolerance
Change the `tol` parameter in function calls:
```python
# More strict (0.5% tolerance)
within_tolerance(current_val, target_val, tol=0.005)

# More lenient (2% tolerance)
within_tolerance(current_val, target_val, tol=0.02)
```

### Add New Target Columns
1. Add column to `Q4_Targets.csv`
2. Add comparison logic in `build_dashboard_payload.py`
3. Update `Payload` type in `code.tsx`
4. Add visual indicator in Figma widget

### Change Status Colors
Edit `statusColors` object in `code.tsx` (line 77-81)
