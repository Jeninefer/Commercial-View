"""
Feature engineering module extracted from PR #8 and #9
Customer classification and data processing utilities
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Any, Dict, Optional

class FeatureEngineer:
    """Feature engineering for commercial lending analytics"""
    
    CUSTOMER_TYPES = {
        'NEW': 'New',
        'RECURRENT': 'Recurrent',
        'RECOVERED': 'Recovered'
    }
    
    def classify_client_type(self,
                           df: pd.DataFrame,
                           customer_id_col: str = 'customer_id',
                           loan_count_col: str = 'loan_count', 
                           last_active_col: str = 'last_active_date',
                           reference_date: Optional[datetime] = None) -> pd.DataFrame:
        """
        Classify as New / Recurrent / Recovered based on loan count and gaps.
        If last gap >90d and returns => Recovered; if >1 loan and gaps <=90d => Recurrent; else New.
        """
        ref = (reference_date or datetime.now()).date()
        out = df.copy()
        if last_active_col in out.columns:
            out[last_active_col] = pd.to_datetime(out[last_active_col]).dt.date
            out["days_since_last"] = (pd.to_datetime(ref) - 
                                    pd.to_datetime(out[last_active_col])).dt.days
        else:
            out["days_since_last"] = np.nan

        def _label(row: pd.Series) -> str:
            cnt = row.get(loan_count_col, 0) or 0
            dsl = row.get("days_since_last", np.nan)
            if cnt <= 1:
                return self.CUSTOMER_TYPES['NEW']
            if pd.notna(dsl) and dsl > 90:
                return self.CUSTOMER_TYPES['RECOVERED']
            return self.CUSTOMER_TYPES['RECURRENT']

        out["customer_type"] = out.apply(_label, axis=1)
        return out
    
    def calculate_weighted_stats(self, portfolio_data: pd.DataFrame) -> Dict[str, float]:
        """Calculate weighted portfolio statistics.

        Parameters
        ----------
        portfolio_data
            DataFrame containing, at minimum, a column representing the
            outstanding balance (``outstanding_balance`` or one of its common
            aliases) which is used as the weighting factor. Metrics are resolved
            by alias for apr, tenor/term and loan amount so the function can be
            used with heterogeneous data sources.

        Returns
        -------
        Dict[str, float]
            Dictionary containing weighted KPIs and auxiliary portfolio
            information. All metrics default to ``np.nan`` when they cannot be
            computed due to missing data or zero/invalid weights.
        """

        if portfolio_data.empty:
            return {
                'weighted_apr': np.nan,
                'weighted_tenor': np.nan,
                'weighted_amount': np.nan,
                'weighted_eir': np.nan,
                'weighted_ltv': np.nan,
                'weighted_risk_score': np.nan,
                'total_outstanding_balance': 0.0,
                'total_loan_amount': 0.0,
                'portfolio_size': 0
            }

        df = portfolio_data.copy()

        weight_aliases = [
            'outstanding_balance', 'current_balance', 'balance', 'exposure',
            'olb', 'saldo_actual'
        ]
        weight_col = next((c for c in weight_aliases if c in df.columns), None)
        if not weight_col:
            # No valid weight column: return NaNs but keep basic totals if
            # possible to assist downstream diagnostics.
            outstanding = 0.0
            if 'outstanding_balance' in df.columns:
                outstanding = float(pd.to_numeric(df['outstanding_balance'], errors='coerce').sum(skipna=True))
            amount_total = 0.0
            for candidate in ['loan_amount', 'principal', 'origination_amount']:
                if candidate in df.columns:
                    amount_total = float(pd.to_numeric(df[candidate], errors='coerce').clip(lower=0).sum(skipna=True))
                    break
            return {
                'weighted_apr': np.nan,
                'weighted_tenor': np.nan,
                'weighted_amount': np.nan,
                'weighted_eir': np.nan,
                'weighted_ltv': np.nan,
                'weighted_risk_score': np.nan,
                'total_outstanding_balance': outstanding,
                'total_loan_amount': amount_total,
                'portfolio_size': int(len(df))
            }

        weights = pd.to_numeric(df[weight_col], errors='coerce')
        weights = weights.replace([np.inf, -np.inf], np.nan)
        valid_weight_mask = weights > 0
        weights = weights.where(valid_weight_mask)

        total_weight = float(weights.sum(skipna=True)) if valid_weight_mask.any() else 0.0

        def _weighted_average(column_candidates: Any) -> float:
            col = next((c for c in column_candidates if c in df.columns), None)
            if not col:
                return np.nan
            values = pd.to_numeric(df[col], errors='coerce')
            values = values.replace([np.inf, -np.inf], np.nan)
            mask = valid_weight_mask & values.notna()
            if not mask.any():
                return np.nan
            sub_weights = weights[mask]
            sub_values = values[mask]
            if sub_weights.empty or sub_weights.sum() == 0:
                return np.nan
            return float(np.average(sub_values, weights=sub_weights))

        weighted_stats = {
            'weighted_apr': _weighted_average(['apr', 'annual_rate', 'apr_percent', 'interest_rate']),
            'weighted_tenor': _weighted_average(['tenor_days', 'tenor', 'term', 'term_days']),
            'weighted_amount': _weighted_average(['loan_amount', 'principal', 'origination_amount']),
            'weighted_eir': _weighted_average(['eir', 'effective_interest_rate']),
            'weighted_ltv': _weighted_average(['ltv', 'loan_to_value', 'loan_to_value_ratio']),
            'weighted_risk_score': _weighted_average(['risk_score', 'internal_risk_score'])
        }

        total_loan_amount = 0.0
        if any(c in df.columns for c in ['loan_amount', 'principal', 'origination_amount']):
            amount_col = next((c for c in ['loan_amount', 'principal', 'origination_amount'] if c in df.columns), None)
            total_loan_amount = float(pd.to_numeric(df[amount_col], errors='coerce').clip(lower=0).sum(skipna=True))

        weighted_stats.update({
            'total_outstanding_balance': total_weight,
            'total_loan_amount': total_loan_amount,
            'portfolio_size': int(valid_weight_mask.sum())
        })

        return weighted_stats

    def calculate_customer_dpd_stats(self, payment_data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate customer-level DPD statistics"""
        dpd_stats: Dict[str, Any] = {
            'avg_dpd': 0.0,
            'max_dpd': 0,
            'customers_in_arrears': 0,
            'dpd_distribution': {}
        }

        if payment_data.empty:
            dpd_stats.update({
                'avg_dpd': 0.0,
                'max_dpd': 0,
                'customers_in_arrears': 0,
                'dpd_distribution': {
                    'current': 0,
                    'dpd_1_30': 0,
                    'dpd_31_60': 0,
                    'dpd_61_90': 0,
                    'dpd_91_plus': 0
                },
                'customer_count': 0,
                'arrears_rate': 0.0
            })
            return dpd_stats

        df = payment_data.copy()

        dpd_aliases = ['dpd', 'days_past_due', 'days_in_arrears']
        dpd_col = next((c for c in dpd_aliases if c in df.columns), None)
        if not dpd_col:
            return dpd_stats

        cust_aliases = ['customer_id', 'client_id', 'borrower_id']
        customer_col = next((c for c in cust_aliases if c in df.columns), None)
        if not customer_col:
            df[customer_col := 'customer_id'] = np.arange(len(df))

        dpd_values = pd.to_numeric(df[dpd_col], errors='coerce').fillna(0)
        dpd_values = dpd_values.clip(lower=0)
        df[dpd_col] = dpd_values

        grouped = df.groupby(customer_col)[dpd_col].agg(['mean', 'max'])

        customer_count = int(grouped.shape[0])
        avg_dpd = float(grouped['mean'].mean()) if customer_count else 0.0
        max_dpd = int(grouped['max'].max()) if customer_count else 0
        customers_in_arrears = int((grouped['max'] > 0).sum())

        bucket_edges = {
            'current': (0, 0),
            'dpd_1_30': (1, 30),
            'dpd_31_60': (31, 60),
            'dpd_61_90': (61, 90),
            'dpd_91_plus': (91, np.inf)
        }

        distribution: Dict[str, int] = {}
        for bucket, (lower, upper) in bucket_edges.items():
            if upper == np.inf:
                count = int((grouped['max'] >= lower).sum())
            elif lower == upper == 0:
                count = int((grouped['max'] == 0).sum())
            else:
                count = int(((grouped['max'] >= lower) & (grouped['max'] <= upper)).sum())
            distribution[bucket] = count

        arrears_rate = float(customers_in_arrears / customer_count) if customer_count else 0.0

        dpd_stats.update({
            'avg_dpd': avg_dpd,
            'max_dpd': max_dpd,
            'customers_in_arrears': customers_in_arrears,
            'dpd_distribution': distribution,
            'customer_count': customer_count,
            'arrears_rate': arrears_rate
        })

        return dpd_stats

    def engineer_risk_features(self, loan_data: pd.DataFrame) -> pd.DataFrame:
        """Engineer risk-related features for analysis.

        Expected input columns (or aliases) include:

        - ``bureau_score`` (``credit_score``, ``fico_score``)
        - ``behavior_score`` (``internal_score``)
        - ``financial_score`` (``cashflow_score``)
        - ``dpd`` (``days_past_due``)
        - ``ltv`` (``loan_to_value``)
        - ``utilization_rate`` (``credit_utilization``)
        - ``pd`` (probability of default) and ``lgd`` (loss given default)

        The function is resilient to missing columns; unavailable metrics are
        ignored and the remaining components are re-weighted accordingly.
        Additional diagnostic columns flag anomalies observed in the payment
        behaviour or structural attributes of the loan.
        """

        if loan_data.empty:
            loan_data['risk_score'] = np.nan
            loan_data['risk_category'] = pd.Categorical([], categories=['very_low', 'low', 'elevated', 'high'])
            loan_data['risk_alert_flag'] = pd.Series(dtype=bool)
            loan_data['dpd_alert'] = pd.Series(dtype=bool)
            loan_data['ltv_alert'] = pd.Series(dtype=bool)
            loan_data['utilization_alert'] = pd.Series(dtype=bool)
            loan_data['pd_alert'] = pd.Series(dtype=bool)
            loan_data['early_warning_signal'] = pd.Series(dtype=bool)
            return loan_data

        df = loan_data.copy()

        def _resolve_column(candidates):
            return next((c for c in candidates if c in df.columns), None)

        def _scale(series: pd.Series, invert: bool = False) -> pd.Series:
            if series is None:
                return pd.Series(np.nan, index=df.index)
            numeric = pd.to_numeric(series, errors='coerce')
            numeric = numeric.replace([np.inf, -np.inf], np.nan)
            if numeric.notna().sum() == 0:
                return pd.Series(np.nan, index=df.index)
            min_val = numeric.min()
            max_val = numeric.max()
            if not np.isfinite(min_val) or not np.isfinite(max_val) or min_val == max_val:
                scaled = pd.Series(0.5, index=df.index)
            else:
                scaled = (numeric - min_val) / (max_val - min_val)
            if invert:
                scaled = 1 - scaled
            return scaled.clip(0, 1)

        bureau_col = _resolve_column(['bureau_score', 'credit_score', 'credit_bureau_score', 'fico_score'])
        behaviour_col = _resolve_column(['behavior_score', 'behaviour_score', 'internal_score'])
        financial_col = _resolve_column(['financial_score', 'cashflow_score', 'debt_service_score'])
        dpd_col = _resolve_column(['dpd', 'days_past_due', 'days_in_arrears'])
        ltv_col = _resolve_column(['ltv', 'loan_to_value', 'loan_to_value_ratio'])
        utilisation_col = _resolve_column(['utilization_rate', 'credit_utilization', 'balance_to_limit'])
        pd_col = _resolve_column(['pd', 'prob_default', 'probability_of_default'])
        lgd_col = _resolve_column(['lgd', 'loss_given_default'])

        score_components = pd.concat(
            [
                _scale(df[bureau_col], invert=True) if bureau_col else pd.Series(np.nan, index=df.index),
                _scale(df[behaviour_col], invert=True) if behaviour_col else pd.Series(np.nan, index=df.index),
                _scale(df[financial_col], invert=True) if financial_col else pd.Series(np.nan, index=df.index)
            ],
            axis=1
        )
        score_components.columns = ['bureau_component', 'behaviour_component', 'financial_component']
        score_component = score_components.mean(axis=1, skipna=True)

        component_series = {
            'score_component': score_component,
            'dpd_component': _scale(df[dpd_col]) if dpd_col else pd.Series(np.nan, index=df.index),
            'ltv_component': _scale(df[ltv_col]) if ltv_col else pd.Series(np.nan, index=df.index),
            'utilisation_component': _scale(df[utilisation_col]) if utilisation_col else pd.Series(np.nan, index=df.index),
            'pd_component': _scale(df[pd_col]) if pd_col else pd.Series(np.nan, index=df.index),
            'lgd_component': _scale(df[lgd_col]) if lgd_col else pd.Series(np.nan, index=df.index)
        }

        base_weights = {
            'score_component': 0.35,
            'dpd_component': 0.2,
            'ltv_component': 0.15,
            'utilisation_component': 0.1,
            'pd_component': 0.15,
            'lgd_component': 0.05
        }

        available_weights = {k: w for k, w in base_weights.items() if component_series[k].notna().any()}
        weight_sum = sum(available_weights.values())
        if weight_sum == 0:
            df['risk_score'] = score_component.fillna(0.5).clip(0, 1)
        else:
            normalised_weights = {k: v / weight_sum for k, v in available_weights.items()}
            risk_score = pd.Series(0.0, index=df.index)
            for name, comp in component_series.items():
                if name in normalised_weights:
                    base_series = comp.copy()
                    if base_series.notna().sum() == 0:
                        base_series = pd.Series(0.5, index=df.index)
                    else:
                        base_series = base_series.fillna(base_series.mean())
                    risk_score = risk_score.add(base_series * normalised_weights[name], fill_value=0.0)
            df['risk_score'] = risk_score.clip(0, 1).fillna(0.5)

        risk_bins = [-np.inf, 0.25, 0.5, 0.75, np.inf]
        risk_labels = ['very_low', 'low', 'elevated', 'high']
        df['risk_category'] = pd.cut(df['risk_score'], bins=risk_bins, labels=risk_labels)

        dpd_series = pd.to_numeric(df[dpd_col], errors='coerce') if dpd_col else pd.Series(0, index=df.index)
        ltv_series = pd.to_numeric(df[ltv_col], errors='coerce') if ltv_col else pd.Series(0, index=df.index)
        util_series = pd.to_numeric(df[utilisation_col], errors='coerce') if utilisation_col else pd.Series(0, index=df.index)
        pd_series = pd.to_numeric(df[pd_col], errors='coerce') if pd_col else pd.Series(0, index=df.index)

        df['dpd_alert'] = dpd_series.fillna(0) > 30
        df['ltv_alert'] = ltv_series.fillna(0) > 0.85
        df['utilization_alert'] = util_series.fillna(0) > 0.9
        df['pd_alert'] = pd_series.fillna(0) > 0.2
        df['risk_alert_flag'] = (
            (df['risk_score'] >= 0.75) |
            df['dpd_alert'] |
            df['ltv_alert'] |
            df['utilization_alert'] |
            df['pd_alert']
        )
        df['early_warning_signal'] = df['risk_alert_flag'] & (df['risk_category'].isin(['elevated', 'high']))

        # Persist component diagnostics for transparency
        for name, series in score_components.items():
            df[f'{name}_scaled'] = series
        for key, series in component_series.items():
            df[f'{key}_scaled'] = series

        return df
