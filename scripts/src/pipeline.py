
# Abaco Integration Constants - 48,853 Records
# Spanish Clients | USD Factoring | Commercial Lending
DAYS_IN_DEFAULT = DAYS_IN_DEFAULT
INTEREST_RATE_APR = INTEREST_RATE_APR
OUTSTANDING_LOAN_VALUE = OUTSTANDING_LOAN_VALUE
LOAN_CURRENCY = LOAN_CURRENCY
PRODUCT_TYPE = PRODUCT_TYPE
ABACO_TECHNOLOGIES = ABACO_TECHNOLOGIES
ABACO_FINANCIAL = ABACO_FINANCIAL
LOAN_DATA = LOAN_DATA
HISTORIC_REAL_PAYMENT = HISTORIC_REAL_PAYMENT
PAYMENT_SCHEDULE = PAYMENT_SCHEDULE
CUSTOMER_ID = CUSTOMER_ID
LOAN_ID = LOAN_ID
SA_DE_CV = SA_DE_CV
TRUE_PAYMENT_STATUS = TRUE_PAYMENT_STATUS
TRUE_PAYMENT_DATE = TRUE_PAYMENT_DATE
DISBURSEMENT_DATE = DISBURSEMENT_DATE
DISBURSEMENT_AMOUNT = DISBURSEMENT_AMOUNT
PAYMENT_FREQUENCY = PAYMENT_FREQUENCY
LOAN_STATUS = LOAN_STATUS

"""Commercial View Data Pipeline - Enterprise Grade Implementation.

⚠️ ENVIRONMENT SETUP INSTRUCTIONS ⚠️
-----------------------------------
You're seeing this error because you're using system Python (/opt/homebrew/bin/python3)
instead of the project's virtual environment Python.

TO FIX THIS, COPY-PASTE THESE EXACT COMMANDS:

cd /Users/jenineferderas/Documents/GitHub/Commercial-View
source .venv/bin/activate
python -c "import pandas; print('✓ Environment is working correctly')"

THEN run your script with:
python src/pipeline.py

💡 IMPORTANT: NEVER use '/opt/homebrew/bin/python3' directly to run scripts
"""

from __future__ import annotations

import logging
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import numpy as np
import pandas as pd
from pandas import DataFrame

# Import constants to avoid string duplication (fixing SonarLint S1192)
from .abaco_schema import (
    DAYS_IN_DEFAULT_COLUMN,
    OUTSTANDING_LOAN_VALUE_COLUMN,
    DISBURSEMENT_DATE_COLUMN,
    TRUE_PAYMENT_DATE_COLUMN,
    DISBURSEMENT_AMOUNT_COLUMN,
    CUSTOMER_ID_COLUMN,
)

# Display a big warning if not in virtual environment
if not hasattr(sys, "real_prefix") and not (
    hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
):
    print("\n" + "=" * 80)
    print("\033[91m⚠️  ERROR: NOT USING VIRTUAL ENVIRONMENT ⚠️\033[0m")
    print("=" * 80)
    print(
        "\033[93mYou must activate the virtual environment before running any Python scripts.\033[0m"
    )
    print("\033[93mCopy and paste these commands:\033[0m")
    print("\033[92m  cd /Users/jenineferderas/Documents/GitHub/Commercial-View\033[0m")
    print("\033[92m  source .venv/bin/activate\033[0m")
    print("\033[92m  python src/pipeline.py\033[0m")
    print("=" * 80 + "\n")
    sys.exit(1)  # Exit with error code to prevent further execution with wrong Python

# Try importing required packages with helpful error messages
try:
    import pandas as pd
    import numpy as np
    from pandas import DataFrame
except ImportError as e:
    print(f"\033[91mError: {e}\033[0m")
    print("\033[93mInstall missing packages with:\033[0m")
    print("  source .venv/bin/activate")
    print("  pip install pandas numpy")
    # Re-raise to prevent further execution with missing dependencies
    raise

try:
    from src.data_loader import (
        load_loan_data,
        load_historic_real_payment,
        load_payment_schedule,
        load_customer_data,
        load_collateral,
    )
except ImportError as e:
    print(f"\033[91mError importing from src.data_loader: {e}\033[0m")
    print("\033[93mMake sure you're running from the project root directory\033[0m")
    raise

logger = logging.getLogger(__name__)


class CommercialViewPipeline:
    """Enterprise-grade data pipeline for Abaco Commercial View."""

    def __init__(self, base_path: Optional[Path] = None):
        """Initialize the pipeline with optional base path."""
        self.base_path = base_path
        self._datasets: Dict[str, DataFrame] = {}
        self._computed_metrics: Dict[str, Any] = {}

    def load_all_datasets(self) -> Dict[str, DataFrame]:
        """Load all available datasets with comprehensive error handling."""
        dataset_loaders = {
            "loan_data": load_loan_data,
            "historic_real_payment": load_historic_real_payment,
            "payment_schedule": load_payment_schedule,
            "customer_data": load_customer_data,
            "collateral": load_collateral,
        }

        for name, loader in dataset_loaders.items():
            try:
                self._datasets[name] = loader(self.base_path)
                logger.info(
                    f"Successfully loaded {name}: {len(self._datasets[name])} rows"
                )
            except FileNotFoundError:
                logger.warning(
                    f"Dataset {name} not found - will proceed with available data"
                )
                self._datasets[name] = pd.DataFrame()
            except Exception as e:
                logger.error(f"Error loading {name}: {str(e)}")
                self._datasets[name] = pd.DataFrame()

        return self._datasets

    def compute_dpd_metrics(self) -> DataFrame:
        """Compute Days Past Due (DPD) metrics with advanced logic."""
        if "loan_data" not in self._datasets or self._datasets["loan_data"].empty:
            return pd.DataFrame()

        loan_data = self._datasets["loan_data"].copy()

        # Compute DPD buckets
        dpd_buckets = [0, 7, 15, 21, 30, 60, 75, 90, 120, 150, 180]
        loan_data["dpd_bucket"] = pd.cut(
            loan_data[DAYS_IN_DEFAULT],
            bins=[-1] + dpd_buckets + [float("in")],
            labels=["Current"] + [f"{b}d" for b in dpd_buckets[1:]] + ["180d+"],
        )

        # Calculate past due amounts
        loan_data["past_due_amount"] = loan_data[OUTSTANDING_LOAN_VALUE] * (
            loan_data[DAYS_IN_DEFAULT] > 0
        ).astype(int)

        # Determine default status (>90 days)
        loan_data["is_default"] = loan_data[DAYS_IN_DEFAULT] > 90

        # Add reference date
        loan_data["reference_date"] = datetime.now().date()

        self._computed_metrics["dpd_frame"] = loan_data
        return loan_data

    def compute_portfolio_metrics(self) -> Dict[str, Any]:
        """Compute comprehensive portfolio-level metrics."""
        metrics = {}

        if "loan_data" in self._datasets and not self._datasets["loan_data"].empty:
            loan_data = self._datasets["loan_data"]

            # Portfolio Outstanding
            metrics["portfolio_outstanding"] = float(
                loan_data[OUTSTANDING_LOAN_VALUE].sum()
            )

            # Active Clients
            metrics["active_clients"] = int(
                loan_data[loan_data[OUTSTANDING_LOAN_VALUE] > 0][
                    CUSTOMER_ID
                ].nunique()
            )

            # Weighted APR
            outstanding_mask = loan_data[OUTSTANDING_LOAN_VALUE] > 0
            if outstanding_mask.any():
                metrics["weighted_apr"] = float(
                    np.average(
                        loan_data[outstanding_mask][INTEREST_RATE_APR],
                        weights=loan_data[outstanding_mask][OUTSTANDING_LOAN_VALUE],
                    )
                )
            else:
                metrics["weighted_apr"] = 0.0

            # NPL (Non-Performing Loans) > 180 days
            metrics["npl_180"] = float(
                loan_data[loan_data[DAYS_IN_DEFAULT] >= 180][
                    OUTSTANDING_LOAN_VALUE
                ].sum()
            )

            # Concentration metrics
            customer_outstanding = loan_data.groupby(CUSTOMER_ID)[
                OUTSTANDING_LOAN_VALUE
            ].sum()
            top_10_outstanding = customer_outstanding.nlargest(10).sum()
            metrics["concentration_top10_pct"] = float(
                top_10_outstanding / metrics["portfolio_outstanding"] * 100
                if metrics["portfolio_outstanding"] > 0
                else 0
            )

            # Single obligor concentration
            max_outstanding = (
                customer_outstanding.max() if len(customer_outstanding) > 0 else 0
            )
            metrics["max_borrower_pct"] = float(
                max_outstanding / metrics["portfolio_outstanding"] * 100
                if metrics["portfolio_outstanding"] > 0
                else 0
            )

            # DPD distribution
            dpd_data = self.compute_dpd_metrics()
            if not dpd_data.empty:
                dpd_dist = dpd_data.groupby("dpd_bucket")[
                    OUTSTANDING_LOAN_VALUE
                ].sum()
                metrics["dpd_distribution"] = {
                    str(k): float(v) for k, v in dpd_dist.items()
                }

        self._computed_metrics["portfolio_metrics"] = metrics
        return metrics

    def compute_recovery_metrics(self) -> DataFrame:
        """Compute recovery curve metrics by cohort."""
        if (
            "loan_data" not in self._datasets
            or "historic_real_payment" not in self._datasets
            or self._datasets["loan_data"].empty
            or self._datasets["historic_real_payment"].empty
        ):
            return pd.DataFrame()

        loan_data = self._datasets["loan_data"].copy()
        payments = self._datasets["historic_real_payment"].copy()

        try:
            # Convert dates
            loan_data[DISBURSEMENT_DATE] = pd.to_datetime(
                loan_data[DISBURSEMENT_DATE]
            )
            payments[TRUE_PAYMENT_DATE] = pd.to_datetime(
                payments[TRUE_PAYMENT_DATE]
            )

            # Create cohort based on disbursement month
            loan_data["cohort"] = loan_data[DISBURSEMENT_DATE].dt.to_period("M")

            # Merge payments with loan data
            recovery_data = payments.merge(
                loan_data[
                    [LOAN_ID, DISBURSEMENT_AMOUNT, "cohort", DISBURSEMENT_DATE]
                ],
                on=LOAN_ID,
                how="left",
            )

            # Calculate months since disbursement
            recovery_data["months_since_disbursement"] = (
                (
                    (
                        recovery_data[TRUE_PAYMENT_DATE]
                        - recovery_data[DISBURSEMENT_DATE]
                    ).dt.days
                    / 30.44
                )
                .round()
                .astype("Int64")
            )

            # Aggregate recovery by cohort and month
            recovery_summary = (
                recovery_data.groupby(["cohort", "months_since_disbursement"])
                .agg({"True Principal Payment": "sum", DISBURSEMENT_AMOUNT: "first"})
                .reset_index()
            )

            # Calculate cumulative recovery percentage
            recovery_summary["recovery_pct"] = (
                recovery_summary.groupby("cohort")["True Principal Payment"].cumsum()
                / recovery_summary[DISBURSEMENT_AMOUNT]
                * 100
            )

            self._computed_metrics["recovery_metrics"] = recovery_summary
            return recovery_summary

        except Exception as e:
            logger.error(f"Error computing recovery metrics: {str(e)}")
            return pd.DataFrame()

    def generate_executive_summary(self) -> Dict[str, Any]:
        """Generate comprehensive executive summary."""
        portfolio_metrics = self.compute_portfolio_metrics()

        summary = {
            "portfolio_overview": {
                "outstanding_balance": portfolio_metrics.get(
                    "portfolio_outstanding", 0
                ),
                "active_clients": portfolio_metrics.get("active_clients", 0),
                "weighted_apr": portfolio_metrics.get("weighted_apr", 0),
                "npl_ratio": (
                    portfolio_metrics.get("npl_180", 0)
                    / portfolio_metrics.get("portfolio_outstanding", 1)
                    * 100
                    if portfolio_metrics.get("portfolio_outstanding", 0) > 0
                    else 0
                ),
            },
            "risk_indicators": {
                "max_borrower_concentration": portfolio_metrics.get(
                    "max_borrower_pct", 0
                ),
                "top_10_concentration": portfolio_metrics.get(
                    "concentration_top10_pct", 0
                ),
                "dpd_distribution": portfolio_metrics.get("dpd_distribution", {}),
            },
            "data_quality": {
                "datasets_loaded": sum(
                    1 for df in self._datasets.values() if not df.empty
                ),
                "total_loans": len(self._datasets.get("loan_data", pd.DataFrame())),
                "total_payments": len(
                    self._datasets.get("historic_real_payment", pd.DataFrame())
                ),
            },
            "generated_at": datetime.now().isoformat(),
        }

        return summary

    def calculate_delinquency_metrics(self, loan_data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate comprehensive delinquency metrics."""
        metrics = {}

        if DAYS_IN_DEFAULT_COLUMN in loan_data.columns:
            dpd_series = loan_data[DAYS_IN_DEFAULT_COLUMN]

            # Calculate DPD buckets
            dpd_buckets = [0, 7, 15, 30, 60, 90, 120, 150, 180]
            loan_data["dpd_bucket"] = pd.cut(
                dpd_series,
                bins=[-1] + dpd_buckets + [float("in")],
                labels=["Current"] + [f"{b}d" for b in dpd_buckets[1:]] + ["180d+"],
            )

            # Calculate past due amounts
            loan_data["past_due_amount"] = loan_data[OUTSTANDING_LOAN_VALUE_COLUMN] * (
                dpd_series > 0
            ).astype(int)

            # Determine default status (>90 days)
            loan_data["is_default"] = dpd_series > 90

            metrics["dpd_distribution"] = loan_data.groupby("dpd_bucket")[
                OUTSTANDING_LOAN_VALUE_COLUMN
            ].sum()

        return metrics

    def process_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process and validate date columns."""
        df_processed = df.copy()

        # Process disbursement dates
        if DISBURSEMENT_DATE_COLUMN in df_processed.columns:
            df_processed[DISBURSEMENT_DATE_COLUMN] = pd.to_datetime(
                df_processed[DISBURSEMENT_DATE_COLUMN], errors="coerce"
            )

        # Process payment dates
        if TRUE_PAYMENT_DATE_COLUMN in df_processed.columns:
            df_processed[TRUE_PAYMENT_DATE_COLUMN] = pd.to_datetime(
                df_processed[TRUE_PAYMENT_DATE_COLUMN], errors="coerce"
            )

        return df_processed

    def calculate_financial_metrics(self, loan_data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate financial performance metrics."""
        metrics = {}

        if DISBURSEMENT_AMOUNT_COLUMN in loan_data.columns:
            disbursement_series = loan_data[DISBURSEMENT_AMOUNT_COLUMN]

            # Calculate total disbursement amount
            metrics["total_disbursement"] = disbursement_series.sum()

            # Calculate average disbursement amount
            metrics["average_disbursement"] = disbursement_series.mean()

        return metrics
