#!/usr/bin/env python3
"""
Commercial-View Portfolio Processing Script

Main entry point for processing commercial lending portfolios and generating
DPD analysis, risk bucketing, and KPI reports.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Dict, Any
import yaml
import json
from datetime import datetime
import pandas as pd
import numpy as np
import logging

from kpi_calculator import compute_arr, calculate_progress_percentage, update_snapshot
import kpi_calculator
from csv_processor import CSVProcessor
from evergreen_analytics import (
    analyze_cohort_retention,
    calculate_customer_reactivation,
    track_customer_lifecycle,
)
from evergreen import monthly_cohort, reactivation_flag
from feature_engineer import FeatureEngineer
from loan_analytics import LoanAnalytics
from metrics_calculator import MetricsCalculator
from payment_processor import PaymentProcessor
from abaco_core import AbacoCore
from portfolio_optimizer import PortfolioOptimizer
from disbursement_optimizer import DisbursementOptimizer
from data_processor import DataProcessor
from field_detector import FieldDetector
from google_drive_exporter import GoogleDriveExporter
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def load_config(config_dir: str) -> Dict[str, Any]:
    """Load all configuration files from the config directory."""
    configs = {}

    config_files = [
        "column_maps.yml",
        "pricing_config.yml",
        "dpd_policy.yml",
        "export_config.yml",
    ]

    for config_file in config_files:
        config_path = Path(config_dir) / config_file
        if config_path.exists():
            with open(config_path, "r") as f:
                config_name = config_file.replace(".yml", "")
                configs[config_name] = yaml.safe_load(f)
        else:
            print(f"Warning: Configuration file {config_file} not found")

    return configs


def create_export_directories(export_config: Dict[str, Any]) -> None:
    """Create necessary export directories."""
    export_paths = export_config.get("export_paths", {})

    directories = [
        export_paths.get("base_path", "./abaco_runtime/exports"),
        export_paths.get("kpi_json", "./abaco_runtime/exports/kpi/json"),
        export_paths.get("kpi_csv", "./abaco_runtime/exports/kpi/csv"),
        "./abaco_runtime/exports/dpd",
        "./abaco_runtime/exports/buckets",
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")


def generate_sample_output(export_config: Dict[str, Any]) -> None:
    """Generate sample output files to demonstrate the system."""
    export_paths = export_config.get("export_paths", {})
    base_path = export_paths.get("base_path", "./abaco_runtime/exports")

    # Sample DPD data
    dpd_data = {
        "analysis_date": datetime.now().isoformat(),
        "portfolio_summary": {
            "total_loans": 1000,
            "total_exposure": 50000000,
            "default_rate": 0.05,
        },
        "dpd_analysis": {
            "current": {"count": 850, "amount": 42500000},
            "1_30_days": {"count": 100, "amount": 5000000},
            "31_60_days": {"count": 30, "amount": 1500000},
            "61_90_days": {"count": 15, "amount": 750000},
            "90_plus_days": {"count": 5, "amount": 250000},
        },
    }

    # Sample KPI data
    kpi_data = {
        "generated_at": datetime.now().isoformat(),
        "kpis": {
            "portfolio_at_risk": 0.15,
            "default_rate": 0.05,
            "recovery_rate": 0.75,
            "provision_coverage": 0.12,
            "net_charge_off_rate": 0.03,
        },
    }

    # Write sample files
    with open(f"{base_path}/dpd/dpd_analysis.json", "w") as f:
        json.dump(dpd_data, f, indent=2)

    with open(
        f"{export_paths.get('kpi_json', './abaco_runtime/exports/kpi/json')}/kpi_report.json",
        "w",
    ) as f:
        json.dump(kpi_data, f, indent=2)

    print("Generated sample output files:")
    print(f"  - {base_path}/dpd/dpd_analysis.json")
    print(
        f"  - {export_paths.get('kpi_json', './abaco_runtime/exports/kpi/json')}/kpi_report.json"
    )


def enhanced_kpi_analysis(configs: Dict[str, Any]) -> Dict[str, Any]:
    """Enhanced KPI analysis with extracted features"""
    csv_processor = CSVProcessor()

    # Load and process CSV data
    csv_data = csv_processor.load_csv_files()

    # Calculate enhanced KPIs with null checks
    results = {
        "outstanding_portfolio": csv_processor.calculate_outstanding_portfolio(
            csv_data.get("payment_schedule") or pd.DataFrame()
        ),
        "tenor_mix": csv_processor.calculate_tenor_mix(
            csv_data.get("loan_data") or pd.DataFrame()
        ),
        "npl_metrics": csv_processor.calculate_npl_metrics(
            csv_data.get("historic_real_payment") or pd.DataFrame()
        ),
    }

    # Add startup metrics example
    startup_data = {"startup": {"mrr": 5000.0}, "valuation": {"pre_money": 1000000.0}}
    enhanced_startup = update_snapshot(startup_data, 250000.0)
    results["startup_metrics"] = enhanced_startup

    # Progress calculations
    results["progress_metrics"] = {
        "portfolio_progress": calculate_progress_percentage(7610000, 7800000),
        "apr_progress": calculate_progress_percentage(18.2, 18.5),
    }

    return results


def comprehensive_analysis(configs: Dict[str, Any]) -> Dict[str, Any]:
    """Comprehensive analysis with all extracted features from PRs #7-12"""
    results = {}

    # Initialize all modules
    feature_engineer = FeatureEngineer()
    loan_analytics = LoanAnalytics()
    metrics_calc = MetricsCalculator()

    # Sample data for demonstration
    sample_portfolio = pd.DataFrame(
        {
            "customer_id": range(50),
            "loan_count": np.random.randint(1, 5, 50),
            "last_active_date": pd.date_range("2023-01-01", periods=50, freq="30D"),
            "transaction_date": pd.date_range("2023-01-01", periods=50, freq="15D"),
            "outstanding_balance": np.abs(np.random.normal(25000, 10000, 50)),
            "apr": np.random.normal(15.5, 2.5, 50),
            "eir": np.random.normal(16.2, 2.8, 50),
            "term": np.random.randint(12, 60, 50),
            "credit_score": np.random.normal(650, 80, 50),
        }
    )

    # Cohort retention analysis
    cohort_retention = monthly_cohort(
        sample_portfolio, "customer_id", "transaction_date"
    )

    # Customer reactivation analysis
    reactivation_analysis = reactivation_flag(
        sample_portfolio, "customer_id", "transaction_date"
    )

    # Customer classification
    classified_customers = feature_engineer.classify_client_type(sample_portfolio)

    # Weighted portfolio analytics
    weighted_stats = loan_analytics.calculate_weighted_stats(
        sample_portfolio, metrics=["apr", "eir", "term"]
    )

    # Weighted metrics calculation
    weighted_metrics = metrics_calc.calculate_weighted_metrics(
        sample_portfolio,
        metrics=["credit_score", "apr"],
        weight_col="outstanding_balance",
    )

    results.update(
        {
            "cohort_retention_matrix": (
                cohort_retention.to_dict() if not cohort_retention.empty else {}
            ),
            "reactivation_count": int(reactivation_analysis["reactivated"].sum()),
            "customer_type_distribution": classified_customers["customer_type"]
            .value_counts()
            .to_dict(),
            "weighted_portfolio_stats": (
                weighted_stats.to_dict("records")[0] if not weighted_stats.empty else {}
            ),
            "weighted_metrics": weighted_metrics,
            "portfolio_summary": {
                "total_customers": len(sample_portfolio),
                "total_exposure": float(sample_portfolio["outstanding_balance"].sum()),
                "avg_credit_score": float(sample_portfolio["credit_score"].mean()),
            },
        }
    )

    return results


def enhanced_analysis(configs: Dict[str, Any]) -> Dict[str, Any]:
    """Enhanced analysis with all extracted features from PRs #7-12"""
    results = {}

    # Initialize all modules
    feature_engineer = FeatureEngineer()
    loan_analytics = LoanAnalytics()
    metrics_calc = MetricsCalculator()

    # Sample data for demonstration
    sample_portfolio = pd.DataFrame(
        {
            "customer_id": range(50),
            "loan_count": np.random.randint(1, 5, 50),
            "last_active_date": pd.date_range("2023-01-01", periods=50, freq="30D"),
            "transaction_date": pd.date_range("2023-01-01", periods=50, freq="15D"),
            "outstanding_balance": np.abs(np.random.normal(25000, 10000, 50)),
            "apr": np.random.normal(15.5, 2.5, 50),
            "eir": np.random.normal(16.2, 2.8, 50),
            "term": np.random.randint(12, 60, 50),
            "credit_score": np.random.normal(650, 80, 50),
        }
    )

    # Cohort retention analysis
    cohort_retention = monthly_cohort(
        sample_portfolio, "customer_id", "transaction_date"
    )

    # Customer reactivation analysis
    reactivation_analysis = reactivation_flag(
        sample_portfolio, "customer_id", "transaction_date"
    )

    # Customer classification
    classified_customers = feature_engineer.classify_client_type(sample_portfolio)

    # Weighted portfolio analytics
    weighted_stats = loan_analytics.calculate_weighted_stats(
        sample_portfolio, metrics=["apr", "eir", "term"]
    )

    # Weighted metrics calculation
    weighted_metrics = metrics_calc.calculate_weighted_metrics(
        sample_portfolio,
        metrics=["credit_score", "apr"],
        weight_col="outstanding_balance",
    )

    results.update(
        {
            "cohort_retention_matrix": (
                cohort_retention.to_dict() if not cohort_retention.empty else {}
            ),
            "reactivation_count": int(reactivation_analysis["reactivated"].sum()),
            "customer_type_distribution": classified_customers["customer_type"]
            .value_counts()
            .to_dict(),
            "weighted_portfolio_stats": (
                weighted_stats.to_dict("records")[0] if not weighted_stats.empty else {}
            ),
            "weighted_metrics": weighted_metrics,
            "portfolio_summary": {
                "total_customers": len(sample_portfolio),
                "total_exposure": float(sample_portfolio["outstanding_balance"].sum()),
                "avg_credit_score": float(sample_portfolio["credit_score"].mean()),
            },
        }
    )

    return results


class ProcessPortfolio:
    """
    Portfolio processing CLI that implements proper data path resolution
    Follows sequence diagram: User/CLI -> process_portfolio -> data_loader
    """

    def __init__(self):
        self.data_loader = None
        self.processing_timestamp = datetime.now()

    def process_with_cli_args(self, data_dir: Optional[str] = None) -> dict:
        """
        Process portfolio with optional CLI data directory
        Implements sequence diagram flow for path resolution
        """
        logger.info("🚀 Starting Commercial-View portfolio processing...")

        # Initialize DataLoader with proper path resolution
        # This follows the sequence diagram logic:
        # - If --data-dir provided: use CLI path
        # - If no --data-dir: DataLoader checks ENV var then uses default
        self.data_loader = DataLoader(base_path=data_dir)

        results = {
            "processing_timestamp": self.processing_timestamp.isoformat(),
            "data_path_used": str(self.data_loader.base_path.absolute()),
            "datasets_processed": {},
            "portfolio_metrics": {},
            "processing_status": "in_progress",
        }

        try:
            # Process each dataset following sequence diagram
            results["datasets_processed"] = self._process_all_datasets()
            results["portfolio_metrics"] = self._calculate_portfolio_metrics()
            results["processing_status"] = "completed"

            logger.info("✅ Portfolio processing completed successfully")

        except Exception as e:
            logger.error(f"❌ Portfolio processing failed: {e}")
            results["processing_status"] = "failed"
            results["error"] = str(e)
            raise

        return results

    def _process_all_datasets(self) -> dict:
        """
        Process all datasets with proper error handling
        Implements the file existence checks from sequence diagram
        """
        datasets_results = {}

        # Process loan data
        try:
            loan_df = self.data_loader.load_loan_data()
            datasets_results["loan_data"] = {
                "status": "success",
                "records": len(loan_df) if loan_df is not None else 0,
                "columns": list(loan_df.columns) if loan_df is not None else [],
            }
        except FileNotFoundError as e:
            logger.error(f"Loan data not found: {e}")
            datasets_results["loan_data"] = {
                "status": "file_not_found",
                "error": str(e),
            }
        except Exception as e:
            logger.error(f"Error processing loan data: {e}")
            datasets_results["loan_data"] = {"status": "error", "error": str(e)}

        # Process payment schedule
        try:
            payment_df = self.data_loader.load_payment_schedule()
            datasets_results["payment_schedule"] = {
                "status": "success",
                "records": len(payment_df) if payment_df is not None else 0,
                "columns": list(payment_df.columns) if payment_df is not None else [],
            }
        except FileNotFoundError as e:
            logger.error(f"Payment schedule not found: {e}")
            datasets_results["payment_schedule"] = {
                "status": "file_not_found",
                "error": str(e),
            }
        except Exception as e:
            logger.error(f"Error processing payment schedule: {e}")
            datasets_results["payment_schedule"] = {"status": "error", "error": str(e)}

        # Process historic payments
        try:
            historic_df = self.data_loader.load_historic_real_payment()
            datasets_results["historic_real_payment"] = {
                "status": "success",
                "records": len(historic_df) if historic_df is not None else 0,
                "columns": list(historic_df.columns) if historic_df is not None else [],
            }
        except FileNotFoundError as e:
            logger.error(f"Historic payment data not found: {e}")
            datasets_results["historic_real_payment"] = {
                "status": "file_not_found",
                "error": str(e),
            }
        except Exception as e:
            logger.error(f"Error processing historic payments: {e}")
            datasets_results["historic_real_payment"] = {
                "status": "error",
                "error": str(e),
            }

        return datasets_results

    def _calculate_portfolio_metrics(self) -> dict:
        """Calculate basic portfolio metrics from loaded data"""
        metrics = {
            "total_loans": 0,
            "total_outstanding": 0.0,
            "average_loan_size": 0.0,
            "active_customers": 0,
        }

        try:
            # Get loan data for metrics
            loan_df = self.data_loader.load_loan_data()
            if loan_df is not None and not loan_df.empty:
                # Filter active loans
                active_loans = (
                    loan_df[loan_df["Status"] == "Active"]
                    if "Status" in loan_df.columns
                    else loan_df
                )

                metrics["total_loans"] = len(active_loans)

                if "Loan Amount" in active_loans.columns:
                    loan_amounts = pd.to_numeric(
                        active_loans["Loan Amount"], errors="coerce"
                    )
                    metrics["total_outstanding"] = float(loan_amounts.sum())
                    metrics["average_loan_size"] = (
                        float(loan_amounts.mean()) if len(loan_amounts) > 0 else 0.0
                    )

                if "Customer ID" in active_loans.columns:
                    metrics["active_customers"] = active_loans["Customer ID"].nunique()

        except Exception as e:
            logger.error(f"Error calculating portfolio metrics: {e}")
            metrics["calculation_error"] = str(e)

        return metrics


def main():
    """Main processing function."""
    parser = argparse.ArgumentParser(description="Process commercial lending portfolio")
    parser.add_argument("--config", required=True, help="Configuration directory path")
    parser.add_argument("--data", help="Input data file path (optional for demo)")

    args = parser.parse_args()

    print("Commercial-View Portfolio Processing")
    print("=" * 50)

    # Load configurations
    print(f"Loading configurations from: {args.config}")
    configs = load_config(args.config)

    if not configs:
        print("Error: No valid configuration files found")
        sys.exit(1)

    # Create export directories
    print("\nCreating export directories...")
    create_export_directories(configs.get("export_config", {}))

    # For now, generate sample output
    print("\nGenerating sample analysis (demo mode)...")
    generate_sample_output(configs.get("export_config", {}))

    # Enhanced KPI analysis
    print("\nRunning enhanced KPI analysis...")
    enhanced_results = enhanced_kpi_analysis(configs)

    # Save enhanced results
    export_paths = configs.get("export_config", {}).get("export_paths", {})
    enhanced_path = (
        f"{export_paths.get('base_path', './abaco_runtime/exports')}/enhanced_kpis.json"
    )
    with open(enhanced_path, "w") as f:
        json.dump(enhanced_results, f, indent=2, default=str)

    print(f"Enhanced KPIs saved to: {enhanced_path}")

    # Comprehensive analysis with all features
    print("\nRunning comprehensive analytics...")
    comprehensive_results = comprehensive_analysis(configs)

    # Save comprehensive results
    comprehensive_path = f"{export_paths.get('base_path', './abaco_runtime/exports')}/comprehensive_analytics.json"
    with open(comprehensive_path, "w") as f:
        json.dump(comprehensive_results, f, indent=2, default=str)

    # Prepare Google Drive export
    drive_exporter = GoogleDriveExporter()
    export_files = drive_exporter.prepare_export_files(comprehensive_results)
    manifest_path = drive_exporter.generate_export_manifest(export_files)

    print(f"Comprehensive analytics saved to: {comprehensive_path}")
    print(
        f"✅ Found {comprehensive_results.get('reactivation_count', 0)} reactivated customers"
    )
    print(
        f"✅ Customer types: {comprehensive_results.get('customer_type_distribution', {})}"
    )
    print(f"📤 Export files ready for Google Drive: {len(export_files)} files")
    print(f"📋 Export manifest: {manifest_path}")
    print(
        f"🔗 Target folder: https://drive.google.com/drive/folders/1qIg_BnIf_IWYcWqCuvLaYU_Gu4C2-Dj8"
    )

    # Enhanced analysis with cohort and classification features
    print("\nRunning cohort and classification analysis...")
    enhanced_results = enhanced_analysis(configs)

    # Save enhanced results
    enhanced_path = f"{export_paths.get('base_path', './abaco_runtime/exports')}/cohort_analysis.json"
    with open(enhanced_path, "w") as f:
        json.dump(enhanced_results, f, indent=2, default=str)

    print(f"Cohort analysis saved to: {enhanced_path}")

    # Weighted metrics analysis
    print("\nRunning weighted metrics analysis...")
    # Use comprehensive_analysis to get weighted metrics as it already computes them
    weighted_results = comprehensive_analysis(configs).get("weighted_metrics", {})

    # Save weighted metrics results
    weighted_path = f"{export_paths.get('base_path', './abaco_runtime/exports')}/weighted_metrics.json"
    with open(weighted_path, "w") as f:
        json.dump(weighted_results, f, indent=2, default=str)

    print(f"Weighted metrics saved to: {weighted_path}")

    print("\n✅ Processing completed successfully!")
    print("\nNext steps:")
    print("1. Check the generated files in ./abaco_runtime/exports/")
    print("2. Customize the configuration files for your data")
    print("3. Implement actual data processing logic in this script")


if __name__ == "__main__":
    main()


"""
Portfolio processing module for Commercial-View
Handles the main portfolio processing logic for Abaco loan tape data
"""

import pandas as pd
from typing import Dict, Any, Optional, List
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def process_abaco_portfolio(
    loan_data: pd.DataFrame,
    payment_data: Optional[pd.DataFrame] = None,
    schedule_data: Optional[pd.DataFrame] = None,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process complete Abaco portfolio data with analytics.
    
    Args:
        loan_data: Loan data DataFrame
        payment_data: Payment history DataFrame (optional)
        schedule_data: Payment schedule DataFrame (optional)  
        config: Configuration parameters (optional)
        
    Returns:
        Dictionary containing processed results and analytics
    """
    config = config or {}
    results = {}
    
    # Process loan data
    if loan_data is not None and not loan_data.empty:
        loan_analytics = process_loan_analytics(loan_data, config)
        results['loan_analytics'] = loan_analytics
        logger.info(f"Processed {len(loan_data)} loan records")
    
    # Process payment data
    if payment_data is not None and not payment_data.empty:
        payment_analytics = process_payment_analytics(payment_data, config)
        results['payment_analytics'] = payment_analytics
        logger.info(f"Processed {len(payment_data)} payment records")
    
    # Process schedule data
    if schedule_data is not None and not schedule_data.empty:
        schedule_analytics = process_schedule_analytics(schedule_data, config)
        results['schedule_analytics'] = schedule_analytics
        logger.info(f"Processed {len(schedule_data)} schedule records")
    
    # Generate combined analytics
    results['portfolio_summary'] = generate_portfolio_summary(results)
    
    return results

def process_loan_analytics(df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
    """Process loan data with Abaco-specific analytics."""
    analytics = {
        'total_loans': len(df),
        'companies': df['Company'].value_counts().to_dict() if 'Company' in df.columns else {},
        'currency_distribution': df['Loan Currency'].value_counts().to_dict() if 'Loan Currency' in df.columns else {},
        'product_types': df['Product Type'].value_counts().to_dict() if 'Product Type' in df.columns else {},
        'loan_statuses': df['Loan Status'].value_counts().to_dict() if 'Loan Status' in df.columns else {}
    }
    
    # Financial metrics
    if 'Outstanding Loan Value' in df.columns:
        analytics['total_exposure'] = float(df['Outstanding Loan Value'].sum())
        analytics['avg_loan_size'] = float(df['Outstanding Loan Value'].mean())
    
    if 'Interest Rate APR' in df.columns:
        analytics['avg_interest_rate'] = float(df['Interest Rate APR'].mean())
        analytics['interest_rate_range'] = {
            'min': float(df['Interest Rate APR'].min()),
            'max': float(df['Interest Rate APR'].max())
        }
    
    # Delinquency analysis
    if 'Days in Default' in df.columns:
        analytics['delinquency_distribution'] = analyze_delinquency(df['Days in Default'])
    
    return analytics

def process_payment_analytics(df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
    """Process payment history with performance metrics."""
    analytics = {
        'total_payments': len(df),
        'payment_statuses': df['True Payment Status'].value_counts().to_dict() if 'True Payment Status' in df.columns else {}
    }
    
    if 'True Total Payment' in df.columns:
        analytics['total_payment_amount'] = float(df['True Total Payment'].sum())
        analytics['avg_payment_size'] = float(df['True Total Payment'].mean())
    
    if 'True Payment Status' in df.columns:
        # Calculate payment performance metrics
        total_payments = len(df)
        on_time_payments = len(df[df['True Payment Status'] == 'On Time'])
        analytics['on_time_rate'] = on_time_payments / total_payments if total_payments > 0 else 0
    
    return analytics

def process_schedule_analytics(df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
    """Process payment schedule data."""
    analytics = {
        'total_scheduled_payments': len(df)
    }
    
    if 'Total Payment' in df.columns:
        analytics['total_scheduled_amount'] = float(df['Total Payment'].sum())
        
    if 'Currency' in df.columns:
        analytics['currency_distribution'] = df['Currency'].value_counts().to_dict()
    
    return analytics

def analyze_delinquency(days_in_default: pd.Series) -> Dict[str, Any]:
    """Analyze delinquency distribution with Abaco buckets."""
    def get_bucket(days):
        if pd.isna(days) or days == 0:
            return 'current'
        elif 1 <= days <= 30:
            return 'early_delinquent'
        elif 31 <= days <= 60:
            return 'moderate_delinquent'
        elif 61 <= days <= 90:
            return 'late_delinquent'
        elif 91 <= days <= 120:
            return 'severe_delinquent'
        elif 121 <= days <= 180:
            return 'default'
        else:
            return 'npl'
    
    buckets = days_in_default.apply(get_bucket).value_counts()
    
    return {
        'buckets': buckets.to_dict(),
        'current_rate': buckets.get('current', 0) / len(days_in_default),
        'delinquent_rate': (len(days_in_default) - buckets.get('current', 0)) / len(days_in_default)
    }

def generate_portfolio_summary(results: Dict[str, Any]) -> Dict[str, Any]:
    """Generate overall portfolio summary."""
    summary = {
        'generation_timestamp': datetime.now().isoformat(),
        'data_sources': list(results.keys())
    }
    
    # Aggregate key metrics
    if 'loan_analytics' in results:
        loan_data = results['loan_analytics']
        summary.update({
            'total_loans': loan_data.get('total_loans', 0),
            'total_exposure': loan_data.get('total_exposure', 0),
            'primary_currency': 'USD',  # Based on Abaco data
            'primary_product': 'factoring'  # Based on Abaco data
        })
    
    if 'payment_analytics' in results:
        payment_data = results['payment_analytics']
        summary.update({
            'total_payments': payment_data.get('total_payments', 0),
            'on_time_rate': payment_data.get('on_time_rate', 0)
        })
    
    return summary

# Legacy compatibility functions
def process_loan_data(df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
    """Legacy function for backward compatibility."""
    return process_loan_analytics(df, config)

def process_payment_data(df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
    """Legacy function for backward compatibility."""
    return process_payment_analytics(df, config)
