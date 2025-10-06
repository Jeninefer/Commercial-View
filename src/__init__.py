"""
Commercial-View package initialization
Enhanced commercial lending platform with comprehensive feature set
"""

import sys
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Configure package-level logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

# Version information
__version__ = "1.0.0"
__title__ = "Commercial-View"
__description__ = "Commercial lending analytics and portfolio management platform"
__author__ = "Commercial-View Team"

# Package metadata
PACKAGE_INFO = {
    "version": __version__,
    "title": __title__,
    "description": __description__,
    "author": __author__,
    "python_requires": ">=3.8",
    "commercial_lending_features": [
        "loan_pricing", "risk_assessment", "dpd_analysis", 
        "kpi_generation", "portfolio_optimization", "regulatory_reporting"
    ]
}

# Core commercial lending modules
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
    
    # Enhanced commercial lending modules
    try:
        from commercial_view.pricing.calculator import PricingCalculator
        from commercial_view.risk.assessor import RiskAssessor
        from commercial_view.kpi.generator import KPIGenerator
        from commercial_view.export.manager import ExportManager
        from commercial_view.regulatory.compliance import ComplianceValidator
        from commercial_view.stress.testing import StressTestEngine
        
        _ENHANCED_MODULES_AVAILABLE = True
    except ImportError:
        _ENHANCED_MODULES_AVAILABLE = False
        
    # Utility modules
    try:
        from utils.schema_converter import CommercialLendingSchemaConverter
        from utils.schema_parser import CommercialLendingSchemaParser
        from utils.retry import CommercialLendingRetry
        
        _UTILITY_MODULES_AVAILABLE = True
    except ImportError:
        _UTILITY_MODULES_AVAILABLE = False
        
    _CORE_MODULES_AVAILABLE = True
    
except ImportError as e:
    logging.warning(f"Some core modules could not be imported: {e}")
    _CORE_MODULES_AVAILABLE = False
    _ENHANCED_MODULES_AVAILABLE = False
    _UTILITY_MODULES_AVAILABLE = False

# Configuration management
def get_package_info() -> Dict[str, Any]:
    """Get comprehensive package information"""
    return {
        **PACKAGE_INFO,
        "modules_status": {
            "core_modules": _CORE_MODULES_AVAILABLE,
            "enhanced_modules": _ENHANCED_MODULES_AVAILABLE,
            "utility_modules": _UTILITY_MODULES_AVAILABLE
        },
        "available_features": get_available_features()
    }

def get_available_features() -> Dict[str, bool]:
    """Get status of available commercial lending features"""
    features = {
        "basic_analytics": _CORE_MODULES_AVAILABLE,
        "loan_pricing": _ENHANCED_MODULES_AVAILABLE,
        "risk_assessment": _ENHANCED_MODULES_AVAILABLE,
        "kpi_generation": _ENHANCED_MODULES_AVAILABLE,
        "data_export": _ENHANCED_MODULES_AVAILABLE,
        "regulatory_compliance": _ENHANCED_MODULES_AVAILABLE,
        "stress_testing": _ENHANCED_MODULES_AVAILABLE,
        "schema_management": _UTILITY_MODULES_AVAILABLE,
        "retry_mechanisms": _UTILITY_MODULES_AVAILABLE
    }
    
    return features

def validate_environment() -> Dict[str, Any]:
    """Validate Commercial-View environment setup"""
    validation_results = {
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "python_compatible": sys.version_info >= (3, 8),
        "package_path": Path(__file__).parent,
        "modules_loaded": get_available_features(),
        "issues": []
    }
    
    # Check Python version
    if not validation_results["python_compatible"]:
        validation_results["issues"].append("Python 3.8+ required")
    
    # Check core modules
    if not _CORE_MODULES_AVAILABLE:
        validation_results["issues"].append("Core modules not available")
    
    # Check for common commercial lending dependencies
    try:
        import pandas as pd
        import numpy as np
        validation_results["pandas_version"] = pd.__version__
        validation_results["numpy_version"] = np.__version__
    except ImportError:
        validation_results["issues"].append("Missing data science dependencies (pandas, numpy)")
    
    return validation_results

# Clean public API - organized by functionality
_CORE_EXPORTS = [
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
] if _CORE_MODULES_AVAILABLE else []

_ENHANCED_EXPORTS = [
    'PricingCalculator',
    'RiskAssessor', 
    'KPIGenerator',
    'ExportManager',
    'ComplianceValidator',
    'StressTestEngine'
] if _ENHANCED_MODULES_AVAILABLE else []

_UTILITY_EXPORTS = [
    'CommercialLendingSchemaConverter',
    'CommercialLendingSchemaParser',
    'CommercialLendingRetry'
] if _UTILITY_MODULES_AVAILABLE else []

_PACKAGE_EXPORTS = [
    'get_package_info',
    'get_available_features', 
    'validate_environment',
    '__version__',
    'PACKAGE_INFO'
]

__all__ = _CORE_EXPORTS + _ENHANCED_EXPORTS + _UTILITY_EXPORTS + _PACKAGE_EXPORTS

# Commercial lending convenience functions
def create_loan_analyzer() -> Optional[Any]:
    """Create a comprehensive loan analyzer with all available features"""
    if not _CORE_MODULES_AVAILABLE:
        logging.error("Core modules not available for loan analyzer")
        return None
    
    try:
        analyzer_config = {
            "feature_engineer": FeatureEngineer(),
            "loan_analytics": LoanAnalytics(),
            "metrics_calculator": MetricsCalculator(),
            "dpd_analyzer": DPDAnalyzer()
        }
        
        if _ENHANCED_MODULES_AVAILABLE:
            analyzer_config.update({
                "pricing_calculator": PricingCalculator(),
                "risk_assessor": RiskAssessor(),
                "kpi_generator": KPIGenerator()
            })
        
        return analyzer_config
    except Exception as e:
        logging.error(f"Failed to create loan analyzer: {e}")
        return None

def create_portfolio_manager() -> Optional[Any]:
    """Create a comprehensive portfolio manager"""
    if not _CORE_MODULES_AVAILABLE:
        logging.error("Core modules not available for portfolio manager")
        return None
    
    try:
        manager_config = {
            "portfolio_optimizer": PortfolioOptimizer(),
            "customer_analytics": CustomerAnalytics(),
            "payment_processor": PaymentProcessor()
        }
        
        if _ENHANCED_MODULES_AVAILABLE:
            manager_config.update({
                "stress_test_engine": StressTestEngine(),
                "compliance_validator": ComplianceValidator()
            })
        
        return manager_config
    except Exception as e:
        logging.error(f"Failed to create portfolio manager: {e}")
        return None

# Package initialization diagnostics
def run_diagnostics() -> Dict[str, Any]:
    """Run comprehensive package diagnostics"""
    diagnostics = {
        "timestamp": sys.modules.get('datetime', type('', (), {
            'datetime': type('', (), {'now': lambda: 'unavailable'})()
        })).datetime.now(),
        "package_info": get_package_info(),
        "environment": validate_environment(),
        "import_status": {
            "successful_imports": len([m for m in __all__ if m in globals()]),
            "total_exports": len(__all__),
            "success_rate": len([m for m in __all__ if m in globals()]) / len(__all__) if __all__ else 0
        }
    }
    
    return diagnostics

# Add convenience exports to __all__
__all__.extend(['create_loan_analyzer', 'create_portfolio_manager', 'run_diagnostics'])

# Package initialization message
if _CORE_MODULES_AVAILABLE:
    available_features = sum(get_available_features().values())
    total_features = len(get_available_features())
    logging.info(f"Commercial-View v{__version__} initialized with {available_features}/{total_features} features available")
else:
    logging.warning("Commercial-View initialized with limited functionality due to import issues")
