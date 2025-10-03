"""Example usage of the EnhancedKPICalculator"""

import pandas as pd
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src import EnhancedKPICalculator, KPIConfig


def main():
    """Demonstrate the usage of EnhancedKPICalculator"""
    
    # Create a calculator with default configuration
    calculator = EnhancedKPICalculator()
    
    # Or with custom configuration
    # config = KPIConfig(risk_threshold_high=0.8, default_interest_rate=0.06)
    # calculator = EnhancedKPICalculator(config)
    
    # Example 1: Calculate portfolio KPIs only
    print("=" * 60)
    print("Example 1: Portfolio KPIs Only")
    print("=" * 60)
    
    loan_df = pd.DataFrame({
        "loan_id": [1, 2, 3, 4, 5],
        "principal": [100000, 200000, 150000, 120000, 180000],
        "balance": [80000, 180000, 140000, 100000, 170000],
        "status": ["active", "active", "default", "active", "charged_off"],
        "interest_paid": [5000, 12000, 7000, 6000, 9000],
        "days_past_due": [0, 0, 120, 15, 180],
    })
    
    portfolio_kpis = calculator.calculate_portfolio_kpis(loan_df)
    print("\nPortfolio KPIs:")
    print(f"Total Loans: {portfolio_kpis['total_loans']}")
    print(f"Total Principal: ${portfolio_kpis['portfolio_metrics']['total_principal']:,.2f}")
    print(f"Total Balance: ${portfolio_kpis['portfolio_metrics']['total_balance']:,.2f}")
    print(f"Default Rate: {portfolio_kpis['risk_metrics']['default_rate']:.2%}")
    print(f"Total Interest Income: ${portfolio_kpis['performance_metrics']['total_interest_income']:,.2f}")
    
    # Example 2: Calculate all metrics
    print("\n" + "=" * 60)
    print("Example 2: All Metrics (Portfolio + Business)")
    print("=" * 60)
    
    revenue_df = pd.DataFrame({
        "amount": [10000, 15000, 12000, 18000],
        "period": ["monthly", "monthly", "one-time", "monthly"],
    })
    
    customer_df = pd.DataFrame({
        "customer_id": [1, 2, 3, 4, 5],
        "acquisition_cost": [500, 600, 450, 550, 500],
        "status": ["active", "active", "active", "churned", "active"],
    })
    
    transaction_df = pd.DataFrame({
        "transaction_id": [1, 2, 3, 4, 5, 6],
        "amount": [1000, 2000, 1500, 3000, 2500, 1800],
        "status": ["success", "success", "failed", "success", "success", "completed"],
        "payment_method": ["card", "card", "bank", "card", "bank", "card"],
    })
    
    all_metrics = calculator.calculate_all_metrics(
        loan_df,
        revenue_df,
        customer_df,
        transaction_df
    )
    
    print(f"\nCalculation Timestamp: {all_metrics['calculation_timestamp']}")
    print("\nData Summary:")
    print(f"  Loans Count: {all_metrics['data_summary']['loans_count']}")
    print(f"  Revenue Available: {all_metrics['data_summary']['revenue_available']}")
    print(f"  Customer Data Available: {all_metrics['data_summary']['customer_data_available']}")
    print(f"  Transaction Data Available: {all_metrics['data_summary']['transaction_data_available']}")
    
    print("\nBusiness Metrics:")
    if "startup_metrics" in all_metrics["business_metrics"]:
        startup = all_metrics["business_metrics"]["startup_metrics"]
        print(f"  Startup - Total Customers: {startup['total_customers']}")
        print(f"  Startup - Total Revenue: ${startup['total_revenue']:,.2f}")
        print(f"  Startup - MRR: ${startup.get('mrr', 0):,.2f}")
        
        fintech = all_metrics["business_metrics"]["fintech_metrics"]
        print(f"  Fintech - Total Transactions: {fintech['total_transactions']}")
        print(f"  Fintech - Transaction Volume: ${fintech['total_transaction_volume']:,.2f}")
        print(f"  Fintech - Success Rate: {fintech['transaction_success_rate']:.2%}")
        
        valuation = all_metrics["business_metrics"]["valuation_metrics"]
        print(f"  Valuation - Average CLTV: ${valuation.get('average_cltv', 0):,.2f}")
        print(f"  Valuation - ARR: ${valuation.get('arr', 0):,.2f}")
        print(f"  Valuation - Churn Rate: {valuation.get('churn_rate', 0):.2%}")
    else:
        print(f"  Status: {all_metrics['business_metrics']['status']}")
        print(f"  Reason: {all_metrics['business_metrics']['reason']}")
    
    # Example 3: Calculate without business data
    print("\n" + "=" * 60)
    print("Example 3: Portfolio KPIs Only (via calculate_all_metrics)")
    print("=" * 60)
    
    result = calculator.calculate_all_metrics(loan_df)
    print(f"\nBusiness Metrics Status: {result['business_metrics']['status']}")
    print(f"Reason: {result['business_metrics']['reason']}")
    print(f"\nPortfolio KPIs still calculated:")
    print(f"Total Loans: {result['portfolio_kpis']['total_loans']}")


if __name__ == "__main__":
    main()
