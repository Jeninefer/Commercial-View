"""
Predictive Modeling Module for Commercial-View

Provides PD (Probability of Default) models, churn prediction,
and stress testing capabilities for portfolio risk assessment.
"""

import logging
from typing import Tuple, Optional, List, Dict, Any
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

# Constants
DEFAULT_MAX_ITER = 1000
DEFAULT_RANDOM_STATE = 42
DEFAULT_TEST_SIZE = 0.2
DEFAULT_SHOCK_MULTIPLIER = 1.2
MIN_TRAINING_SAMPLES = 50
MAX_PD_VALUE = 1.0
MIN_PD_VALUE = 0.0

# Required model features
REQUIRED_PD_FEATURES = [
    'outstanding_principal',
    'interest_rate',
    'loan_amount',
    'dpd'
]


class PDModel:
    """
    Probability of Default (PD) model for credit risk assessment.
    
    Uses logistic regression to predict loan default probability
    based on borrower and loan characteristics.
    """

    def __init__(self, random_state: int = DEFAULT_RANDOM_STATE):
        """
        Initialize PD model.
        
        Args:
            random_state: Random seed for reproducibility
        """
        self.model = None
        self.features: Optional[List[str]] = None
        self.random_state = random_state
        self.training_metrics: Dict[str, float] = {}
        self.is_trained = False

    def _validate_training_data(
        self,
        loan_df: pd.DataFrame,
        target_column: str
    ) -> Tuple[bool, str]:
        """
        Validate training data requirements.
        
        Args:
            loan_df: Training DataFrame
            target_column: Target column name
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if loan_df.empty:
            return False, "Training data is empty"
        
        if target_column not in loan_df.columns:
            return False, f"Target column '{target_column}' not found"
        
        if len(loan_df) < MIN_TRAINING_SAMPLES:
            return False, f"Insufficient training samples (minimum: {MIN_TRAINING_SAMPLES})"
        
        # Check for sufficient positive and negative samples
        target_counts = loan_df[target_column].value_counts()
        if len(target_counts) < 2:
            return False, "Target variable must have at least 2 classes"
        
        return True, ""

    def _prepare_features(self, loan_df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare and clean features for modeling.
        
        Args:
            loan_df: Input DataFrame
            
        Returns:
            Cleaned feature DataFrame
        """
        # Select numeric columns only
        numeric_df = loan_df.select_dtypes(include=[np.number]).copy()
        
        # Fill missing values
        numeric_df = numeric_df.fillna(0)
        
        # Remove infinite values
        numeric_df = numeric_df.replace([np.inf, -np.inf], 0)
        
        return numeric_df

    def train(
        self,
        loan_df: pd.DataFrame,
        target_column: str = "default_flag",
        test_size: float = DEFAULT_TEST_SIZE
    ) -> Dict[str, Any]:
        """
        Train PD model to predict default probability.
        
        Args:
            loan_df: Training DataFrame with features and target
            target_column: Name of target variable (1=default, 0=no default)
            test_size: Proportion of data for validation
            
        Returns:
            Dictionary with training metrics
        """
        # Validate data
        is_valid, error_msg = self._validate_training_data(loan_df, target_column)
        if not is_valid:
            logger.warning(f"Training validation failed: {error_msg}")
            return {"error": error_msg, "trained": False}

        try:
            from sklearn.linear_model import LogisticRegression
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import roc_auc_score, accuracy_score, precision_score, recall_score

            # Prepare features
            X = self._prepare_features(loan_df)
            y = loan_df[target_column]

            # Store feature names
            self.features = X.columns.tolist()

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y,
                test_size=test_size,
                random_state=self.random_state,
                stratify=y
            )

            # Train model
            self.model = LogisticRegression(
                max_iter=DEFAULT_MAX_ITER,
                random_state=self.random_state,
                class_weight='balanced'  # Handle imbalanced classes
            )
            self.model.fit(X_train, y_train)

            # Evaluate on test set
            y_pred = self.model.predict(X_test)
            y_pred_proba = self.model.predict_proba(X_test)[:, 1]

            # Calculate metrics
            self.training_metrics = {
                "accuracy": float(accuracy_score(y_test, y_pred)),
                "precision": float(precision_score(y_test, y_pred, zero_division=0)),
                "recall": float(recall_score(y_test, y_pred, zero_division=0)),
                "roc_auc": float(roc_auc_score(y_test, y_pred_proba)),
                "n_features": len(self.features),
                "n_training_samples": len(X_train),
                "n_test_samples": len(X_test),
                "trained": True
            }

            self.is_trained = True
            logger.info(
                f"✅ PD model trained successfully "
                f"(AUC: {self.training_metrics['roc_auc']:.3f}, "
                f"Accuracy: {self.training_metrics['accuracy']:.3f})"
            )

            return self.training_metrics

        except ImportError as e:
            error_msg = f"scikit-learn not available: {e}"
            logger.error(error_msg)
            return {"error": error_msg, "trained": False}
        
        except Exception as e:
            error_msg = f"Error training PD model: {e}"
            logger.error(error_msg, exc_info=True)
            return {"error": error_msg, "trained": False}

    def predict(self, loan_df: pd.DataFrame) -> pd.Series:
        """
        Predict default probability for loans.
        
        Args:
            loan_df: DataFrame with loan features
            
        Returns:
            Series of default probabilities (0.0 to 1.0)
        """
        if not self.is_trained or self.model is None or self.features is None:
            logger.warning("PD model not trained; returning zero probabilities")
            return pd.Series(0.0, index=loan_df.index)

        if loan_df.empty:
            logger.warning("Empty DataFrame provided for prediction")
            return pd.Series(dtype=float)

        try:
            # Prepare features (only use trained features)
            X = loan_df[self.features].fillna(0)
            X = X.replace([np.inf, -np.inf], 0)

            # Predict probabilities
            probs = self.model.predict_proba(X)[:, 1]
            
            # Clip to valid range
            probs = np.clip(probs, MIN_PD_VALUE, MAX_PD_VALUE)

            result = pd.Series(probs, index=loan_df.index, name='pd')
            
            logger.info(f"✅ Generated PD predictions for {len(result)} loans")
            return result

        except Exception as e:
            logger.error(f"Error predicting PD: {e}", exc_info=True)
            return pd.Series(0.0, index=loan_df.index)

    def get_feature_importance(self) -> Optional[pd.DataFrame]:
        """
        Get feature importance from trained model.
        
        Returns:
            DataFrame with features and their coefficients
        """
        if not self.is_trained or self.model is None or self.features is None:
            logger.warning("Model not trained, no feature importance available")
            return None

        try:
            importance_df = pd.DataFrame({
                'feature': self.features,
                'coefficient': self.model.coef_[0],
                'abs_coefficient': np.abs(self.model.coef_[0])
            })
            
            importance_df = importance_df.sort_values('abs_coefficient', ascending=False)
            return importance_df

        except Exception as e:
            logger.error(f"Error getting feature importance: {e}")
            return None


class ChurnModel:
    """
    Customer churn prediction model.
    
    Predicts probability that a customer will stop doing business
    based on engagement and transaction patterns.
    """

    def __init__(self, random_state: int = DEFAULT_RANDOM_STATE):
        """Initialize churn model."""
        self.model = None
        self.features: Optional[List[str]] = None
        self.random_state = random_state
        self.is_trained = False

    def train(
        self,
        customer_df: pd.DataFrame,
        target_column: str = "churned"
    ) -> Dict[str, Any]:
        """
        Train churn prediction model.
        
        Args:
            customer_df: DataFrame with customer features and churn indicator
            target_column: Name of churn indicator column (1=churned, 0=active)
            
        Returns:
            Dictionary with training metrics
        """
        if customer_df.empty or target_column not in customer_df.columns:
            logger.warning("Insufficient data for churn model training")
            return {"error": "Insufficient data", "trained": False}

        try:
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import roc_auc_score, accuracy_score

            # Prepare features
            X = customer_df.select_dtypes(include=[np.number]).fillna(0)
            y = customer_df[target_column]

            self.features = X.columns.tolist()

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y,
                test_size=DEFAULT_TEST_SIZE,
                random_state=self.random_state
            )

            # Train model
            self.model = RandomForestClassifier(
                n_estimators=100,
                random_state=self.random_state,
                class_weight='balanced'
            )
            self.model.fit(X_train, y_train)

            # Evaluate
            y_pred_proba = self.model.predict_proba(X_test)[:, 1]
            
            metrics = {
                "roc_auc": float(roc_auc_score(y_test, y_pred_proba)),
                "accuracy": float(accuracy_score(y_test, self.model.predict(X_test))),
                "n_features": len(self.features),
                "trained": True
            }

            self.is_trained = True
            logger.info(f"✅ Churn model trained successfully (AUC: {metrics['roc_auc']:.3f})")
            
            return metrics

        except Exception as e:
            logger.error(f"Error training churn model: {e}", exc_info=True)
            return {"error": str(e), "trained": False}

    def predict(self, customer_df: pd.DataFrame) -> pd.Series:
        """
        Predict churn probability for customers.
        
        Args:
            customer_df: DataFrame with customer features
            
        Returns:
            Series of churn probabilities (0.0 to 1.0)
        """
        if not self.is_trained or self.model is None:
            logger.warning("Churn model not trained; returning zero probabilities")
            return pd.Series(0.0, index=customer_df.index)

        try:
            X = customer_df[self.features].fillna(0)
            probs = self.model.predict_proba(X)[:, 1]
            
            logger.info(f"✅ Generated churn predictions for {len(probs)} customers")
            return pd.Series(probs, index=customer_df.index, name='churn_probability')

        except Exception as e:
            logger.error(f"Error predicting churn: {e}")
            return pd.Series(0.0, index=customer_df.index)


def run_stress_test(
    loan_df: pd.DataFrame,
    shock_multiplier: float = DEFAULT_SHOCK_MULTIPLIER,
    pd_column: str = 'pd',
    outstanding_column: str = 'outstanding_principal'
) -> Dict[str, Any]:
    """
    Run portfolio stress test by applying shock to default rates.
    
    Args:
        loan_df: DataFrame with PD and outstanding balance
        shock_multiplier: Factor to increase default probability (e.g., 1.2 = 20% increase)
        pd_column: Name of PD column
        outstanding_column: Name of outstanding balance column
        
    Returns:
        Dictionary with stress test results including:
        - baseline_expected_loss: Expected loss under normal conditions
        - stressed_expected_loss: Expected loss under stress scenario
        - incremental_loss: Additional loss from stress
        - loss_increase_pct: Percentage increase in expected loss
    """
    # Validate inputs
    required_columns = [pd_column, outstanding_column]
    missing_columns = [col for col in required_columns if col not in loan_df.columns]
    
    if loan_df.empty or missing_columns:
        logger.warning(
            f"Insufficient data for stress test. "
            f"Missing columns: {missing_columns if missing_columns else 'None'}"
        )
        return {
            "baseline_expected_loss": 0.0,
            "stressed_expected_loss": 0.0,
            "incremental_loss": 0.0,
            "loss_increase_pct": 0.0,
            "error": "Insufficient data"
        }

    try:
        # Calculate baseline expected loss
        baseline_loss = float((loan_df[pd_column] * loan_df[outstanding_column]).sum())

        # Apply stress scenario
        stressed_pd = loan_df[pd_column] * shock_multiplier
        stressed_pd = stressed_pd.clip(upper=MAX_PD_VALUE)  # Cap at 100%

        # Calculate stressed expected loss
        stressed_loss = float((stressed_pd * loan_df[outstanding_column]).sum())

        # Calculate metrics
        incremental_loss = stressed_loss - baseline_loss
        loss_increase_pct = (
            (incremental_loss / baseline_loss * 100.0)
            if baseline_loss > 0 else 0.0
        )

        results = {
            "baseline_expected_loss": round(baseline_loss, 2),
            "stressed_expected_loss": round(stressed_loss, 2),
            "incremental_loss": round(incremental_loss, 2),
            "loss_increase_pct": round(loss_increase_pct, 2),
            "shock_multiplier": shock_multiplier,
            "n_loans_tested": len(loan_df)
        }

        logger.info(
            f"✅ Stress test completed: "
            f"Baseline loss: ${baseline_loss:,.0f}, "
            f"Stressed loss: ${stressed_loss:,.0f} "
            f"(+{loss_increase_pct:.1f}%)"
        )

        return results

    except Exception as e:
        logger.error(f"Error in stress testing: {e}", exc_info=True)
        return {
            "baseline_expected_loss": 0.0,
            "stressed_expected_loss": 0.0,
            "incremental_loss": 0.0,
            "loss_increase_pct": 0.0,
            "error": str(e)
        }


def run_scenario_analysis(
    loan_df: pd.DataFrame,
    scenarios: Dict[str, float],
    pd_column: str = 'pd',
    outstanding_column: str = 'outstanding_principal'
) -> pd.DataFrame:
    """
    Run multiple stress test scenarios.
    
    Args:
        loan_df: DataFrame with PD and outstanding balance
        scenarios: Dict mapping scenario names to shock multipliers
        pd_column: Name of PD column
        outstanding_column: Name of outstanding balance column
        
    Returns:
        DataFrame with results for each scenario
    """
    results = []
    
    for scenario_name, multiplier in scenarios.items():
        scenario_result = run_stress_test(
            loan_df,
            shock_multiplier=multiplier,
            pd_column=pd_column,
            outstanding_column=outstanding_column
        )
        scenario_result['scenario'] = scenario_name
        results.append(scenario_result)
    
    results_df = pd.DataFrame(results)
    
    logger.info(f"✅ Completed scenario analysis for {len(scenarios)} scenarios")
    
    return results_df
