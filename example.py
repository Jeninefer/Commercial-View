"""Example usage of the StartupAnalyzer

This script demonstrates how to use the compute_viability_index method.
"""

from startup_analyzer import StartupAnalyzer


def main():
    """Demonstrate the StartupAnalyzer functionality."""
    
    # Create analyzer with default thresholds
    analyzer = StartupAnalyzer()
    
    print("Startup Viability Analyzer")
    print("=" * 50)
    print(f"Thresholds: {analyzer.thresholds}")
    print()
    
    # Example 1: High-performing startup
    print("Example 1: High-performing startup")
    metrics1 = {
        "runway_months": 24,
        "ltv_cac_ratio": 6.0,
        "nrr": 1.2
    }
    score1 = analyzer.compute_viability_index(metrics1)
    print(f"Metrics: {metrics1}")
    print(f"Viability Index: {score1}/100")
    print()
    
    # Example 2: Average startup
    print("Example 2: Average startup")
    metrics2 = {
        "runway_months": 12,
        "ltv_cac_ratio": 3.0,
        "nrr": 1.0
    }
    score2 = analyzer.compute_viability_index(metrics2)
    print(f"Metrics: {metrics2}")
    print(f"Viability Index: {score2}/100")
    print()
    
    # Example 3: Struggling startup
    print("Example 3: Struggling startup")
    metrics3 = {
        "runway_months": 3,
        "ltv_cac_ratio": 1.0,
        "nrr": 0.7
    }
    score3 = analyzer.compute_viability_index(metrics3)
    print(f"Metrics: {metrics3}")
    print(f"Viability Index: {score3}/100")
    print()
    
    # Example 4: Using alternate key name for LTV/CAC
    print("Example 4: Using alternate key name 'ltv_cac'")
    metrics4 = {
        "runway_months": 18,
        "ltv_cac": 4.5,
        "nrr": 1.1
    }
    score4 = analyzer.compute_viability_index(metrics4)
    print(f"Metrics: {metrics4}")
    print(f"Viability Index: {score4}/100")
    print()
    
    # Example 5: Custom thresholds
    print("Example 5: Using custom thresholds")
    custom_analyzer = StartupAnalyzer(thresholds={
        "runway_months_min": 6,
        "ltv_cac_ratio_min": 2.0,
        "nrr_min": 0.9
    })
    print(f"Custom Thresholds: {custom_analyzer.thresholds}")
    metrics5 = {
        "runway_months": 6,
        "ltv_cac_ratio": 2.0,
        "nrr": 0.9
    }
    score5 = custom_analyzer.compute_viability_index(metrics5)
    print(f"Metrics: {metrics5}")
    print(f"Viability Index: {score5}/100")


if __name__ == "__main__":
    main()
