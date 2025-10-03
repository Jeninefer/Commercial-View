"""
Commercial-View: DPD Bucket Classification System

This package provides consistent DPD (Days Past Due) bucket classification for
commercial loan portfolios with two complementary approaches:

1. PaymentProcessor (payment_processor.py):
   - Uses dpd_threshold (default 180 days) for accounting/regulatory default
   - Sets default_flag for loans >= 180 days past due
   - Provides detailed bucket descriptions for reporting
   - Suitable for financial reporting and regulatory compliance

2. FeatureEngineer (feature_engineer.py):
   - Uses risk_threshold (default 90 days) for risk analysis
   - Sets is_default flag for loans >= 90 days past due (high risk)
   - Provides risk categories for portfolio management
   - Suitable for risk segmentation and early intervention strategies

Key Distinction:
- DEFAULT (accounting): Loans >= 180 days past due (default_flag in PaymentProcessor)
- HIGH RISK (analytical): Loans >= 90 days past due (is_default in FeatureEngineer)

This dual approach allows for:
- Regulatory compliance with 180-day default definition
- Proactive risk management with 90-day high-risk threshold
- Consistent bucket classification across both methods
"""

from .payment_processor import PaymentProcessor
from .feature_engineer import FeatureEngineer

__all__ = ['PaymentProcessor', 'FeatureEngineer']

# Version information
__version__ = '1.0.0'
__author__ = 'Commercial-View Team'
