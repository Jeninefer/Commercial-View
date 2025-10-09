"""
Enterprise-grade production data manager for Commercial-View
Ensures only real commercial lending data is processed with market-leading quality
"""

import os
import pandas as pd
import gdown
import hashlib
import json
from pathlib import Path
from typing import Dict, Optional, List, Tuple, Any
from datetime import datetime, timezone
import logging
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class DataQualityLevel(Enum):
    """Data quality assessment levels"""

    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    CRITICAL = "critical"


@dataclass
class DataQualityMetrics:
    """Comprehensive data quality metrics for commercial lending"""

    completeness_score: float  # Percentage of non-null values
    consistency_score: float  # Data format consistency
    accuracy_score: float  # Business rule compliance
    timeliness_score: float  # Data freshness
    validity_score: float  # Schema compliance
    overall_quality: DataQualityLevel
    issues_identified: List[str]
    recommendations: List[str]


class ProductionDataManager:
    """
    Enterprise-grade production data manager
    Ensures robust, secure, and validated real data processing
    """

    def __init__(self):
        self.drive_folder_url = (
            "https://drive.google.com/drive/folders/1qIg_BnIf_IWYcWqCuvLaYU_Gu4C2-Dj8"
        )
        self.data_directory = Path("data/production")
        self.metadata_directory = Path("data/metadata")
        self.backup_directory = Path("data/backups")

        # Create directory structure
        for directory in [
            self.data_directory,
            self.metadata_directory,
            self.backup_directory,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

        # Production CSV file mapping (real data sources)
        self.production_files = {
            "loan_portfolio": {
                "filename": "loan_data.csv",
                "required_columns": [
                    "loan_id",
                    "customer_id",
                    "principal_amount",
                    "interest_rate",
                    "origination_date",
                    "maturity_date",
                    "loan_status",
                    "industry_code",
                ],
                "business_rules": self._get_loan_validation_rules(),
                "critical": True,
            },
            "payment_schedule": {
                "filename": "payment_schedule.csv",
                "required_columns": [
                    "payment_id",
                    "loan_id",
                    "due_date",
                    "principal_amount",
                    "interest_amount",
                    "total_amount",
                    "payment_status",
                ],
                "business_rules": self._get_payment_validation_rules(),
                "critical": True,
            },
            "historic_payments": {
                "filename": "historic_real_payment.csv",
                "required_columns": [
                    "loan_id",
                    "payment_date",
                    "amount_paid",
                    "days_past_due",
                    "payment_method",
                    "collection_status",
                ],
                "business_rules": self._get_historic_payment_rules(),
                "critical": True,
            },
            "customer_master": {
                "filename": "customer_data.csv",
                "required_columns": [
                    "customer_id",
                    "customer_name",
                    "credit_score",
                    "industry_code",
                    "registration_date",
                    "risk_grade",
                    "total_exposure",
                ],
                "business_rules": self._get_customer_validation_rules(),
                "critical": True,
            },
            "collateral_register": {
                "filename": "collateral_data.csv",
                "required_columns": [
                    "collateral_id",
                    "loan_id",
                    "collateral_type",
                    "estimated_value",
                    "appraisal_date",
                    "lien_position",
                ],
                "business_rules": self._get_collateral_validation_rules(),
                "critical": False,
            },
        }

    def synchronize_production_data(
        self, force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Synchronize production data with enterprise-grade validation
        Returns comprehensive sync results with quality metrics
        """
        sync_results = {
            "sync_timestamp": datetime.now(timezone.utc).isoformat(),
            "sync_triggered_by": "automated" if not force_refresh else "manual",
            "files_processed": {},
            "quality_assessment": {},
            "business_validation": {},
            "sync_successful": False,
            "critical_issues": [],
            "recommendations": [],
        }

        try:
            # Create backup of existing data
            if self._has_existing_data():
                self._create_data_backup()

            # Download fresh production data
            download_status = self._download_production_files()

            if not download_status["success"]:
                sync_results["critical_issues"].append(
                    "Failed to download production data"
                )
                return sync_results

            # Process each production file with comprehensive validation
            all_files_valid = True

            for dataset_key, file_config in self.production_files.items():
                file_path = self.data_directory / file_config["filename"]

                if not file_path.exists():
                    sync_results["critical_issues"].append(
                        f"Missing critical file: {file_config['filename']}"
                    )
                    if file_config["critical"]:
                        all_files_valid = False
                    continue

                # Load and validate dataset
                validation_results = self._validate_production_dataset(
                    file_path, file_config
                )
                sync_results["files_processed"][dataset_key] = validation_results

                # Assess data quality
                quality_metrics = self._assess_data_quality(file_path, file_config)
                sync_results["quality_assessment"][dataset_key] = asdict(
                    quality_metrics
                )

                # Business rule validation
                business_validation = self._validate_business_rules(
                    file_path, file_config
                )
                sync_results["business_validation"][dataset_key] = business_validation

                # Check for critical quality issues
                if quality_metrics.overall_quality in [
                    DataQualityLevel.POOR,
                    DataQualityLevel.CRITICAL,
                ]:
                    sync_results["critical_issues"].extend(
                        quality_metrics.issues_identified
                    )
                    if file_config["critical"]:
                        all_files_valid = False

            # Generate comprehensive metadata
            self._generate_data_metadata(sync_results)

            sync_results["sync_successful"] = (
                all_files_valid and len(sync_results["critical_issues"]) == 0
            )

            if sync_results["sync_successful"]:
                logger.info("✅ Production data synchronization completed successfully")
            else:
                logger.error(
                    "❌ Production data synchronization failed with critical issues"
                )

        except Exception as e:
            logger.error(f"❌ Critical error during data synchronization: {e}")
            sync_results["critical_issues"].append(f"Synchronization error: {str(e)}")

        return sync_results

    def _validate_production_dataset(
        self, file_path: Path, config: Dict
    ) -> Dict[str, Any]:
        """Comprehensive dataset validation with commercial lending specifics"""
        validation_results = {
            "file_size_mb": file_path.stat().st_size / (1024 * 1024),
            "row_count": 0,
            "column_count": 0,
            "schema_compliance": False,
            "data_types_valid": False,
            "missing_columns": [],
            "extra_columns": [],
            "null_percentage": {},
            "duplicate_records": 0,
            "validation_passed": False,
        }

        try:
            # Load dataset
            df = pd.read_csv(file_path)
            validation_results["row_count"] = len(df)
            validation_results["column_count"] = len(df.columns)

            # Schema validation
            required_columns = set(config["required_columns"])
            actual_columns = set(df.columns)

            validation_results["missing_columns"] = list(
                required_columns - actual_columns
            )
            validation_results["extra_columns"] = list(
                actual_columns - required_columns
            )
            validation_results["schema_compliance"] = (
                len(validation_results["missing_columns"]) == 0
            )

            # Data quality checks
            validation_results["null_percentage"] = (
                df.isnull().sum() / len(df) * 100
            ).to_dict()
            validation_results["duplicate_records"] = df.duplicated().sum()

            # Commercial lending specific validations
            if "loan_id" in df.columns:
                validation_results["unique_loan_ids"] = df["loan_id"].nunique() == len(
                    df
                )

            if "customer_id" in df.columns:
                validation_results["customer_id_format_valid"] = (
                    df["customer_id"].notna().all()
                )

            validation_results["validation_passed"] = (
                validation_results["schema_compliance"]
                and validation_results["duplicate_records"] == 0
                and validation_results["row_count"] > 0
            )

        except Exception as e:
            logger.error(f"Dataset validation failed for {file_path}: {e}")
            validation_results["validation_error"] = str(e)

        return validation_results

    def _assess_data_quality(self, file_path: Path, config: Dict) -> DataQualityMetrics:
        """Comprehensive data quality assessment for commercial lending"""
        try:
            df = pd.read_csv(file_path)
            issues = []
            recommendations = []

            # Completeness Score (0-100)
            completeness = (
                1 - df.isnull().sum().sum() / (len(df) * len(df.columns))
            ) * 100

            # Consistency Score - Check data format consistency
            consistency = 100.0  # Start with perfect score

            # Check date format consistency
            date_columns = [col for col in df.columns if "date" in col.lower()]
            for col in date_columns:
                try:
                    pd.to_datetime(df[col].dropna())
                except:
                    consistency -= 10
                    issues.append(f"Inconsistent date format in {col}")

            # Accuracy Score - Business rule compliance
            accuracy = self._calculate_accuracy_score(df, config)

            # Timeliness Score - Data freshness
            timeliness = self._calculate_timeliness_score(df)

            # Validity Score - Schema and constraint compliance
            validity = 100.0
            if df.duplicated().any():
                validity -= 20
                issues.append("Duplicate records found")

            # Overall quality determination
            overall_score = (
                completeness + consistency + accuracy + timeliness + validity
            ) / 5

            if overall_score >= 95:
                overall_quality = DataQualityLevel.EXCELLENT
            elif overall_score >= 85:
                overall_quality = DataQualityLevel.GOOD
            elif overall_score >= 70:
                overall_quality = DataQualityLevel.ACCEPTABLE
            elif overall_score >= 50:
                overall_quality = DataQualityLevel.POOR
            else:
                overall_quality = DataQualityLevel.CRITICAL

            # Generate recommendations
            if completeness < 95:
                recommendations.append(
                    "Improve data completeness by addressing missing values"
                )
            if accuracy < 90:
                recommendations.append(
                    "Review business rule compliance and data validation"
                )
            if timeliness < 85:
                recommendations.append("Implement more frequent data updates")

            return DataQualityMetrics(
                completeness_score=completeness,
                consistency_score=consistency,
                accuracy_score=accuracy,
                timeliness_score=timeliness,
                validity_score=validity,
                overall_quality=overall_quality,
                issues_identified=issues,
                recommendations=recommendations,
            )

        except Exception as e:
            logger.error(f"Quality assessment failed: {e}")
            return DataQualityMetrics(
                completeness_score=0.0,
                consistency_score=0.0,
                accuracy_score=0.0,
                timeliness_score=0.0,
                validity_score=0.0,
                overall_quality=DataQualityLevel.CRITICAL,
                issues_identified=[f"Quality assessment error: {str(e)}"],
                recommendations=["Fix data loading issues before quality assessment"],
            )

    def _get_loan_validation_rules(self) -> Dict[str, Any]:
        """Commercial lending specific validation rules for loan data"""
        return {
            "principal_amount": {"min": 1000, "max": 50000000},
            "interest_rate": {"min": 0.01, "max": 0.50},
            "loan_status": {
                "allowed_values": ["active", "paid_off", "charged_off", "delinquent"]
            },
            "industry_code": {"pattern": r"^\d{6}$"},  # NAICS format
        }

    def _get_payment_validation_rules(self) -> Dict[str, Any]:
        """Payment schedule validation rules"""
        return {
            "principal_amount": {"min": 0},
            "interest_amount": {"min": 0},
            "total_amount": {"min": 0},
            "payment_status": {
                "allowed_values": ["pending", "paid", "overdue", "partial"]
            },
        }

    def _get_historic_payment_rules(self) -> Dict[str, Any]:
        """Historic payment validation rules"""
        return {
            "amount_paid": {"min": 0},
            "days_past_due": {"min": 0, "max": 2000},
            "payment_method": {
                "allowed_values": ["ach", "wire", "check", "online", "cash"]
            },
        }

    def _get_customer_validation_rules(self) -> Dict[str, Any]:
        """Customer data validation rules"""
        return {
            "credit_score": {"min": 300, "max": 850},
            "risk_grade": {"allowed_values": ["A", "B", "C", "D", "E"]},
            "total_exposure": {"min": 0},
        }

    def _get_collateral_validation_rules(self) -> Dict[str, Any]:
        """Collateral data validation rules"""
        return {
            "estimated_value": {"min": 0},
            "collateral_type": {
                "allowed_values": [
                    "real_estate",
                    "equipment",
                    "inventory",
                    "receivables",
                    "cash",
                ]
            },
            "lien_position": {
                "allowed_values": ["first", "second", "third", "subordinate"]
            },
        }
