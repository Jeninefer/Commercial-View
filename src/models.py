"""
Predictive Modeling Module for Commercial-View

Provides ML models for probability of default (PD), customer churn prediction,
and stress testing capabilities for portfolio risk assessment.
"""

import logging
from typing import Optional, Tuple, Dict, Any
import pandas as pd
import numpy as np
from pathlib import Path
import joblib

# ML imports
try:
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import roc_auc_score, classification_report
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    LogisticRegression = None
    StandardScaler = None

logger = logging.getLogger(__name__)

# Constants
DEFAULT_RANDOM_STATE = 42
DEFAULT_TEST_SIZE = 0.2
MAX_PD_VALUE = 1.0
MIN_PD_VALUE = 0.0


class PDModel:
    """
    Probability of Default (PD) Model using Logistic Regression.
    
    Predicts the likelihood of loan default based on loan characteristics.
    """

    def __init__(self, random_state: int = DEFAULT_RANDOM_STATE):
        """Initialize PD model with configuration."""
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn required for PDModel")
        
        self.model = LogisticRegression(random_state=random_state, max_iter=1000)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = []
        self.performance_metrics = {}

    def _select_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Select numeric features for modeling.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with selected numeric features
        """
        # Exclude target and ID columns
        exclude_cols = ['default_flag', 'customer_id', 'loan_id', 'id']
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        feature_cols = [col for col in numeric_cols if col.lower() not in exclude_cols]
        
        return df[feature_cols]

    def train(
        self,
        loan_df: pd.DataFrame,
        target_col: str = 'default_flag',
        test_size: float = DEFAULT_TEST_SIZE
    ) -> Dict[str, Any]:
        """
        Train the PD model on loan data.
        
        Args:
            loan_df: DataFrame with loan features and default flag
            target_col: Name of target column (default indicator)
            test_size: Proportion of data for testing
            
        Returns:
            Dictionary with training metrics
        """
        if loan_df is None or loan_df.empty:
            logger.error("Cannot train on empty DataFrame")
            return {'success': False, 'error': 'Empty DataFrame'}

        if target_col not in loan_df.columns:
            logger.error(f"Target column '{target_col}' not found")
            return {'success': False, 'error': f'Missing {target_col}'}

        try:
            # Select features
            X = self._select_features(loan_df)
            y = loan_df[target_col]
            
            # Handle missing values
            X = X.fillna(X.median())
            
            # Store feature names
            self.feature_names = X.columns.tolist()
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=DEFAULT_RANDOM_STATE,
                stratify=y if y.nunique() > 1 else None
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate
            y_pred_proba = self.model.predict_proba(X_test_scaled)[:, 1]
            y_pred = self.model.predict(X_test_scaled)
            
            # Calculate metrics
            auc_score = roc_auc_score(y_test, y_pred_proba)
            report = classification_report(y_test, y_pred, output_dict=True)
            
            self.performance_metrics = {
                'auc_score': float(auc_score),
                'accuracy': float(report['accuracy']),
                'precision': float(report['weighted avg']['precision']),
                'recall': float(report['weighted avg']['recall']),
                'f1_score': float(report['weighted avg']['f1-score']),
                'n_features': len(self.feature_names),
                'n_training_samples': len(X_train),
                'n_test_samples': len(X_test)
            }
            
            self.is_trained = True
            
            logger.info(f"✅ PD model trained successfully (AUC: {auc_score:.4f})")
            
            return {
                'success': True,
                'metrics': self.performance_metrics
            }
            
        except Exception as e:
            logger.error(f"Error training PD model: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def predict(self, loan_df: pd.DataFrame) -> pd.Series:
        """
        Predict probability of default for loans.
        
        Args:
            loan_df: DataFrame with loan features
            
        Returns:
            Series with PD predictions (0-1)
        """
        if not self.is_trained:
            logger.warning("Model not trained, returning zero probabilities")
            return pd.Series([0.0] * len(loan_df), index=loan_df.index)

        try:
            # Select and prepare features
            X = self._select_features(loan_df)
            
            # Ensure same features as training
            missing_features = set(self.feature_names) - set(X.columns)
            if missing_features:
                logger.warning(f"Missing features: {missing_features}")
                for feat in missing_features:
                    X[feat] = 0.0
            
            X = X[self.feature_names]
            X = X.fillna(X.median())
            
            # Scale and predict
            X_scaled = self.scaler.transform(X)
            pd_proba = self.model.predict_proba(X_scaled)[:, 1]
            
            logger.info(f"✅ Generated PD predictions for {len(loan_df)} loans")
            
            return pd.Series(pd_proba, index=loan_df.index)
            
        except Exception as e:
            logger.error(f"Error in PD prediction: {e}", exc_info=True)
            return pd.Series([0.0] * len(loan_df), index=loan_df.index)

    def save_model(self, filepath: str) -> bool:
        """Save trained model to disk."""
        if not self.is_trained:
            logger.error("Cannot save untrained model")
            return False
        
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            joblib.dump({
                'model': self.model,
                'scaler': self.scaler,
                'feature_names': self.feature_names,
                'metrics': self.performance_metrics
            }, filepath)
            logger.info(f"✅ Model saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            return False

    def load_model(self, filepath: str) -> bool:
        """Load trained model from disk."""
        try:
            data = joblib.load(filepath)
            self.model = data['model']
            self.scaler = data['scaler']
            self.feature_names = data['feature_names']
            self.performance_metrics = data['metrics']
            self.is_trained = True
            logger.info(f"✅ Model loaded from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False


class ChurnModel:
    """
    Customer Churn Prediction Model.
    
    Predicts the likelihood of customer churn based on behavior patterns.
    """

    def __init__(self, random_state: int = DEFAULT_RANDOM_STATE):
        """Initialize churn model."""
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn required for ChurnModel")
        
        self.model = LogisticRegression(random_state=random_state, max_iter=1000)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = []

    def train(self, customer_df: pd.DataFrame, target_col: str = 'churned_flag') -> Dict[str, Any]:
        """
        Train churn model.
        
        Args:
            customer_df: DataFrame with customer features
            target_col: Name of churn indicator column
            
        Returns:
            Training results dictionary
        """
        # Note: Implement similar to PDModel.train()
        logger.info("Churn model training not yet implemented")
        return {'success': False, 'error': 'Not implemented'}

    def predict(self, customer_df: pd.DataFrame) -> pd.Series:
        """
        Predict churn probability for customers.
        
        Args:
            customer_df: DataFrame with customer features
            
        Returns:
            Series with churn probabilities
        """
        logger.info(f"Generating churn predictions for {len(customer_df)} customers")
        # Placeholder: return zero probabilities
        return pd.Series([0.0] * len(customer_df), index=customer_df.index)


def run_stress_test(
    loan_df: pd.DataFrame,
    pd_column: str = 'pd',
    outstanding_column: str = 'outstanding_principal',
    shock_multiplier: float = 1.2
) -> Tuple[float, float, Dict[str, Any]]:
    """
    Run stress test on loan portfolio by shocking PD values.
    
    Args:
        loan_df: DataFrame with loan data
        pd_column: Column containing PD values
        outstanding_column: Column with outstanding principal
        shock_multiplier: Factor to multiply PDs (e.g., 1.2 = 20% increase)
        
    Returns:
        Tuple of (baseline_loss, stressed_loss, details_dict)
    """
    if loan_df is None or loan_df.empty:
        logger.warning("Cannot run stress test on empty DataFrame")
        return 0.0, 0.0, {'error': 'Empty DataFrame'}

    if pd_column not in loan_df.columns or outstanding_column not in loan_df.columns:
        logger.error(f"Required columns not found: {pd_column}, {outstanding_column}")
        return 0.0, 0.0, {'error': 'Missing columns'}

    try:
        # Get baseline values
        pds = loan_df[pd_column].fillna(0.0)
        outstanding = loan_df[outstanding_column].fillna(0.0)
        
        # Calculate baseline expected loss
        baseline_loss = (pds * outstanding).sum()
        
        # Apply shock to PDs (cap at 100%)
        shocked_pds = np.minimum(pds * shock_multiplier, MAX_PD_VALUE)
        
        # Calculate stressed expected loss
        stressed_loss = (shocked_pds * outstanding).sum()
        
        # Calculate impact
        loss_increase = stressed_loss - baseline_loss
        loss_increase_pct = (loss_increase / baseline_loss * 100.0) if baseline_loss > 0 else 0.0
        
        details = {
            'baseline_expected_loss': float(baseline_loss),
            'stressed_expected_loss': float(stressed_loss),
            'loss_increase': float(loss_increase),
            'loss_increase_pct': float(loss_increase_pct),
            'shock_multiplier': float(shock_multiplier),
            'n_loans': len(loan_df),
            'avg_pd_baseline': float(pds.mean()),
            'avg_pd_stressed': float(shocked_pds.mean())
        }
        
        logger.info(
            f"✅ Stress test complete: Baseline={baseline_loss:,.2f}, "
            f"Stressed={stressed_loss:,.2f}, Increase={loss_increase_pct:.2f}%"
        )
        
        return float(baseline_loss), float(stressed_loss), details
        
    except Exception as e:
        logger.error(f"Error running stress test: {e}", exc_info=True)
        return 0.0, 0.0, {'error': str(e)}


def calculate_expected_loss(
    loan_df: pd.DataFrame,
    pd_column: str = 'pd',
    lgd_column: str = 'lgd',
    ead_column: str = 'ead'
) -> pd.Series:
    """
    Calculate Expected Loss (EL) = PD × LGD × EAD for each loan.
    
    Args:
        loan_df: DataFrame with risk parameters
        pd_column: Probability of Default column
        lgd_column: Loss Given Default column
        ead_column: Exposure at Default column
        
    Returns:
        Series with expected loss values
    """
    try:
        pd_values = loan_df[pd_column].fillna(0.0) if pd_column in loan_df.columns else 0.0
        lgd_values = loan_df[lgd_column].fillna(0.45) if lgd_column in loan_df.columns else 0.45  # Default LGD
        ead_values = loan_df[ead_column].fillna(0.0) if ead_column in loan_df.columns else loan_df.get('outstanding_principal', 0.0)
        
        expected_loss = pd_values * lgd_values * ead_values
        
        logger.info(f"✅ Calculated expected loss for {len(loan_df)} loans")
        
        return expected_loss
        
    except Exception as e:
        logger.error(f"Error calculating expected loss: {e}")
        return pd.Series([0.0] * len(loan_df), index=loan_df.index)
