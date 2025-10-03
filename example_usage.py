"""
Example usage of the KPI Calculator
"""
from abaco_core import KPICalculator
import pandas as pd


def main():
    # Initialize the calculator
    calc = KPICalculator(export_path="/tmp/kpi_exports")
    
    print("=== KPI Calculator Example ===\n")
    
    # Example 1: Startup Metrics
    print("1. Computing Startup Metrics...")
    revenue_df = pd.DataFrame({
        "date": ["2023-01-01", "2023-02-01", "2023-03-01"],
        "recurring_revenue": [10000, 12000, 15000],
        "revenue": [10000, 12000, 15000],
        "customer_count": [100, 120, 150],
        "start_revenue": [10000, 12000, 15000],
        "end_revenue": [12000, 15000, 18000]
    })
    
    customer_df = pd.DataFrame({
        "churn_count": [5],
        "start_count": [100],
        "new_customers": [25]
    })
    
    expense_df = pd.DataFrame({
        "date": ["2023-01-01", "2023-02-01", "2023-03-01"],
        "total_expense": [8000, 8500, 9000],
        "cash_balance": [100000, 91500, 82500],
        "marketing_expense": [3000, 3500, 4000]
    })
    
    startup_metrics = calc.compute_startup_metrics(revenue_df, customer_df, expense_df)
    print(f"  MRR: ${startup_metrics.get('mrr', 0):,.2f}")
    print(f"  ARR: ${startup_metrics.get('arr', 0):,.2f}")
    print(f"  Churn Rate: {startup_metrics.get('churn_rate', 0):.2%}")
    print(f"  NRR: {startup_metrics.get('nrr', 0):.2f}")
    print(f"  CAC: ${startup_metrics.get('cac', 0):,.2f}")
    print(f"  Runway: {startup_metrics.get('runway_months', 0):.1f} months")
    
    # Example 2: Fintech Metrics
    print("\n2. Computing Fintech Metrics...")
    loan_df = pd.DataFrame({
        "loan_amount": [1000, 2000, 3000, 4000, 5000],
        "days_past_due": [0, 30, 100, 150, 200],
        "revenue": [100, 200, 300, 400, 500],
        "apr": [0.15, 0.18, 0.20, 0.22, 0.25],
        "eir": [0.12, 0.15, 0.17, 0.19, 0.22]
    })
    
    fintech_metrics = calc.compute_fintech_metrics(loan_df)
    print(f"  GMV: ${fintech_metrics.get('gmv', 0):,.2f}")
    print(f"  Default Rate: {fintech_metrics.get('default_rate', 0):.2%}")
    print(f"  Take Rate: {fintech_metrics.get('take_rate', 0):.2%}")
    print(f"  Avg EIR: {fintech_metrics.get('avg_eir', 0):.2%}")
    
    # Example 3: Full KPI Computation
    print("\n3. Computing All KPIs...")
    data_dict = {
        "revenue": revenue_df,
        "customer": customer_df,
        "expense": expense_df,
        "loan": loan_df
    }
    
    all_metrics = calc.compute_kpis(data_dict)
    
    # Get summary
    summary = calc.summarize_kpis(all_metrics)
    print("\n  Summary:")
    for key, value in summary.items():
        if value is not None:
            if isinstance(value, (int, float)):
                print(f"    {key}: {value}")
    
    # Example 4: Export results
    print("\n4. Exporting Results...")
    json_path = calc.export_metrics_to_json(all_metrics)
    print(f"  JSON exported to: {json_path}")
    
    csv_paths = calc.export_metrics_to_csv(all_metrics)
    for category, path in csv_paths.items():
        print(f"  {category.capitalize()} CSV exported to: {path}")
    
    # Example 5: Viability Index
    viability = all_metrics.get("viability", {}).get("viability_index", 0)
    print(f"\n5. Viability Index: {viability}/100")
    if viability >= 80:
        print("   Status: Excellent")
    elif viability >= 60:
        print("   Status: Good")
    elif viability >= 40:
        print("   Status: Fair")
    else:
        print("   Status: Needs Improvement")
    
    print("\n=== Example Complete ===")


if __name__ == "__main__":
    main()
