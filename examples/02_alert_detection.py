"""
Example: Alert detection

Demonstrates how to use the AlertEngine for detecting portfolio anomalies.
"""

import pandas as pd
import numpy as np
from abaco_core import AlertEngine


def main():
    # Initialize alert engine
    engine = AlertEngine()
    print("Alert Engine initialized\n")
    
    # ===== Concentration Alerts =====
    print("=== Testing Concentration Alerts ===")
    
    # Simulated client exposures
    exposures = pd.Series({
        "client_A": 100000,  # 45% - exceeds 4% limit
        "client_B": 50000,   # 22.5%
        "client_C": 30000,   # 13.5%
        "client_D": 20000,   # 9%
        "client_E": 22000    # 10%
    })
    
    # Month-over-month growth in bps
    exposures_mom = pd.Series({
        "client_A": 30,  # Growing 30 bps
        "client_B": 5,
        "client_C": 15,
        "client_D": 2,
        "client_E": 1
    })
    
    alerts = engine.concentration_alerts(exposures, exposures_mom)
    print(f"Generated {len(alerts)} concentration alerts:")
    for alert in alerts:
        print(f"  [{alert['severity']}] {alert['title']}")
        print(f"    {alert['meta']}")
    
    # ===== Risk Alerts =====
    print("\n=== Testing Risk Alerts ===")
    
    # Simulated roll rates (last 6 months)
    rollrates_hist = pd.DataFrame({
        "from_bucket": ["30-60"] * 6 + ["60-90"] * 6,
        "to_bucket": ["60-90"] * 6 + ["90-120"] * 6,
        "value": [0.05, 0.06, 0.05, 0.06, 0.05, 0.15,  # Spike in last month
                  0.10, 0.12, 0.11, 0.12, 0.11, 0.28]   # Spike in last month
    })
    
    alerts = engine.risk_alerts(
        npl180_mom_bps=60,  # NPL up 60 bps (exceeds 50 bps threshold)
        rollrates_hist=rollrates_hist,
        dpd_7d_growth_amt=0.25  # 25% growth in 7 days (exceeds 20% threshold)
    )
    
    print(f"Generated {len(alerts)} risk alerts:")
    for alert in alerts:
        print(f"  [{alert['severity']}] {alert['title']}")
        print(f"    {alert['meta']}")
    
    # ===== Yield Alerts =====
    print("\n=== Testing Yield Alerts ===")
    
    # Simulated APR mix over time (last value deviates)
    apr_mix = pd.Series([35.5, 36.0, 35.8, 35.9, 36.1, 42.5])
    
    # Simulated effective APR over time (last value drops)
    apr_effective = pd.Series([34.2, 34.5, 34.3, 34.4, 34.6, 33.1])
    
    alerts = engine.yield_alerts(apr_mix, apr_effective)
    print(f"Generated {len(alerts)} yield alerts:")
    for alert in alerts:
        print(f"  [{alert['severity']}] {alert['title']}")
        print(f"    {alert['meta']}")
    
    # ===== Liquidity Alerts =====
    print("\n=== Testing Liquidity Alerts ===")
    
    alerts = engine.liquidity_alerts(
        collections_vs_plan=-0.15,  # 15% below plan (exceeds -10% threshold)
        bank_shortfall=True
    )
    
    print(f"Generated {len(alerts)} liquidity alerts:")
    for alert in alerts:
        print(f"  [{alert['severity']}] {alert['title']}")
        print(f"    {alert['meta']}")
    
    # ===== Growth Alerts =====
    print("\n=== Testing Growth Alerts ===")
    
    alerts = engine.growth_alerts(
        ltv_over_3_cac=True,  # CAC > LTV/3
        payback_months=15  # Exceeds 12 month threshold
    )
    
    print(f"Generated {len(alerts)} growth alerts:")
    for alert in alerts:
        print(f"  [{alert['severity']}] {alert['title']}")
        print(f"    {alert['meta']}")
    
    # ===== Slack Integration =====
    print("\n=== Slack Integration ===")
    print("To post alerts to Slack:")
    print("1. Set SLACK_WEBHOOK_URL in .env")
    print("2. Call: engine.post_to_slack(alerts)")
    print("\nNote: Webhook not configured, alerts not posted to Slack")


if __name__ == "__main__":
    main()
