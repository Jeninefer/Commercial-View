"""
Commercial-View package initialization
Clean public API without internal testing utilities (from PR #14)
"""

# Import functions directly to avoid relative import issues
import sys
import os
sys.path.append(os.path.dirname(__file__))

try:
    from feature_engineer import FeatureEngineer
    from loan_analytics import LoanAnalytics
    from metrics_calculator import MetricsCalculator
    from customer_analytics import CustomerAnalytics
    from dpd_analyzer import DPDAnalyzer
    from payment_processor import PaymentProcessor
    from pricing_enricher import PricingEnricher
    from abaco_core import AbacoCore
    from portfolio_optimizer import PortfolioOptimizer
    from google_drive_exporter import GoogleDriveExporter
    from evergreen import monthly_cohort, reactivation_flag
except ImportError as e:
    print(f"Warning: Some modules could not be imported: {e}")

# Clean public API - no sample data generators exposed
__all__ = [
    'FeatureEngineer', 
    'LoanAnalytics',
    'MetricsCalculator',
    'CustomerAnalytics',
    'DPDAnalyzer',
    'PaymentProcessor',
    'PricingEnricher',
    'AbacoCore',
    'PortfolioOptimizer',
    'GoogleDriveExporter',
    'monthly_cohort',
    'reactivation_flag'
]
