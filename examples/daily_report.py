"""
Example: Daily Portfolio Report with Optimizer and Alerts

This script demonstrates a typical daily workflow:
1. Load current portfolio and pending requests
2. Run optimizer to select disbursements
3. Generate alerts for portfolio health
4. Post alerts to Slack
"""

import pandas as pd
from abaco_core.optimizer import DisbursementOptimizer
from abaco_core.alerts import AlertEngine
from abaco_core.manifest import bucket_apr, bucket_line, bucket_payer, share

# Example current portfolio
current_portfolio = pd.DataFrame({
    "amount": [500_000, 750_000, 300_000, 1_200_000, 400_000],
    "apr": [18.5, 22.0, 25.5, 20.0, 28.0],
    "industry": ["Manufacturing", "Retail", "Services", "Construction", "Wholesale"],
    "payer_grade": ["A", "B", "A", "B", "C"],
    "customer_id": ["C001", "C002", "C003", "C004", "C005"],
})

# Example pending disbursement requests
pending_requests = pd.DataFrame({
    "amount": [250_000, 400_000, 600_000, 150_000, 800_000],
    "apr": [19.0, 24.0, 26.5, 17.5, 22.5],
    "industry": ["Healthcare", "Manufacturing", "Services", "Retail", "Technology"],
    "payer_grade": ["A", "B", "A", "A", "C"],
    "customer_id": ["C006", "C007", "C008", "C009", "C010"],
})

print("=" * 80)
print("ABACO DAILY PORTFOLIO REPORT")
print("=" * 80)
print()

# 1. Portfolio Summary
print("CURRENT PORTFOLIO SUMMARY")
print("-" * 80)
total_aum = current_portfolio["amount"].sum()
print(f"Total AUM: ${total_aum:,.0f}")
print(f"Number of clients: {len(current_portfolio)}")
print()

# APR mix
apr_mix = share(current_portfolio.groupby(
    current_portfolio["apr"].apply(bucket_apr)
)["amount"].sum())
print("APR Mix:")
for bucket, pct in sorted(apr_mix.items()):
    print(f"  {bucket}: {pct:.1f}%")
print()

# Industry mix
industry_mix = share(current_portfolio.groupby("industry")["amount"].sum())
print("Industry Mix:")
for industry, pct in sorted(industry_mix.items(), key=lambda x: x[1], reverse=True):
    print(f"  {industry}: {pct:.1f}%")
print()

# Payer mix
payer_mix = share(current_portfolio.groupby("payer_grade")["amount"].sum())
print("Payer Mix:")
for grade, pct in sorted(payer_mix.items()):
    print(f"  Grade {grade}: {pct:.1f}%")
print()

# 2. Run Optimizer
print("=" * 80)
print("DISBURSEMENT OPTIMIZATION")
print("-" * 80)

# Define target portfolio mix
target_apr_mix = {
    "15-20%": 30.0,
    "20-25%": 40.0,
    "25-30%": 30.0,
}

optimizer = DisbursementOptimizer(
    target_apr_mix=target_apr_mix,
    payer_a_min=0.35,  # Want at least 35% A-grade
    payer_d_max=0.10,  # Max 10% D-grade
    industry_max_share=0.25,  # Max 25% per industry
    top_client_max=0.15,  # Max 15% for top client
)

# Target AUM: current + 2M growth
aum_target = total_aum + 2_000_000

selected, report = optimizer.optimize(
    requests=pending_requests,
    current_portfolio=current_portfolio,
    aum_target=aum_target,
)

print(f"Budget available: ${report['budget']:,.0f}")
print(f"Requests evaluated: {len(pending_requests)}")
print(f"Requests selected: {report['selected_count']}")
print(f"Amount selected: ${report['selected_amount']:,.0f}")
print(f"Budget utilization: {report['utilization']:.1f}%")
print()

if len(selected) > 0:
    print("Selected Requests:")
    print("-" * 80)
    for idx, row in selected.iterrows():
        print(f"  Customer {row['customer_id']}: ${row['amount']:,.0f} @ {row['apr']:.1f}% APR")
        print(f"    Industry: {row['industry']}, Payer Grade: {row['payer_grade']}")
    print()
    
    print("Projected Portfolio Mix After Disbursements:")
    print("-" * 80)
    print("APR Mix:")
    for bucket, pct in sorted(report['apr_mix'].items()):
        target = target_apr_mix.get(bucket, 0)
        delta = pct - target
        print(f"  {bucket}: {pct:.1f}% (Target: {target:.1f}%, Delta: {delta:+.1f}%)")
    print()

# 3. Generate Alerts
print("=" * 80)
print("PORTFOLIO HEALTH ALERTS")
print("-" * 80)

engine = AlertEngine()
alerts = []

# Concentration alerts
exposures = current_portfolio.groupby("customer_id")["amount"].sum()
alerts += engine.concentration_alerts(exposures, top_1_threshold=0.15, top_5_threshold=0.40)

# Risk alerts (example values)
alerts += engine.risk_alerts(
    npl180_mom_bps=45,  # NPL 180+ increased 45 bps
    dpd_7d_growth=1.2,  # DPD growing moderately
)

# Yield alerts
current_apr_mix = pd.Series(apr_mix)
alerts += engine.yield_alerts(
    apr_mix=current_apr_mix,
    target_apr_mix=target_apr_mix,
    deviation_threshold=5.0,
)

# Liquidity alerts (example values)
alerts += engine.liquidity_alerts(
    collections_vs_plan=0.92,  # 92% of plan
    bank_shortfall=False,
)

# Growth alerts (example values)
alerts += engine.growth_alerts(
    ltv_over_3_cac=True,
    payback_months=15.5,
)

# Display alerts
if alerts:
    for alert in sorted(alerts, key=lambda a: {"critical": 0, "warning": 1, "info": 2}[a.severity]):
        emoji = {"critical": "🚨", "warning": "⚠️", "info": "ℹ️"}[alert.severity]
        print(f"{emoji} [{alert.severity.upper()}] {alert.title}")
        print(f"  {alert.message}")
        if alert.value is not None and alert.threshold is not None:
            print(f"  Value: {alert.value:.2f} | Threshold: {alert.threshold:.2f}")
        print()
    
    # Post to Slack (requires SLACK_WEBHOOK_URL env var)
    print("-" * 80)
    print("To post alerts to Slack, set SLACK_WEBHOOK_URL environment variable")
    print("Example: export SLACK_WEBHOOK_URL='https://hooks.slack.com/services/...'")
    # engine.post_to_slack(alerts)
else:
    print("✅ No alerts detected - portfolio health is good!")
    print()

print("=" * 80)
print("Report completed successfully")
print("=" * 80)
