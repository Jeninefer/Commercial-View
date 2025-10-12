"""
Abaco Core module extracted from PRs #26-30
Core utilities for commercial view analysis with robust error handling
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class AbacoCore:
    """Core utilities for commercial lending analysis"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {
            "date_format": "%Y-%m-%d",
            "currency_precision": 2,
            "validation_rules": {"min_loan_amount": 1000, "max_loan_amount": 1000000},
        }
        self.snapshots: List[Dict[str, Any]] = []
        logger.info("Abaco Core initialized successfully")

    def standardize_data_formats(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize date and numeric formats across datasets"""
        if df.empty:
            logger.warning("Empty DataFrame provided for standardization")
            return df

        result_df = df.copy()

        # Date standardization with error handling
        date_columns = [
            "disbursement_date",
            "payment_date",
            "maturity_date",
            "last_active_date",
        ]
        for col in date_columns:
            if col in result_df.columns:
                try:
                    result_df[col] = pd.to_datetime(result_df[col], errors="coerce")
                    logger.debug(f"Standardized date column: {col}")
                except Exception as e:
                    logger.error(f"Error standardizing date column {col}: {e}")

        # Numeric standardization with validation
        numeric_columns = ["loan_amount", "outstanding_balance", "apr", "days_past_due"]
        for col in numeric_columns:
            if col in result_df.columns:
                try:
                    result_df[col] = pd.to_numeric(result_df[col], errors="coerce")
                    # Apply validation rules
                    if col == "loan_amount":
                        min_amount = self.config["validation_rules"]["min_loan_amount"]
                        max_amount = self.config["validation_rules"]["max_loan_amount"]
                        invalid_amounts = (
                            (result_df[col] < min_amount)
                            | (result_df[col] > max_amount)
                        ).sum()
                        if invalid_amounts > 0:
                            logger.warning(
                                f"Found {invalid_amounts} invalid loan amounts"
                            )
                except Exception as e:
                    logger.error(f"Error standardizing numeric column {col}: {e}")

        logger.info(f"Data standardization completed for {len(result_df)} records")
        return result_df

    def validate_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Comprehensive data quality validation with detailed metrics"""
        quality_report = {
            "total_records": len(df),
            "missing_data": {},
            "duplicate_records": 0,
            "data_types": {},
            "quality_score": 0.0,
            "recommendations": [],
        }

        if df.empty:
            quality_report["quality_score"] = 0.0
            quality_report["recommendations"].append("Dataset is empty")
            return quality_report

        try:
            # Missing data analysis
            missing_data = df.isnull().sum()
            quality_report["missing_data"] = missing_data.to_dict()

            # Duplicate analysis
            quality_report["duplicate_records"] = int(df.duplicated().sum())

            # Data types
            quality_report["data_types"] = {
                col: str(dtype) for col, dtype in df.dtypes.items()
            }

            # Calculate quality score (0-100)
            total_cells = len(df) * len(df.columns)
            missing_cells = missing_data.sum()
            duplicate_penalty = quality_report["duplicate_records"] * len(df.columns)

            quality_score = max(
                0, 100 - ((missing_cells + duplicate_penalty) / total_cells * 100)
            )
            quality_report["quality_score"] = round(quality_score, 2)

            # Generate recommendations
            if missing_cells > 0:
                quality_report["recommendations"].append(
                    f"Address {missing_cells} missing values"
                )
            if quality_report["duplicate_records"] > 0:
                quality_report["recommendations"].append(
                    f"Remove {quality_report['duplicate_records']} duplicate records"
                )
            if quality_score < 80:
                quality_report["recommendations"].append(
                    "Data quality below 80% - review data sources"
                )

            logger.info(f"Data quality validation completed. Score: {quality_score}%")

        except Exception as e:
            logger.error(f"Error during data quality validation: {e}")
            quality_report["recommendations"].append("Data quality validation failed")

        return quality_report

    def create_data_snapshot(
        self, df: pd.DataFrame, snapshot_name: str
    ) -> Dict[str, Any]:
        """Create a data snapshot for audit trail"""
        snapshot = {
            "snapshot_name": snapshot_name,
            "timestamp": datetime.now().isoformat(),
            "record_count": len(df),
            "columns": list(df.columns),
            "summary_stats": {},
        }

        # Generate summary statistics for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            snapshot["summary_stats"][col] = {
                "mean": float(df[col].mean()) if not df[col].empty else 0.0,
                "median": float(df[col].median()) if not df[col].empty else 0.0,
                "std": float(df[col].std()) if not df[col].empty else 0.0,
            }

        logger.info(f"Data snapshot '{snapshot_name}' created")
        self.snapshots.append(snapshot)  # Store snapshot in history
        return snapshot

    def export_quality_report(
        self, quality_report: Dict[str, Any], output_path: Optional[Path] = None
    ) -> str:
        """
        Export data quality report to JSON file

        Args:
            quality_report: Quality report dictionary
            output_path: Optional output file path

        Returns:
            Path to exported file
        """
        import json

        if output_path is None:
            output_path = Path("data_quality_report.json")

        try:
            with open(output_path, "w") as f:
                json.dump(quality_report, f, indent=2, default=str)

            logger.info(f"Quality report exported to {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to export quality report: {e}")
            raise

    def get_snapshot_history(self) -> List[Dict[str, Any]]:
        """
        Retrieve snapshot history

        Returns:
            List of all created snapshots
        """
        return self.snapshots.copy()

    def compare_snapshots(
        self, snapshot1_name: str, snapshot2_name: str
    ) -> Dict[str, Any]:
        """
        Compare two data snapshots

        Args:
            snapshot1_name: Name of first snapshot
            snapshot2_name: Name of second snapshot

        Returns:
            Comparison report dictionary
        """
        snapshot1 = next(
            (s for s in self.snapshots if s["snapshot_name"] == snapshot1_name), None
        )
        snapshot2 = next(
            (s for s in self.snapshots if s["snapshot_name"] == snapshot2_name), None
        )

        if not snapshot1 or not snapshot2:
            logger.error("One or both snapshots not found")
            return {"error": "Snapshots not found"}

        comparison = {
            "snapshot1": snapshot1_name,
            "snapshot2": snapshot2_name,
            "record_count_change": snapshot2["record_count"] - snapshot1["record_count"],
            "column_changes": {
                "added": list(set(snapshot2["columns"]) - set(snapshot1["columns"])),
                "removed": list(set(snapshot1["columns"]) - set(snapshot2["columns"])),
            },
            "timestamp_comparison": {
                "snapshot1_time": snapshot1["timestamp"],
                "snapshot2_time": snapshot2["timestamp"],
            },
        }

        logger.info(f"Snapshot comparison completed: {snapshot1_name} vs {snapshot2_name}")
        return comparison

    def validate_loan_portfolio(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Validate commercial loan portfolio data

        Args:
            df: Portfolio DataFrame

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues: List[str] = []

        # Check required columns
        required_columns = ["loan_id", "loan_amount", "disbursement_date"]
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            issues.append(f"Missing required columns: {', '.join(missing_columns)}")

        # Check for negative loan amounts
        if "loan_amount" in df.columns:
            negative_amounts = (df["loan_amount"] < 0).sum()
            if negative_amounts > 0:
                issues.append(f"Found {negative_amounts} loans with negative amounts")

        # Check for duplicate loan IDs
        if "loan_id" in df.columns:
            duplicates = df["loan_id"].duplicated().sum()
            if duplicates > 0:
                issues.append(f"Found {duplicates} duplicate loan IDs")

        # Check for future disbursement dates
        if "disbursement_date" in df.columns:
            df["disbursement_date"] = pd.to_datetime(df["disbursement_date"], errors="coerce")
            future_dates = (df["disbursement_date"] > pd.Timestamp.now()).sum()
            if future_dates > 0:
                issues.append(f"Found {future_dates} loans with future disbursement dates")

        is_valid = len(issues) == 0

        if is_valid:
            logger.info("Portfolio validation passed")
        else:
            logger.warning(f"Portfolio validation failed with {len(issues)} issues")

        return is_valid, issues

    def calculate_portfolio_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate comprehensive portfolio metrics

        Args:
            df: Portfolio DataFrame

        Returns:
            Dictionary with portfolio metrics
        """
        metrics: Dict[str, Any] = {
            "total_loans": len(df),
            "total_loan_value": 0.0,
            "avg_loan_amount": 0.0,
            "portfolio_balance": 0.0,
            "delinquency_rate": 0.0,
            "calculated_at": datetime.now().isoformat(),
        }

        try:
            if "loan_amount" in df.columns:
                metrics["total_loan_value"] = float(df["loan_amount"].sum())
                metrics["avg_loan_amount"] = float(df["loan_amount"].mean())

            if "outstanding_balance" in df.columns:
                metrics["portfolio_balance"] = float(df["outstanding_balance"].sum())

            if "days_past_due" in df.columns:
                delinquent_loans = (df["days_past_due"] > 30).sum()
                metrics["delinquency_rate"] = (
                    delinquent_loans / len(df) * 100
                    if len(df) > 0
                    else 0.0
                )

            logger.info("Portfolio metrics calculated successfully")

        except Exception as e:
            logger.error(f"Error calculating portfolio metrics: {e}")

        return metrics

    def __repr__(self) -> str:
        """Return string representation of AbacoCore instance"""
        return (
            "AbacoCore("
            f"config={self.config}, "
            f"snapshots_count={len(self.snapshots)}"
            ")"
        )
