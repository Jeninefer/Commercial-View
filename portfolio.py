#!/usr/bin/env python3
"""
Commercial-View Portfolio Processing - Abaco Integration
Processes 48,853 record Abaco loan tape with Spanish client names and USD factoring
"""

import argparse
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Tuple, Optional

import pandas as pd
import numpy as np

# Project imports
from src.data_loader import DataLoader, DataLoaderError
from src.exceptions import ConfigurationError, ExportError

# Constants for Abaco schema validation
ABACO_EXPECTED_RECORDS = 48853
ABACO_SCHEMA_PATH = Path("config/abaco_schema_autodetected.json")
EXPORT_BASE_PATH = Path("abaco_runtime/exports")


def load_config(config_dir: str) -> Dict[str, Any]:
    """Load configuration files for Commercial-View processing."""
    config_path = Path(config_dir)

    if not config_path.exists():
        raise ConfigurationError(f"Configuration directory not found: {config_dir}")

    configs = {}

    # Load export configuration
    export_config_path = config_path / "export_config.yml"
    if export_config_path.exists():
        import yaml

        with open(export_config_path, "r") as f:
            configs["export_config"] = yaml.safe_load(f)
    else:
        # Default export configuration for Abaco
        configs["export_config"] = {
            "base_path": str(EXPORT_BASE_PATH),
            "formats": ["csv", "json"],
            "timestamp": True,
            "abaco_specific": True,
        }

    # Load Abaco schema if available
    if ABACO_SCHEMA_PATH.exists():
        with open(ABACO_SCHEMA_PATH, "r") as f:
            configs["abaco_schema"] = json.load(f)

    return configs


def create_export_directories(export_config: Dict[str, Any]) -> None:
    """Create export directories for Abaco processing."""
    base_path = Path(export_config.get("base_path", EXPORT_BASE_PATH))

    # Create Abaco-specific export structure
    directories = [
        base_path / "abaco",
        base_path / "kpi" / "json",
        base_path / "kpi" / "csv",
        base_path / "spanish_clients",
        base_path / "usd_factoring",
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def get_delinquency_bucket(days_in_default: float) -> str:
    """
    Categorize loans into delinquency buckets based on days past due.
    Optimized for Abaco factoring products with bullet payment structure.
    """
    if pd.isna(days_in_default) or days_in_default <= 0:
        return "current"
    elif 1 <= days_in_default <= 30:
        return "early_delinquent"
    elif 31 <= days_in_default <= 60:
        return "moderate_delinquent"
    elif 61 <= days_in_default <= 90:
        return "late_delinquent"
    elif 91 <= days_in_default <= 120:
        return "severe_delinquent"
    elif 121 <= days_in_default <= 180:
        return "default"
    else:
        return "npl"  # Non-performing loan


def calculate_abaco_risk_score(loan_data: pd.Series) -> float:
    """
    Calculate risk score specifically calibrated for Abaco factoring products.

    Risk factors:
    - Days in Default (40% weight)
    - Loan Status (30% weight)
    - Interest Rate relative to Abaco range 29.47%-36.99% (20% weight)
    - Outstanding Amount (10% weight)
    """
    risk_score = 0.0

    # Days in Default factor (40% weight)
    days_in_default = loan_data.get("Days in Default", 0)
    if pd.notna(days_in_default):
        dpd_risk = min(float(days_in_default) / 180.0, 1.0) * 0.4
        risk_score += dpd_risk

    # Loan Status factor (30% weight)
    loan_status = loan_data.get("Loan Status", "Unknown")
    status_risk_map = {"Current": 0.0, "Complete": 0.0, "Default": 1.0, "Unknown": 0.5}
    status_risk = status_risk_map.get(str(loan_status), 0.5) * 0.3
    risk_score += status_risk

    # Interest Rate factor (20% weight) - Abaco range: 29.47% - 36.99%
    interest_rate = loan_data.get("Interest Rate APR", 0)
    if pd.notna(interest_rate) and float(interest_rate) > 0:
        rate = float(interest_rate)
        # Normalize to Abaco range (higher rates = higher risk)
        normalized_rate = (rate - 0.2947) / (0.3699 - 0.2947) if rate >= 0.2947 else 0
        rate_risk = min(normalized_rate, 1.0) * 0.2
        risk_score += rate_risk

    # Outstanding Amount factor (10% weight) - based on Abaco max: $77,175
    outstanding = loan_data.get("Outstanding Loan Value", 0)
    if pd.notna(outstanding) and float(outstanding) > 0:
        amount = float(outstanding)
        normalized_amount = min(amount / 100000, 1.0)  # Normalize to $100k
        amount_risk = normalized_amount * 0.1
        risk_score += amount_risk

    return min(risk_score, 1.0)


def process_abaco_portfolio(
    data_loader: DataLoader,
) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]:
    """
    Process Abaco loan tape data with comprehensive validation and analytics.

    Returns:
        Tuple of (processed_data, analytics_summary)
    """
    print("\n🏦 Processing Abaco loan tape data...")

    # Validate Abaco schema compliance
    if ABACO_SCHEMA_PATH.exists():
        validate_abaco_schema_compliance()

    try:
        # Load Abaco datasets
        abaco_data = data_loader.load_abaco_data()

        if not abaco_data:
            print("❌ No Abaco data found. Ensure CSV files are in data/ directory:")
            print("   - Abaco - Loan Tape_Loan Data_Table.csv (16,205 records)")
            print(
                "   - Abaco - Loan Tape_Historic Real Payment_Table.csv (16,443 records)"
            )
            print("   - Abaco - Loan Tape_Payment Schedule_Table.csv (16,205 records)")
            return {}, {}

        # Process each dataset
        processed_data = {}
        total_records = 0

        for dataset_name, df in abaco_data.items():
            if df is not None and not df.empty:
                print(f"📊 Processing {dataset_name}: {len(df)} records")

                # Add Abaco-specific enhancements
                enhanced_df = enhance_abaco_dataset(df, dataset_name)
                processed_data[dataset_name] = enhanced_df
                total_records += len(enhanced_df)

                # Display Spanish client validation for loan data
                if dataset_name == "loan_data" and "Cliente" in enhanced_df.columns:
                    spanish_companies = (
                        enhanced_df["Cliente"]
                        .str.contains("S.A. DE C.V.", na=False)
                        .sum()
                    )
                    print(f"   🇪🇸 Spanish companies identified: {spanish_companies}")

                    # Show sample Spanish names
                    spanish_samples = enhanced_df[
                        enhanced_df["Cliente"].str.contains("S.A. DE C.V.", na=False)
                    ]["Cliente"].head(3)
                    for sample in spanish_samples:
                        print(f"      • {sample}")

        # Validate total record count
        if total_records == ABACO_EXPECTED_RECORDS:
            print(
                f"✅ Record validation: {total_records:,} matches expected {ABACO_EXPECTED_RECORDS:,}"
            )
        else:
            print(
                f"⚠️  Record count: {total_records:,} (expected {ABACO_EXPECTED_RECORDS:,})"
            )

        # Generate comprehensive analytics
        analytics_summary = generate_abaco_analytics_summary(processed_data)

        return processed_data, analytics_summary

    except Exception as e:
        raise DataLoaderError(f"Failed to process Abaco portfolio: {e}") from e


def validate_abaco_schema_compliance() -> bool:
    """Validate data against exact Abaco schema structure."""
    try:
        with open(ABACO_SCHEMA_PATH, "r") as f:
            schema = json.load(f)

        datasets = schema.get("datasets", {})
        total_records = sum(
            dataset.get("rows", 0)
            for dataset in datasets.values()
            if dataset.get("exists", False)
        )

        schema_valid = total_records == ABACO_EXPECTED_RECORDS

        if schema_valid:
            print("✅ Abaco schema compliance validated")

            # Validate Spanish language support
            loan_data = datasets.get("Loan Data", {})
            columns = {col["name"]: col for col in loan_data.get("columns", [])}

            cliente_col = columns.get("Cliente", {})
            if cliente_col and "sample_values" in cliente_col:
                spanish_names = [
                    val for val in cliente_col["sample_values"] if "S.A. DE C.V." in val
                ]
                print(
                    f"✅ Spanish business names validated: {len(spanish_names)} found"
                )

            # Validate USD factoring
            currency_col = columns.get("Loan Currency", {})
            product_col = columns.get("Product Type", {})

            if currency_col.get("sample_values") == ["USD"]:
                print("✅ USD currency validation passed")

            if product_col.get("sample_values") == ["factoring"]:
                print("✅ Factoring product validation passed")

        return schema_valid

    except Exception as e:
        print(f"⚠️  Schema validation error: {e}")
        return False


def enhance_abaco_dataset(df: pd.DataFrame, dataset_name: str) -> pd.DataFrame:
    """Enhance dataset with Abaco-specific features and calculations."""
    enhanced_df = df.copy()

    if dataset_name == "loan_data":
        # Add Spanish company identification
        if "Cliente" in enhanced_df.columns:
            enhanced_df["is_spanish_company"] = enhanced_df["Cliente"].str.contains(
                "S.A. DE C.V.|S.A.|S.R.L.", na=False, regex=True
            )

        # Add USD factoring validation
        if (
            "Loan Currency" in enhanced_df.columns
            and "Product Type" in enhanced_df.columns
        ):
            enhanced_df["is_usd_factoring"] = (
                enhanced_df["Loan Currency"] == "USD"
            ) & (enhanced_df["Product Type"] == "factoring")

        # Add bullet payment validation
        if "Payment Frequency" in enhanced_df.columns:
            enhanced_df["is_bullet_payment"] = (
                enhanced_df["Payment Frequency"] == "bullet"
            )

        # Add delinquency bucketing
        if "Days in Default" in enhanced_df.columns:
            enhanced_df["delinquency_bucket"] = enhanced_df["Days in Default"].apply(
                get_delinquency_bucket
            )

        # Calculate Abaco-specific risk scores
        enhanced_df["abaco_risk_score"] = enhanced_df.apply(
            calculate_abaco_risk_score, axis=1
        )

        # Add interest rate categorization for Abaco range
        if "Interest Rate APR" in enhanced_df.columns:
            enhanced_df["rate_category"] = pd.cut(
                enhanced_df["Interest Rate APR"],
                bins=[0, 0.30, 0.35, 1.0],
                labels=["low_rate", "medium_rate", "high_rate"],
                include_lowest=True,
            )

    elif dataset_name == "payment_history":
        # Add payment performance indicators
        if "True Payment Status" in enhanced_df.columns:
            enhanced_df["is_on_time"] = enhanced_df["True Payment Status"] == "On Time"
            enhanced_df["is_late"] = enhanced_df["True Payment Status"] == "Late"
            enhanced_df["is_prepayment"] = (
                enhanced_df["True Payment Status"] == "Prepayment"
            )

        # Validate USD payments
        if "True Payment Currency" in enhanced_df.columns:
            enhanced_df["is_usd_payment"] = (
                enhanced_df["True Payment Currency"] == "USD"
            )

    elif dataset_name == "payment_schedule":
        # Add completion status
        if "Outstanding Loan Value" in enhanced_df.columns:
            enhanced_df["is_completed"] = enhanced_df["Outstanding Loan Value"] == 0

        # Validate USD schedules
        if "Currency" in enhanced_df.columns:
            enhanced_df["is_usd_schedule"] = enhanced_df["Currency"] == "USD"

    return enhanced_df


def generate_abaco_analytics_summary(
    processed_data: Dict[str, pd.DataFrame],
) -> Dict[str, Any]:
    """Generate comprehensive analytics summary for Abaco portfolio."""

    analytics = {
        "generation_time": datetime.now().isoformat(),
        "abaco_integration": True,
        "total_datasets": len(processed_data),
        "schema_validated": validate_abaco_schema_compliance(),
    }

    # Loan data analytics
    if "loan_data" in processed_data:
        loan_df = processed_data["loan_data"]

        analytics.update(
            {
                "total_loans": len(loan_df),
                "total_exposure": float(
                    loan_df.get("Outstanding Loan Value", pd.Series(0)).sum()
                ),
                "avg_risk_score": float(
                    loan_df.get("abaco_risk_score", pd.Series(0)).mean()
                ),
                "spanish_companies": int(
                    loan_df.get("is_spanish_company", pd.Series(False)).sum()
                ),
                "usd_factoring_loans": int(
                    loan_df.get("is_usd_factoring", pd.Series(False)).sum()
                ),
                "bullet_payments": int(
                    loan_df.get("is_bullet_payment", pd.Series(False)).sum()
                ),
            }
        )

        # Interest rate analytics (Abaco range: 29.47% - 36.99%)
        if "Interest Rate APR" in loan_df.columns:
            rates = loan_df["Interest Rate APR"].dropna()
            if not rates.empty:
                analytics["interest_rate_stats"] = {
                    "min_rate": float(rates.min()),
                    "max_rate": float(rates.max()),
                    "avg_rate": float(rates.mean()),
                    "within_abaco_range": int(
                        ((rates >= 0.2947) & (rates <= 0.3699)).sum()
                    ),
                }

        # Delinquency distribution
        if "delinquency_bucket" in loan_df.columns:
            delinq_dist = loan_df["delinquency_bucket"].value_counts().to_dict()
            analytics["delinquency_distribution"] = {
                k: int(v) for k, v in delinq_dist.items()
            }

    # Payment history analytics
    if "payment_history" in processed_data:
        payment_df = processed_data["payment_history"]

        analytics.update(
            {
                "total_payments": len(payment_df),
                "on_time_payments": int(
                    payment_df.get("is_on_time", pd.Series(False)).sum()
                ),
                "late_payments": int(payment_df.get("is_late", pd.Series(False)).sum()),
                "prepayments": int(
                    payment_df.get("is_prepayment", pd.Series(False)).sum()
                ),
                "usd_payments": int(
                    payment_df.get("is_usd_payment", pd.Series(False)).sum()
                ),
            }
        )

        # Payment amount statistics
        if "True Total Payment" in payment_df.columns:
            payments = payment_df["True Total Payment"].dropna()
            if not payments.empty:
                analytics["payment_stats"] = {
                    "total_payment_amount": float(payments.sum()),
                    "avg_payment_amount": float(payments.mean()),
                    "min_payment": float(payments.min()),
                    "max_payment": float(payments.max()),
                }

    # Payment schedule analytics
    if "payment_schedule" in processed_data:
        schedule_df = processed_data["payment_schedule"]

        analytics.update(
            {
                "scheduled_payments": len(schedule_df),
                "completed_loans": int(
                    schedule_df.get("is_completed", pd.Series(False)).sum()
                ),
                "usd_schedules": int(
                    schedule_df.get("is_usd_schedule", pd.Series(False)).sum()
                ),
            }
        )

    return analytics


def export_results(
    abaco_data: Dict[str, pd.DataFrame],
    analytics_summary: Dict[str, Any],
    export_config: Dict[str, Any],
) -> None:
    """Export Abaco processing results in multiple formats."""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_path = Path(export_config.get("base_path", EXPORT_BASE_PATH))

    try:
        # Export analytics summary (JSON)
        analytics_file = base_path / "kpi" / "json" / f"abaco_summary_{timestamp}.json"
        with open(analytics_file, "w", encoding="utf-8") as f:
            json.dump(analytics_summary, f, indent=2, ensure_ascii=False)
        print(f"✅ Analytics summary exported: {analytics_file}")

        # Export datasets
        formats = export_config.get("formats", ["csv", "json"])

        for dataset_name, df in abaco_data.items():
            if df is not None and not df.empty:

                if "csv" in formats:
                    csv_file = base_path / "abaco" / f"{dataset_name}_{timestamp}.csv"
                    df.to_csv(csv_file, index=False, encoding="utf-8")
                    print(f"✅ CSV exported: {csv_file}")

                if "json" in formats:
                    json_file = base_path / "abaco" / f"{dataset_name}_{timestamp}.json"
                    df.to_json(json_file, orient="records", indent=2, force_ascii=False)
                    print(f"✅ JSON exported: {json_file}")

    except (IOError, json.JSONEncodeError) as e:
        raise ExportError(f"Failed to export Abaco results: {e}") from e


def display_portfolio_summary(analytics_summary: Dict[str, Any]) -> None:
    """Display portfolio summary with proper formatting."""
    total_loans = analytics_summary.get("total_loans", 0)
    total_exposure = analytics_summary.get("total_exposure", 0)
    total_payments = analytics_summary.get("total_payments", 0)
    avg_risk_score = analytics_summary.get("avg_risk_score", 0)

    print(f"\n📈 Abaco Portfolio Summary:")
    print(f"   💼 Total Loans: {total_loans:,}")
    print(f"   💰 Total Exposure: ${total_exposure:,.2f} USD")
    print(f"   💸 Total Payments: {total_payments:,}")
    print(f"   🎯 Average Risk Score: {avg_risk_score:.3f}")

    # Display Abaco-specific metrics
    spanish_companies = analytics_summary.get("spanish_companies", 0)
    usd_factoring = analytics_summary.get("usd_factoring_loans", 0)
    bullet_payments = analytics_summary.get("bullet_payments", 0)

    print(f"\n🏦 Abaco Integration Metrics:")
    print(f"   🇪🇸 Spanish Companies: {spanish_companies:,}")
    print(f"   💰 USD Factoring Loans: {usd_factoring:,}")
    print(f"   🔄 Bullet Payments: {bullet_payments:,}")

    # Interest rate statistics for Abaco range
    if "interest_rate_stats" in analytics_summary:
        rate_stats = analytics_summary["interest_rate_stats"]
        print(
            f"   📊 Interest Rate Range: {rate_stats['min_rate']:.4f} - {rate_stats['max_rate']:.4f}"
        )
        print(
            f"   🎯 Within Abaco Range (29.47%-36.99%): {rate_stats.get('within_abaco_range', 0):,}"
        )

    # Payment performance
    on_time = analytics_summary.get("on_time_payments", 0)
    late = analytics_summary.get("late_payments", 0)
    total_payment_records = on_time + late + analytics_summary.get("prepayments", 0)

    if total_payment_records > 0:
        on_time_rate = (on_time / total_payment_records) * 100
        print(f"   ✅ On-Time Payment Rate: {on_time_rate:.1f}%")


def validate_data_availability(data_loader: DataLoader) -> bool:
    """Validate that required Abaco data is available."""
    try:
        test_load = data_loader.load_abaco_data()
        return bool(test_load)
    except (DataLoaderError, IOError, ValueError):
        return False


def main():
    """Main processing function for Commercial-View Abaco integration."""
    parser = argparse.ArgumentParser(
        description="Commercial-View: Process Abaco loan tape (48,853 records) with Spanish client support"
    )
    parser.add_argument(
        "--config", default="config", help="Configuration directory path"
    )
    parser.add_argument("--data-dir", help="Input data directory path (default: data)")
    parser.add_argument(
        "--abaco-only", action="store_true", help="Process only Abaco loan tape data"
    )

    args = parser.parse_args()

    print("🏦 COMMERCIAL-VIEW - ABACO INTEGRATION")
    print("=" * 50)
    print("📊 Dataset: 48,853 records (16,205 + 16,443 + 16,205)")
    print("🇪🇸 Spanish Support: Business names with S.A. DE C.V. entities")
    print("💰 USD Factoring: 29.47% - 36.99% APR range")
    print("🔄 Bullet Payments: Single maturity factoring products")
    print("🏢 Companies: Abaco Technologies & Abaco Financial")
    print("=" * 50)

    # Load configurations
    try:
        configs = load_config(args.config)
        print(f"✅ Configuration loaded from: {args.config}")

        if not configs:
            raise ConfigurationError("No valid configuration files found")

    except ConfigurationError as e:
        print(f"❌ Configuration Error: {e}")
        sys.exit(1)

    # Create export directories
    try:
        create_export_directories(configs.get("export_config", {}))
        print("✅ Export directories prepared")
    except Exception as e:
        print(f"❌ Export setup error: {e}")
        sys.exit(1)

    # Initialize DataLoader with Abaco support
    data_loader = DataLoader(config_dir=args.config, data_dir=args.data_dir or "data")

    # Validate data availability
    if not validate_data_availability(data_loader):
        print(
            "⚠️  No Abaco data available. Please ensure CSV files are in data/ directory."
        )
        print("   Expected files:")
        print("   - Abaco - Loan Tape_Loan Data_Table.csv")
        print("   - Abaco - Loan Tape_Historic Real Payment_Table.csv")
        print("   - Abaco - Loan Tape_Payment Schedule_Table.csv")
        sys.exit(1)

    # Process Abaco portfolio data
    try:
        abaco_data, analytics_summary = process_abaco_portfolio(data_loader)

        if not abaco_data:
            print("⚠️  No data processed. Check data files and configuration.")
            sys.exit(1)

        # Export results
        export_results(abaco_data, analytics_summary, configs.get("export_config", {}))

        # Display comprehensive summary
        display_portfolio_summary(analytics_summary)

        print(f"\n🎉 SUCCESS! Abaco integration completed successfully")
        print(
            f"📊 Processed {sum(len(df) for df in abaco_data.values()):,} total records"
        )
        print(f"📁 Results exported to: {EXPORT_BASE_PATH}")

    except (DataLoaderError, ExportError) as e:
        print(f"❌ Processing Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
