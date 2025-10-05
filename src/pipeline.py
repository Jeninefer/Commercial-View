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

# Display a big warning if not in virtual environment (skip check in CI/automated environments)
is_ci = os.environ.get('CI') or os.environ.get('GITHUB_ACTIONS') or os.environ.get('CONTINUOUS_INTEGRATION')
if not is_ci and not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
    print("\n" + "="*80)
    print("\033[91m⚠️  ERROR: NOT USING VIRTUAL ENVIRONMENT ⚠️\033[0m")
    print("="*80)
    print("\033[93mYou must activate the virtual environment before running any Python scripts.\033[0m")
    print("\033[93mCopy and paste these commands:\033[0m")
    print("\033[92m  cd /Users/jenineferderas/Documents/GitHub/Commercial-View\033[0m")
    print("\033[92m  source .venv/bin/activate\033[0m")
    print("\033[92m  python src/pipeline.py\033[0m")
    print("="*80 + "\n")
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
            'loan_data': load_loan_data,
            'historic_real_payment': load_historic_real_payment,
            'payment_schedule': load_payment_schedule,
            'customer_data': load_customer_data,
            'collateral': load_collateral,
        }
        
        for name, loader in dataset_loaders.items():
            try:
                self._datasets[name] = loader(self.base_path)
                logger.info(f"Successfully loaded {name}: {len(self._datasets[name])} rows")
            except FileNotFoundError:
                logger.warning(f"Dataset {name} not found - will proceed with available data")
                self._datasets[name] = pd.DataFrame()
            except Exception as e:
                logger.error(f"Error loading {name}: {str(e)}")
                self._datasets[name] = pd.DataFrame()
                
        return self._datasets
    
    def compute_dpd_metrics(self) -> DataFrame:
        """Compute Days Past Due (DPD) metrics with advanced logic."""
        if 'loan_data' not in self._datasets or self._datasets['loan_data'].empty:
            return pd.DataFrame()
            
        loan_data = self._datasets['loan_data'].copy()
        
        # Compute DPD buckets
        dpd_buckets = [0, 7, 15, 21, 30, 60, 75, 90, 120, 150, 180]
        loan_data['dpd_bucket'] = pd.cut(
            loan_data['Days in Default'],
            bins=[-1] + dpd_buckets + [float('inf')],
            labels=['Current'] + [f'{b}d' for b in dpd_buckets[1:]] + ['180d+']
        )
        
        # Calculate past due amounts
        loan_data['past_due_amount'] = loan_data['Outstanding Loan Value'] * (
            loan_data['Days in Default'] > 0
        ).astype(int)
        
        # Determine default status (>90 days)
        loan_data['is_default'] = loan_data['Days in Default'] > 90
        
        # Add reference date
        loan_data['reference_date'] = datetime.now().date()
        
        self._computed_metrics['dpd_frame'] = loan_data
        return loan_data
    
    def compute_portfolio_metrics(self) -> Dict[str, Any]:
        """Compute comprehensive portfolio-level metrics."""
        metrics = {}
        
        if 'loan_data' in self._datasets and not self._datasets['loan_data'].empty:
            loan_data = self._datasets['loan_data']
            
            # Portfolio Outstanding
            metrics['portfolio_outstanding'] = float(loan_data['Outstanding Loan Value'].sum())
            
            # Active Clients
            metrics['active_clients'] = int(loan_data[
                loan_data['Outstanding Loan Value'] > 0
            ]['Customer ID'].nunique())
            
            # Weighted APR
            outstanding_mask = loan_data['Outstanding Loan Value'] > 0
            if outstanding_mask.any():
                metrics['weighted_apr'] = float(np.average(
                    loan_data[outstanding_mask]['Interest Rate APR'],
                    weights=loan_data[outstanding_mask]['Outstanding Loan Value']
                ))
            else:
                metrics['weighted_apr'] = 0.0
            
            # NPL (Non-Performing Loans) > 180 days
            metrics['npl_180'] = float(loan_data[
                loan_data['Days in Default'] >= 180
            ]['Outstanding Loan Value'].sum())
            
            # Concentration metrics
            customer_outstanding = loan_data.groupby('Customer ID')['Outstanding Loan Value'].sum()
            top_10_outstanding = customer_outstanding.nlargest(10).sum()
            metrics['concentration_top10_pct'] = float(
                top_10_outstanding / metrics['portfolio_outstanding'] * 100
                if metrics['portfolio_outstanding'] > 0 else 0
            )
            
            # Single obligor concentration
            max_outstanding = customer_outstanding.max() if len(customer_outstanding) > 0 else 0
            metrics['max_borrower_pct'] = float(
                max_outstanding / metrics['portfolio_outstanding'] * 100
                if metrics['portfolio_outstanding'] > 0 else 0
            )
            
            # DPD distribution
            dpd_data = self.compute_dpd_metrics()
            if not dpd_data.empty:
                dpd_dist = dpd_data.groupby('dpd_bucket')['Outstanding Loan Value'].sum()
                metrics['dpd_distribution'] = {str(k): float(v) for k, v in dpd_dist.items()}
        
        self._computed_metrics['portfolio_metrics'] = metrics
        return metrics
    
    def compute_recovery_metrics(self) -> DataFrame:
        """Compute recovery curve metrics by cohort."""
        if ('loan_data' not in self._datasets or 
            'historic_real_payment' not in self._datasets or
            self._datasets['loan_data'].empty or 
            self._datasets['historic_real_payment'].empty):
            return pd.DataFrame()
        
        loan_data = self._datasets['loan_data'].copy()
        payments = self._datasets['historic_real_payment'].copy()
        
        try:
            # Convert dates
            loan_data['Disbursement Date'] = pd.to_datetime(loan_data['Disbursement Date'])
            payments['True Payment Date'] = pd.to_datetime(payments['True Payment Date'])
            
            # Create cohort based on disbursement month
            loan_data['cohort'] = loan_data['Disbursement Date'].dt.to_period('M')
            
            # Merge payments with loan data
            recovery_data = payments.merge(
                loan_data[['Loan ID', 'Disbursement Amount', 'cohort', 'Disbursement Date']],
                on='Loan ID',
                how='left'
            )
            
            # Calculate months since disbursement
            recovery_data['months_since_disbursement'] = (
                (recovery_data['True Payment Date'] - recovery_data['Disbursement Date'])
                .dt.days / 30.44
            ).round().astype('Int64')
            
            # Aggregate recovery by cohort and month
            recovery_summary = recovery_data.groupby(['cohort', 'months_since_disbursement']).agg({
                'True Principal Payment': 'sum',
                'Disbursement Amount': 'first'
            }).reset_index()
            
            # Calculate cumulative recovery percentage
            recovery_summary['recovery_pct'] = (
                recovery_summary.groupby('cohort')['True Principal Payment'].cumsum() /
                recovery_summary['Disbursement Amount'] * 100
            )
            
            self._computed_metrics['recovery_metrics'] = recovery_summary
            return recovery_summary
            
        except Exception as e:
            logger.error(f"Error computing recovery metrics: {str(e)}")
            return pd.DataFrame()
    
    def generate_executive_summary(self) -> Dict[str, Any]:
        """Generate comprehensive executive summary."""
        portfolio_metrics = self.compute_portfolio_metrics()
        
        summary = {
            'portfolio_overview': {
                'outstanding_balance': portfolio_metrics.get('portfolio_outstanding', 0),
                'active_clients': portfolio_metrics.get('active_clients', 0),
                'weighted_apr': portfolio_metrics.get('weighted_apr', 0),
                'npl_ratio': (
                    portfolio_metrics.get('npl_180', 0) / 
                    portfolio_metrics.get('portfolio_outstanding', 1) * 100
                    if portfolio_metrics.get('portfolio_outstanding', 0) > 0 else 0
                )
            },
            'risk_indicators': {
                'max_borrower_concentration': portfolio_metrics.get('max_borrower_pct', 0),
                'top_10_concentration': portfolio_metrics.get('concentration_top10_pct', 0),
                'dpd_distribution': portfolio_metrics.get('dpd_distribution', {})
            },
            'data_quality': {
                'datasets_loaded': sum(1 for df in self._datasets.values() if not df.empty),
                'total_loans': len(self._datasets.get('loan_data', pd.DataFrame())),
                'total_payments': len(self._datasets.get('historic_real_payment', pd.DataFrame()))
            },
            'generated_at': datetime.now().isoformat()
        }
        
        return summary
