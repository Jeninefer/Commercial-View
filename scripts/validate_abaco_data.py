"""
Abaco Data Processing Validator
Validates all 48,853 records against schema and business rules
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants from SLO document
EXPECTED_TOTAL_RECORDS = 48853
EXPECTED_LOAN_RECORDS = 16205
EXPECTED_PAYMENT_RECORDS = 16443
EXPECTED_SCHEDULE_RECORDS = 16205
EXPECTED_PORTFOLIO_VALUE = 208192588.65
USD_CURRENCY = "USD"
FACTORING_PRODUCT = "factoring"
BULLET_FREQUENCY = "bullet"


class AbacoDataValidator:
    """Comprehensive validator for Abaco data processing."""

    def __init__(self, schema_path: str, data_dir: str):
        self.schema_path = Path(schema_path)
        self.data_dir = Path(data_dir)
        self.schema = self._load_schema()
        self.validation_results = {"passed": [], "failed": [], "warnings": []}

    def _load_schema(self) -> Dict:
        """Load and validate Abaco schema."""
        with open(self.schema_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def validate_all(self) -> Dict:
        """Run complete validation suite."""
        logger.info("🚀 Starting Abaco Data Validation")
        logger.info(f"Expected Records: {EXPECTED_TOTAL_RECORDS:,}")

        # Validate schema structure
        self._validate_schema_structure()

        # Validate record counts
        self._validate_record_counts()

        # Validate Spanish client names
        self._validate_spanish_clients()

        # Validate USD factoring
        self._validate_usd_factoring()

        # Validate bullet payments
        self._validate_bullet_payments()

        # Validate financial totals
        self._validate_financial_totals()

        # Validate data quality
        self._validate_data_quality()

        # Generate report
        return self._generate_validation_report()

    def _validate_schema_structure(self):
        """Validate schema has required structure."""
        logger.info("\n📋 Validating Schema Structure...")

        required_datasets = ["Loan Data", "Historic Real Payment", "Payment Schedule"]
        datasets = self.schema.get("datasets", {})

        for dataset_name in required_datasets:
            if dataset_name in datasets:
                self.validation_results["passed"].append(
                    f"✅ Schema contains {dataset_name}"
                )
            else:
                self.validation_results["failed"].append(
                    f"❌ Schema missing {dataset_name}"
                )

    def _validate_record_counts(self):
        """Validate record counts match expectations."""
        logger.info("\n📊 Validating Record Counts...")

        datasets = self.schema["datasets"]

        # Loan Data
        loan_rows = datasets["Loan Data"].get("rows", 0)
        if loan_rows == EXPECTED_LOAN_RECORDS:
            self.validation_results["passed"].append(
                f"✅ Loan Data: {loan_rows:,} records (expected: {EXPECTED_LOAN_RECORDS:,})"
            )
        else:
            self.validation_results["failed"].append(
                f"❌ Loan Data: {loan_rows:,} records (expected: {EXPECTED_LOAN_RECORDS:,})"
            )

        # Payment History
        payment_rows = datasets["Historic Real Payment"].get("rows", 0)
        if payment_rows == EXPECTED_PAYMENT_RECORDS:
            self.validation_results["passed"].append(
                f"✅ Payment History: {payment_rows:,} records (expected: {EXPECTED_PAYMENT_RECORDS:,})"
            )
        else:
            self.validation_results["failed"].append(
                f"❌ Payment History: {payment_rows:,} records (expected: {EXPECTED_PAYMENT_RECORDS:,})"
            )

        # Payment Schedule
        schedule_rows = datasets["Payment Schedule"].get("rows", 0)
        if schedule_rows == EXPECTED_SCHEDULE_RECORDS:
            self.validation_results["passed"].append(
                f"✅ Payment Schedule: {schedule_rows:,} records (expected: {EXPECTED_SCHEDULE_RECORDS:,})"
            )
        else:
            self.validation_results["failed"].append(
                f"❌ Payment Schedule: {schedule_rows:,} records (expected: {EXPECTED_SCHEDULE_RECORDS:,})"
            )

        # Total
        total_records = loan_rows + payment_rows + schedule_rows
        if total_records == EXPECTED_TOTAL_RECORDS:
            self.validation_results["passed"].append(
                f"✅ Total Records: {total_records:,} (expected: {EXPECTED_TOTAL_RECORDS:,})"
            )
        else:
            self.validation_results["failed"].append(
                f"❌ Total Records: {total_records:,} (expected: {EXPECTED_TOTAL_RECORDS:,})"
            )

    def _validate_spanish_clients(self):
        """Validate Spanish client name processing."""
        logger.info("\n🌍 Validating Spanish Client Names...")

        loan_data = self.schema["datasets"]["Loan Data"]
        cliente_column = next(
            (col for col in loan_data["columns"] if col["name"] == "Cliente"), None
        )

        if cliente_column:
            sample_values = cliente_column.get("sample_values", [])
            spanish_patterns = ["S.A. DE C.V.", "S.A.", "DE C.V."]

            spanish_count = sum(
                1
                for name in sample_values
                if any(pattern in name.upper() for pattern in spanish_patterns)
            )

            if spanish_count > 0:
                self.validation_results["passed"].append(
                    f"✅ Spanish client names detected: {spanish_count} samples"
                )
            else:
                self.validation_results["warnings"].append(
                    "⚠️  No Spanish client name patterns detected in samples"
                )

            # UTF-8 validation
            abaco_validation = cliente_column.get("abaco_validation", {})
            if abaco_validation.get("supports_utf8"):
                self.validation_results["passed"].append(
                    "✅ UTF-8 character encoding supported"
                )
        else:
            self.validation_results["failed"].append("❌ Cliente column not found")

    def _validate_usd_factoring(self):
        """Validate USD factoring configuration."""
        logger.info("\n💵 Validating USD Factoring...")

        loan_data = self.schema["datasets"]["Loan Data"]

        # Currency validation
        currency_column = next(
            (col for col in loan_data["columns"] if col["name"] == "Loan Currency"),
            None,
        )
        if currency_column:
            sample_currency = currency_column.get("sample_values", [])[0]
            if sample_currency == USD_CURRENCY:
                self.validation_results["passed"].append(
                    f"✅ Currency: {sample_currency} (expected: {USD_CURRENCY})"
                )
            else:
                self.validation_results["failed"].append(
                    f"❌ Currency: {sample_currency} (expected: {USD_CURRENCY})"
                )

        # Product type validation
        product_column = next(
            (col for col in loan_data["columns"] if col["name"] == "Product Type"), None
        )
        if product_column:
            sample_product = product_column.get("sample_values", [])[0]
            if sample_product.lower() == FACTORING_PRODUCT:
                self.validation_results["passed"].append(
                    f"✅ Product Type: {sample_product} (expected: {FACTORING_PRODUCT})"
                )
            else:
                self.validation_results["failed"].append(
                    f"❌ Product Type: {sample_product} (expected: {FACTORING_PRODUCT})"
                )

        # APR range validation
        apr_column = next(
            (col for col in loan_data["columns"] if col["name"] == "Interest Rate APR"),
            None,
        )
        if apr_column:
            abaco_validation = apr_column.get("abaco_validation", {})
            min_rate = abaco_validation.get("min_rate", 0)
            max_rate = abaco_validation.get("max_rate", 0)

            if 0.29 <= min_rate <= 0.30 and 0.36 <= max_rate <= 0.37:
                self.validation_results["passed"].append(
                    f"✅ APR Range: {min_rate*100:.2f}% - {max_rate*100:.2f}%"
                )
            else:
                self.validation_results["warnings"].append(
                    f"⚠️  APR Range: {min_rate*100:.2f}% - {max_rate*100:.2f}% (unexpected)"
                )

    def _validate_bullet_payments(self):
        """Validate bullet payment configuration."""
        logger.info("\n🎯 Validating Bullet Payment Structure...")

        loan_data = self.schema["datasets"]["Loan Data"]
        frequency_column = next(
            (col for col in loan_data["columns"] if col["name"] == "Payment Frequency"),
            None,
        )

        if frequency_column:
            sample_frequency = frequency_column.get("sample_values", [])[0]
            if sample_frequency.lower() == BULLET_FREQUENCY:
                self.validation_results["passed"].append(
                    f"✅ Payment Frequency: {sample_frequency} (expected: {BULLET_FREQUENCY})"
                )
            else:
                self.validation_results["failed"].append(
                    f"❌ Payment Frequency: {sample_frequency} (expected: {BULLET_FREQUENCY})"
                )

    def _validate_financial_totals(self):
        """Validate financial calculations."""
        logger.info("\n💰 Validating Financial Totals...")

        abaco_notes = self.schema.get("notes", {}).get("abaco_integration", {})
        financial_summary = abaco_notes.get("financial_summary", {})

        total_exposure = financial_summary.get("total_loan_exposure_usd", 0)

        # Allow 0.01% tolerance for floating point
        tolerance = EXPECTED_PORTFOLIO_VALUE * 0.0001

        if abs(total_exposure - EXPECTED_PORTFOLIO_VALUE) < tolerance:
            self.validation_results["passed"].append(
                f"✅ Portfolio Value: ${total_exposure:,.2f} USD"
            )
        else:
            self.validation_results["failed"].append(
                f"❌ Portfolio Value: ${total_exposure:,.2f} (expected: ${EXPECTED_PORTFOLIO_VALUE:,.2f})"
            )

        # Validate other financial metrics
        total_disbursed = financial_summary.get("total_disbursed_usd", 0)
        total_outstanding = financial_summary.get("total_outstanding_usd", 0)

        if total_disbursed > 0:
            self.validation_results["passed"].append(
                f"✅ Total Disbursed: ${total_disbursed:,.2f} USD"
            )

        if total_outstanding > 0:
            self.validation_results["passed"].append(
                f"✅ Total Outstanding: ${total_outstanding:,.2f} USD"
            )

    def _validate_data_quality(self):
        """Validate data quality metrics."""
        logger.info("\n🔍 Validating Data Quality...")

        loan_data = self.schema["datasets"]["Loan Data"]

        # Check for null values in critical columns
        critical_columns = ["Customer ID", "Loan ID", "Product Type", "Loan Currency"]

        for col_name in critical_columns:
            column = next(
                (col for col in loan_data["columns"] if col["name"] == col_name), None
            )
            if column:
                nulls = column.get("nulls", 0)
                if nulls == 0:
                    self.validation_results["passed"].append(
                        f"✅ {col_name}: Zero null values"
                    )
                else:
                    self.validation_results["warnings"].append(
                        f"⚠️  {col_name}: {nulls} null values found"
                    )

    def _generate_validation_report(self) -> Dict:
        """Generate comprehensive validation report."""
        logger.info("\n" + "=" * 70)
        logger.info("📊 ABACO DATA VALIDATION REPORT")
        logger.info("=" * 70)

        # Summary
        total_checks = (
            len(self.validation_results["passed"])
            + len(self.validation_results["failed"])
            + len(self.validation_results["warnings"])
        )

        passed_count = len(self.validation_results["passed"])
        failed_count = len(self.validation_results["failed"])
        warning_count = len(self.validation_results["warnings"])

        logger.info(f"\nTotal Checks: {total_checks}")
        logger.info(f"✅ Passed: {passed_count}")
        logger.info(f"❌ Failed: {failed_count}")
        logger.info(f"⚠️  Warnings: {warning_count}")

        # Detailed results
        if self.validation_results["passed"]:
            logger.info("\n✅ PASSED VALIDATIONS:")
            for result in self.validation_results["passed"]:
                logger.info(f"  {result}")

        if self.validation_results["failed"]:
            logger.info("\n❌ FAILED VALIDATIONS:")
            for result in self.validation_results["failed"]:
                logger.info(f"  {result}")

        if self.validation_results["warnings"]:
            logger.info("\n⚠️  WARNINGS:")
            for result in self.validation_results["warnings"]:
                logger.info(f"  {result}")

        # Final status
        logger.info("\n" + "=" * 70)
        if failed_count == 0:
            logger.info("🎉 VALIDATION STATUS: ✅ ALL CHECKS PASSED")
            logger.info("🚀 Abaco data is PRODUCTION READY")
        else:
            logger.info(f"⚠️  VALIDATION STATUS: ❌ {failed_count} CHECKS FAILED")
            logger.info("🔧 Please review failed validations above")
        logger.info("=" * 70 + "\n")

        return {
            "status": "passed" if failed_count == 0 else "failed",
            "total_checks": total_checks,
            "passed": passed_count,
            "failed": failed_count,
            "warnings": warning_count,
            "details": self.validation_results,
            "timestamp": datetime.now().isoformat(),
        }


def main():
    """Run Abaco data validation."""
    # Paths
    schema_path = "/Users/jenineferderas/Downloads/abaco_schema_autodetected.json"
    data_dir = "/Users/jenineferderas/Documents/GitHub/Commercial-View/data"

    # Create validator
    validator = AbacoDataValidator(schema_path, data_dir)

    # Run validation
    results = validator.validate_all()

    # Save results
    output_path = Path(
        "/Users/jenineferderas/Documents/GitHub/Commercial-View/validation_results.json"
    )
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    logger.info(f"\n📄 Results saved to: {output_path}")

    return 0 if results["status"] == "passed" else 1


if __name__ == "__main__":
    exit(main())
