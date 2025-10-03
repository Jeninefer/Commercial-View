"""Example usage of Commercial View KPI analytics."""
import pandas as pd
from commercial_view import MetricsCalculator

# Create sample commercial data
data = pd.DataFrame({
    'outstanding_balance': [10000, 25000, 50000, 15000, 30000],
    'interest_rate': [4.5, 5.0, 5.5, 4.8, 5.2],
    'credit_score': [720, 680, 750, 700, 740],
    'loan_term_months': [36, 48, 60, 36, 48]
})

# Initialize the calculator
calculator = MetricsCalculator()

# Calculate weighted metrics
weighted_metrics = calculator.calculate_weighted_metrics(
    df=data,
    metrics=['interest_rate', 'credit_score', 'loan_term_months'],
    weight_col='outstanding_balance'
)

print("Commercial View - KPI Analytics")
print("=" * 50)
print("\nSample Data:")
print(data)
print("\nWeighted Metrics (by outstanding_balance):")
for metric, value in weighted_metrics.items():
    print(f"  {metric}: {value:.2f}")
