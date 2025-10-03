"""
Example usage of MetricsCalculator
"""
import pandas as pd
from src.metrics_calculator import MetricsCalculator


def main():
    """Demonstrate the usage of MetricsCalculator"""
    
    # Create an instance of the calculator
    calculator = MetricsCalculator()
    
    # Example 1: Basic MRR/ARR calculation
    print("=" * 60)
    print("Example 1: MRR/ARR Calculation")
    print("=" * 60)
    
    revenue_df = pd.DataFrame({
        'date': ['2023-01-01', '2023-02-01', '2023-03-01'],
        'recurring_revenue': [10000, 12000, 15000]
    })
    customer_df = pd.DataFrame({'customer_id': [1, 2, 3]})
    
    metrics = calculator.compute_startup_metrics(revenue_df, customer_df)
    print(f"MRR: ${metrics.get('mrr', 0):,.2f}")
    print(f"ARR: ${metrics.get('arr', 0):,.2f}")
    
    # Example 2: Comprehensive metrics with all data
    print("\n" + "=" * 60)
    print("Example 2: Comprehensive Startup Metrics")
    print("=" * 60)
    
    revenue_df = pd.DataFrame({
        'date': ['2023-01-01', '2023-02-01', '2023-03-01'],
        'recurring_revenue': [10000, 12000, 15000],
        'revenue': [10000, 12000, 15000],
        'customer_count': [100, 110, 120],
        'start_revenue': [10000, 12000, 15000],
        'end_revenue': [12000, 15000, 18000]
    })
    
    customer_df = pd.DataFrame({
        'new_customers': [10, 15, 20],
        'churn_count': [5, 6, 7],
        'start_count': [100, 110, 120]
    })
    
    expense_df = pd.DataFrame({
        'date': ['2023-01-01', '2023-02-01', '2023-03-01'],
        'marketing_expense': [5000, 6000, 7000],
        'total_expense': [20000, 22000, 24000],
        'cash_balance': [200000, 178000, 154000]
    })
    
    metrics = calculator.compute_startup_metrics(revenue_df, customer_df, expense_df)
    
    print(f"\nRevenue Metrics:")
    print(f"  MRR: ${metrics.get('mrr', 0):,.2f}")
    print(f"  ARR: ${metrics.get('arr', 0):,.2f}")
    print(f"  NRR: {metrics.get('nrr', 0):.2%}")
    print(f"  ARPU: ${metrics.get('arpu', 0):,.2f}")
    
    print(f"\nCustomer Metrics:")
    print(f"  Churn Rate: {metrics.get('churn_rate', 0):.2%}")
    print(f"  CAC: ${metrics.get('cac', 0):,.2f}")
    
    if 'ltv' in metrics:
        print(f"  LTV: ${metrics.get('ltv', 0):,.2f}")
        if 'ltv_cac_ratio' in metrics:
            print(f"  LTV/CAC Ratio: {metrics.get('ltv_cac_ratio', 0):.2f}x")
    
    print(f"\nFinancial Health:")
    print(f"  Monthly Burn: ${metrics.get('monthly_burn', 0):,.2f}")
    runway = metrics.get('runway_months', 0)
    if runway != float('inf'):
        print(f"  Runway: {runway:.1f} months")
    else:
        print(f"  Runway: Infinite (no burn)")
    
    # Example 3: Safe division demonstration
    print("\n" + "=" * 60)
    print("Example 3: Safe Division Helper")
    print("=" * 60)
    
    print(f"10 / 2 = {calculator.safe_division(10, 2, 0)}")
    print(f"10 / 0 (default 0) = {calculator.safe_division(10, 0, 0)}")
    print(f"10 / 0 (default inf) = {calculator.safe_division(10, 0, float('inf'))}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
