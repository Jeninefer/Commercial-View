#!/usr/bin/env python3
"""
Example demonstration of key features:
1. Dynamic percentage calculation
2. Tolerance checks
3. Target comparisons

This script demonstrates the core functionality without requiring actual data files.
No external dependencies required - uses only Python standard library.
"""

# --- Feature 1: Dynamic Percentage Calculation ---
def calculate_percentage_vs_target(current: float, target: float) -> float:
    """Calculate percentage achievement vs target (e.g., 7.61M / 7.80M = 97.5%)."""
    if target is None or target == 0:
        return None
    return (current / target) * 100

# --- Feature 2: Tolerance Checks ---
def within_tolerance(value: float, target: float, tol: float = 0.01) -> bool:
    """Check if value is within tolerance of target."""
    if value is None or target is None or target == 0:
        return False
    return abs(value - target) <= tol * target

# --- Demonstration ---
print("=" * 70)
print("COMMERCIAL VIEW - FEATURE DEMONSTRATION")
print("=" * 70)
print()

# Example 1: Outstanding Portfolio vs Target
print("Example 1: Outstanding Portfolio Comparison")
print("-" * 70)
current_outstanding = 7_610_000  # $7.61M
target_outstanding = 7_800_000   # $7.80M

pct = calculate_percentage_vs_target(current_outstanding, target_outstanding)
within_tol = within_tolerance(current_outstanding, target_outstanding)

print(f"Current EOM:     ${current_outstanding:,.2f}")
print(f"Target EOM:      ${target_outstanding:,.2f}")
print(f"Achievement:     {pct:.1f}%")
print(f"Within 1% Tol:   {within_tol}")
print(f"Difference:      ${abs(current_outstanding - target_outstanding):,.2f}")
print(f"Tolerance Band:  ${target_outstanding * 0.01:,.2f}")
print(f"Status:          {'✓ PASS' if within_tol else '⚠ WARNING'}")
print()

# Example 2: APR Tolerance
print("Example 2: Weighted APR Comparison")
print("-" * 70)
current_apr = 18.2  # %
target_apr = 18.5   # %

apr_pct = calculate_percentage_vs_target(current_apr, target_apr)
apr_within_tol = within_tolerance(current_apr, target_apr)

print(f"Current APR:     {current_apr:.2f}%")
print(f"Target APR:      {target_apr:.2f}%")
print(f"Achievement:     {apr_pct:.1f}%")
print(f"Within 1% Tol:   {apr_within_tol}")
print(f"Difference:      {abs(current_apr - target_apr):.2f}%")
print(f"Tolerance Band:  {target_apr * 0.01:.2f}%")
print(f"Status:          {'✓ PASS' if apr_within_tol else '⚠ WARNING'}")
print()

# Example 3: NPL within tolerance
print("Example 3: NPL Comparison (Within Tolerance)")
print("-" * 70)
current_npl = 2.45  # %
target_npl = 2.50   # %

npl_pct = calculate_percentage_vs_target(current_npl, target_npl)
npl_within_tol = within_tolerance(current_npl, target_npl)

print(f"Current NPL:     {current_npl:.2f}%")
print(f"Target NPL:      {target_npl:.2f}%")
print(f"Achievement:     {npl_pct:.1f}%")
print(f"Within 1% Tol:   {npl_within_tol}")
print(f"Difference:      {abs(current_npl - target_npl):.2f}%")
print(f"Tolerance Band:  {target_npl * 0.01:.2f}%")
print(f"Status:          {'✓ PASS' if npl_within_tol else '⚠ WARNING'}")
print()

# Example 4: Tenor Mix Comparisons
print("Example 4: Tenor Mix vs Targets")
print("-" * 70)
tenor_current = {
    "≤30": 26.5,
    "31–60": 37.0,
    "61–90": 24.0,
    ">90": 12.5
}

tenor_targets = {
    "≤30": 25.0,
    "31–60": 35.0,
    "61–90": 25.0,
    ">90": 15.0
}

print(f"{'Bucket':<10} {'Current':<10} {'Target':<10} {'Diff':<10} {'Status'}")
print("-" * 70)
for bucket in tenor_current.keys():
    curr = tenor_current[bucket]
    targ = tenor_targets[bucket]
    diff = curr - targ
    within = within_tolerance(curr, targ)
    status = "✓ PASS" if within else "⚠ WARN"
    print(f"{bucket:<10} {curr:>7.1f}%  {targ:>7.1f}%  {diff:>+7.1f}%  {status}")

print()

# Example 5: Q4 Target Loading Simulation
print("Example 5: Q4 Targets Structure")
print("-" * 70)
print("Sample Q4_Targets.csv content:")
print()
print("Month,Outstanding_Target,Disbursement_Target,APR_Target,NPL_Target,Tenor_30_Target,...")
print("2025-10-01,7800000,450000,18.5,2.5,25,...")
print("2025-11-01,8200000,450000,18.5,2.5,25,...")
print("2025-12-01,8500000,370000,18.5,2.5,25,...")
print()
print("Benefits:")
print("  ✓ Single source of truth for all targets")
print("  ✓ Easy monthly updates without code changes")
print("  ✓ Version controlled for audit trail")
print("  ✓ Prevents drift between ETL and visualization")
print()

# Example 6: Different Tolerance Levels
print("Example 6: Tolerance Sensitivity Analysis")
print("-" * 70)
value = 7_650_000
target = 7_800_000
tolerances = [0.005, 0.01, 0.02, 0.05]  # 0.5%, 1%, 2%, 5%

print(f"Value: ${value:,.0f}  Target: ${target:,.0f}  Diff: ${abs(value-target):,.0f}")
print()
print(f"{'Tolerance':<12} {'Band ($)':<15} {'Within?'}")
print("-" * 70)
for tol in tolerances:
    band = target * tol
    within = within_tolerance(value, target, tol)
    print(f"{tol*100:>6.1f}%      ${band:>12,.0f}  {within}")

print()
print("=" * 70)
print("Feature demonstration complete!")
print("=" * 70)
