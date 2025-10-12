"""
Feature Engineering Module for Commercial View
Handles data transformation and feature creation
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Feature engineering and data transformation class"""

    def __init__(self):
        # Initialize feature engineer with default configuration
        # No specific initialization required at this time
        pass

    def engineer_loan_features(self, loan_df: pd.DataFrame) -> pd.DataFrame:
        """Create loan-specific features"""
        df = loan_df.copy()

        try:
            # Example feature engineering
            if "loan_amount" in df.columns:
                df["loan_amount_log"] = np.log1p(df["loan_amount"])

            if "interest_rate" in df.columns:
                df["high_interest"] = df["interest_rate"] > df["interest_rate"].median()

            logger.info("Loan features engineered successfully")
        except Exception as e:
            logger.error(f"Error in loan feature engineering: {e}")

        return df

    def engineer_payment_features(self, payment_df: pd.DataFrame) -> pd.DataFrame:
        """Create payment-specific features"""
        df = payment_df.copy()

        try:
            # Example payment feature engineering
            if "payment_date" in df.columns:
                df["payment_month"] = pd.to_datetime(df["payment_date"]).dt.month
                df["payment_year"] = pd.to_datetime(df["payment_date"]).dt.year

            logger.info("Payment features engineered successfully")
        except Exception as e:
            logger.error(f"Error in payment feature engineering: {e}")

        return df

    def classify_client_type(self, df: pd.DataFrame) -> pd.DataFrame:
        """Classify client types based on loan characteristics"""
        df = df.copy()

        try:
            # Simple classification based on available columns
            if "loan_amount" in df.columns:
                df["client_type"] = np.where(
                    df["loan_amount"] > df["loan_amount"].quantile(0.75),
                    "high_value",
                    "standard",
                )
            else:
                df["client_type"] = "standard"

            logger.info("Client classification completed")
        except Exception as e:
            logger.error(f"Error in client classification: {e}")
            df["client_type"] = "unknown"

        return df

    def create_risk_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create risk-based features for portfolio analysis"""
        df = df.copy()

        try:
            # Risk scoring based on available data
            risk_score = 0

            if "dpd" in df.columns:
                risk_score += np.where(df["dpd"] > 30, 2, 0)

            if "loan_amount" in df.columns:
                risk_score += np.where(
                    df["loan_amount"] > df["loan_amount"].quantile(0.9), 1, 0
                )

            df["risk_score"] = risk_score
            df["risk_category"] = pd.cut(
                df["risk_score"], bins=[-1, 0, 1, 3], labels=["low", "medium", "high"]
            )

            logger.info("Risk features created successfully")
        except Exception as e:
            logger.error(f"Error creating risk features: {e}")

        return df

    def engineer_temporal_features(
        self, df: pd.DataFrame, date_column: str = "date"
    ) -> pd.DataFrame:
        """Create temporal features from date columns"""
        df = df.copy()

        try:
            if date_column in df.columns:
                df[date_column] = pd.to_datetime(df[date_column])
                df["year"] = df[date_column].dt.year
                df["month"] = df[date_column].dt.month
                df["quarter"] = df[date_column].dt.quarter
                df["day_of_week"] = df[date_column].dt.dayofweek
                df["is_weekend"] = df["day_of_week"].isin([5, 6])

            logger.info("Temporal features created successfully")
        except Exception as e:
            logger.error(f"Error creating temporal features: {e}")

        return df

    def process_all_features(
        self, datasets: Dict[str, pd.DataFrame]
    ) -> Dict[str, pd.DataFrame]:
        """Process all feature engineering for multiple datasets"""
        processed_datasets = {}

        try:
            for name, df in datasets.items():
                logger.info(f"Processing features for {name}")

                # Apply general feature engineering
                processed_df = df.copy()

                if "loan" in name.lower():
                    processed_df = self.engineer_loan_features(processed_df)
                elif "payment" in name.lower():
                    processed_df = self.engineer_payment_features(processed_df)

                # Apply risk and temporal features
                processed_df = self.create_risk_features(processed_df)
                processed_df = self.classify_client_type(processed_df)

                processed_datasets[name] = processed_df

            logger.info("All feature engineering completed successfully")
        except Exception as e:
            logger.error(f"Error in feature engineering pipeline: {e}")
            processed_datasets = datasets

        return processed_datasets
