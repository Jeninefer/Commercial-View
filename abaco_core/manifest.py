"""
ABACO Core Manifest - Buckets, Client Types, and Classification Logic
"""
from typing import Dict, List, Optional
import pandas as pd

# APR Buckets (in percentage)
APR_BUCKETS = [
    (0.0, 15.0, "0-15%"),
    (15.0, 20.0, "15-20%"),
    (20.0, 25.0, "20-25%"),
    (25.0, 30.0, "25-30%"),
    (30.0, float("inf"), "30%+"),
]

# Line Amount Buckets (in currency units)
LINE_BUCKETS = [
    (0, 100_000, "0-100k"),
    (100_000, 250_000, "100k-250k"),
    (250_000, 500_000, "250k-500k"),
    (500_000, 1_000_000, "500k-1M"),
    (1_000_000, 5_000_000, "1M-5M"),
    (5_000_000, float("inf"), "5M+"),
]

# Client Types based on revenue and established criteria
CLIENT_TYPES = {
    "startup": {"revenue_max": 5_000_000, "years_max": 3},
    "growing": {"revenue_min": 5_000_000, "revenue_max": 50_000_000, "years_min": 3},
    "enterprise": {"revenue_min": 50_000_000},
}

# Payer Quality Buckets (based on payment performance)
PAYER_BUCKETS = [
    ("A", "Excellent - 0-5% DPD history"),
    ("B", "Good - 5-15% DPD history"),
    ("C", "Fair - 15-30% DPD history"),
    ("D", "Poor - 30%+ DPD history"),
]

# NAICS Industry Classification Scheme (simplified)
NAICS_SCHEME = {
    "11": "Agriculture, Forestry, Fishing and Hunting",
    "21": "Mining, Quarrying, and Oil and Gas Extraction",
    "22": "Utilities",
    "23": "Construction",
    "31": "Manufacturing - Food & Textiles",
    "32": "Manufacturing - Wood, Paper & Chemicals",
    "33": "Manufacturing - Metals & Machinery",
    "42": "Wholesale Trade",
    "44": "Retail Trade - Motor Vehicles",
    "45": "Retail Trade - General Merchandise",
    "48": "Transportation and Warehousing",
    "51": "Information",
    "52": "Finance and Insurance",
    "53": "Real Estate and Rental",
    "54": "Professional, Scientific, and Technical Services",
    "55": "Management of Companies",
    "56": "Administrative and Support Services",
    "61": "Educational Services",
    "62": "Health Care and Social Assistance",
    "71": "Arts, Entertainment, and Recreation",
    "72": "Accommodation and Food Services",
    "81": "Other Services (except Public Administration)",
    "92": "Public Administration",
}


def bucket_apr(apr: float) -> str:
    """
    Classify APR into bucket.
    
    Args:
        apr: Annual Percentage Rate (as percentage, e.g., 18.5)
    
    Returns:
        Bucket label (e.g., "15-20%")
    """
    for low, high, label in APR_BUCKETS:
        if low <= apr < high:
            return label
    return APR_BUCKETS[-1][2]  # Default to highest bucket


def bucket_line(amount: float) -> str:
    """
    Classify line amount into bucket.
    
    Args:
        amount: Line amount in currency units
    
    Returns:
        Bucket label (e.g., "100k-250k")
    """
    for low, high, label in LINE_BUCKETS:
        if low <= amount < high:
            return label
    return LINE_BUCKETS[-1][2]  # Default to highest bucket


def bucket_payer(dpd_rate: float) -> str:
    """
    Classify payer quality based on DPD (Days Past Due) history.
    
    Args:
        dpd_rate: Percentage of time in DPD (0.0 to 100.0)
    
    Returns:
        Payer quality grade (A, B, C, or D)
    """
    if dpd_rate < 5.0:
        return "A"
    elif dpd_rate < 15.0:
        return "B"
    elif dpd_rate < 30.0:
        return "C"
    else:
        return "D"


def classify_client(revenue: float, years_in_business: float) -> str:
    """
    Classify client type based on revenue and years in business.
    
    Args:
        revenue: Annual revenue
        years_in_business: Years the company has been operating
    
    Returns:
        Client type: "startup", "growing", or "enterprise"
    """
    if revenue < CLIENT_TYPES["startup"]["revenue_max"] and years_in_business <= CLIENT_TYPES["startup"]["years_max"]:
        return "startup"
    elif revenue >= CLIENT_TYPES["enterprise"]["revenue_min"]:
        return "enterprise"
    else:
        return "growing"


def map_naics(naics_code: str) -> str:
    """
    Map NAICS code to industry description.
    
    Args:
        naics_code: NAICS code (2-6 digits)
    
    Returns:
        Industry description
    """
    # Take first 2 digits
    prefix = naics_code[:2] if len(naics_code) >= 2 else naics_code
    return NAICS_SCHEME.get(prefix, "Unknown Industry")


def share(series: pd.Series) -> Dict[str, float]:
    """
    Calculate percentage share for each item in series.
    
    Args:
        series: Pandas Series with numeric values
    
    Returns:
        Dictionary with percentage shares
    """
    total = series.sum()
    if total == 0:
        return {str(k): 0.0 for k in series.index}
    return {str(k): float(v / total * 100) for k, v in series.items()}
