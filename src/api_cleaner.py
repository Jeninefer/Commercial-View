"""
API cleaner module extracted from PR #14
Removes sample data generators from public API
"""


def clean_public_api():
    """Remove internal testing utilities from public exports"""
    # Based on PR #14 - create_sample_data removed from public API
    return {
        "public_exports": [
            "FeatureEngineer",
            "LoanAnalytics",
            "MetricsCalculator",
            "CustomerAnalytics",
        ],
        "internal_only": ["create_sample_data"],  # Available only via internal imports
    }
