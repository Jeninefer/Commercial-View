#!/usr/bin/env python3
"""
Example demonstrating the safe_division method from Commercial-View
"""

from commercial_view import Calculator
import pandas as pd
import numpy as np


def main():
    """Demonstrate safe division functionality"""
    calc = Calculator()
    
    print("=" * 60)
    print("Commercial-View: Safe Division Examples")
    print("=" * 60)
    
    # Example 1: Scalar division
    print("\n1. Scalar Division Examples:")
    print("-" * 40)
    print(f"   10 / 2 = {calc.safe_division(10, 2)}")
    print(f"   10 / 0 = {calc.safe_division(10, 0)} (returns NaN by default)")
    print(f"   10 / 0 (default=0) = {calc.safe_division(10, 0, default=0)}")
    print(f"   15.5 / 2.5 = {calc.safe_division(15.5, 2.5)}")
    
    # Example 2: Pandas Series division
    print("\n2. Pandas Series Division Examples:")
    print("-" * 40)
    revenue = pd.Series([1000, 2000, 3000, 4000], 
                       index=['Q1', 'Q2', 'Q3', 'Q4'],
                       name='Revenue')
    costs = pd.Series([800, 0, 2500, 3200], 
                     index=['Q1', 'Q2', 'Q3', 'Q4'],
                     name='Costs')
    
    print(f"   Revenue: {revenue.tolist()}")
    print(f"   Costs: {costs.tolist()}")
    
    margins = calc.safe_division(revenue - costs, revenue, default=0) * 100
    print(f"\n   Profit Margins (%):")
    for quarter, margin in margins.items():
        print(f"      {quarter}: {margin:.1f}%")
    
    # Example 3: NumPy array division
    print("\n3. NumPy Array Division Examples:")
    print("-" * 40)
    sales = np.array([100, 200, 150, 0, 250])
    targets = np.array([120, 180, 150, 200, 0])
    
    print(f"   Sales: {sales.tolist()}")
    print(f"   Targets: {targets.tolist()}")
    
    performance = calc.safe_division(sales, targets, default=0) * 100
    print(f"\n   Performance vs Target (%):")
    for i, perf in enumerate(performance):
        print(f"      Month {i+1}: {perf:.1f}%")
    
    # Example 4: Handling invalid data
    print("\n4. Handling Invalid Data:")
    print("-" * 40)
    values = pd.Series([10, 'invalid', 30, None, 50])
    divisors = pd.Series([2, 4, 0, 5, 10])
    
    print(f"   Values: {values.tolist()}")
    print(f"   Divisors: {divisors.tolist()}")
    
    results = calc.safe_division(values, divisors, default=-1)
    print(f"   Results: {results.tolist()}")
    print("   (Invalid values and division by zero replaced with -1)")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
