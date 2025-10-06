"""Unit tests for FeatureEngineer portfolio and risk computations."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.feature_engineer import FeatureEngineer


class TestWeightedStatistics:
    """Tests for weighted KPI calculations."""

    def setup_method(self) -> None:
        self.engineer = FeatureEngineer()

    def test_weighted_statistics_with_valid_data(self) -> None:
        portfolio = pd.DataFrame(
            {
                'loan_id': [1, 2, 3, 4],
                'apr': [0.10, 0.12, 0.08, 0.15],
                'tenor_days': [180, 360, 90, 120],
                'loan_amount': [100000, 150000, 50000, 40000],
                'outstanding_balance': [50000, 100000, 25000, -1000],
                'eir': [0.11, 0.13, np.nan, 0.14],
                'ltv': [0.60, 0.80, 0.90, 0.50],
                'risk_score': [0.4, 0.7, 0.2, 0.9],
            }
        )

        stats = self.engineer.calculate_weighted_stats(portfolio)

        total_balance = 50000 + 100000 + 25000
        expected_weighted_apr = (0.10 * 50000 + 0.12 * 100000 + 0.08 * 25000) / total_balance
        expected_weighted_tenor = (180 * 50000 + 360 * 100000 + 90 * 25000) / total_balance
        expected_weighted_amount = (100000 * 50000 + 150000 * 100000 + 50000 * 25000) / total_balance
        expected_weighted_eir = (0.11 * 50000 + 0.13 * 100000) / (50000 + 100000)
        expected_weighted_ltv = (0.60 * 50000 + 0.80 * 100000 + 0.90 * 25000) / total_balance
        expected_weighted_risk = (0.4 * 50000 + 0.7 * 100000 + 0.2 * 25000) / total_balance

        assert stats['portfolio_size'] == 3
        assert stats['total_outstanding_balance'] == pytest.approx(total_balance)
        assert stats['total_loan_amount'] == pytest.approx(100000 + 150000 + 50000 + 40000)
        assert stats['weighted_apr'] == pytest.approx(expected_weighted_apr)
        assert stats['weighted_tenor'] == pytest.approx(expected_weighted_tenor)
        assert stats['weighted_amount'] == pytest.approx(expected_weighted_amount)
        assert stats['weighted_eir'] == pytest.approx(expected_weighted_eir)
        assert stats['weighted_ltv'] == pytest.approx(expected_weighted_ltv)
        assert stats['weighted_risk_score'] == pytest.approx(expected_weighted_risk)

    def test_weighted_statistics_with_no_valid_weights(self) -> None:
        portfolio = pd.DataFrame(
            {
                'loan_id': [1, 2],
                'apr': [0.1, 0.2],
                'outstanding_balance': [0, np.nan],
            }
        )

        stats = self.engineer.calculate_weighted_stats(portfolio)

        assert stats['portfolio_size'] == 0
        assert stats['total_outstanding_balance'] == 0.0
        assert np.isnan(stats['weighted_apr'])
        assert np.isnan(stats['weighted_tenor'])
        assert np.isnan(stats['weighted_amount'])


class TestCustomerDPDStatistics:
    """Tests for customer DPD aggregation."""

    def setup_method(self) -> None:
        self.engineer = FeatureEngineer()

    def test_customer_dpd_distribution(self) -> None:
        payment_history = pd.DataFrame(
            {
                'customer_id': ['c1', 'c1', 'c2', 'c2', 'c3'],
                'dpd': [0, 5, 30, 45, np.nan],
            }
        )

        stats = self.engineer.calculate_customer_dpd_stats(payment_history)

        assert stats['customer_count'] == 3
        assert stats['customers_in_arrears'] == 2
        assert stats['max_dpd'] == 45
        assert stats['avg_dpd'] == pytest.approx((2.5 + 37.5 + 0.0) / 3)
        assert stats['arrears_rate'] == pytest.approx(2 / 3)
        assert stats['dpd_distribution'] == {
            'current': 1,
            'dpd_1_30': 1,
            'dpd_31_60': 1,
            'dpd_61_90': 0,
            'dpd_91_plus': 0,
        }

    def test_customer_dpd_empty_input(self) -> None:
        stats = self.engineer.calculate_customer_dpd_stats(pd.DataFrame(columns=['customer_id', 'dpd']))

        assert stats['customer_count'] == 0
        assert stats['dpd_distribution'] == {
            'current': 0,
            'dpd_1_30': 0,
            'dpd_31_60': 0,
            'dpd_61_90': 0,
            'dpd_91_plus': 0,
        }


class TestRiskFeatureEngineering:
    """Tests for risk feature creation."""

    def setup_method(self) -> None:
        self.engineer = FeatureEngineer()

    def test_risk_features_computation(self) -> None:
        loan_data = pd.DataFrame(
            {
                'bureau_score': [700, 600, 500],
                'behavior_score': [80, 60, 40],
                'financial_score': [75, 65, 55],
                'dpd': [0, 45, 10],
                'ltv': [0.60, 0.90, 0.95],
                'utilization_rate': [0.50, 0.95, 0.85],
                'pd': [0.05, 0.25, 0.15],
                'lgd': [0.30, 0.45, 0.50],
            }
        )

        enriched = self.engineer.engineer_risk_features(loan_data)

        assert enriched['risk_score'].tolist() == pytest.approx([0.0, 0.7911, 0.7472], rel=1e-4)
        assert enriched['risk_category'].astype(str).tolist() == ['very_low', 'high', 'elevated']
        assert enriched['dpd_alert'].tolist() == [False, True, False]
        assert enriched['ltv_alert'].tolist() == [False, True, True]
        assert enriched['utilization_alert'].tolist() == [False, True, False]
        assert enriched['pd_alert'].tolist() == [False, True, False]
        assert enriched['risk_alert_flag'].tolist() == [False, True, True]
        assert enriched['early_warning_signal'].tolist() == [False, True, True]

        for column in [
            'bureau_component_scaled',
            'behavior_component_scaled',
            'financial_component_scaled',
            'score_component_scaled',
            'dpd_component_scaled',
            'ltv_component_scaled',
            'utilization_component_scaled',
            'pd_component_scaled',
            'lgd_component_scaled',
        ]:
            assert column in enriched.columns
            col = enriched[column]
            assert col.isna().all() or col.between(0, 1).all()

    def test_risk_features_with_missing_columns(self) -> None:
        loan_data = pd.DataFrame({'loan_id': [1, 2, 3]})
        enriched = self.engineer.engineer_risk_features(loan_data)

        assert 'risk_score' in enriched.columns
        assert enriched['risk_score'].tolist() == [0.5, 0.5, 0.5]
        assert enriched['risk_category'].astype(str).tolist() == ['low', 'low', 'low']
        assert not enriched['risk_alert_flag'].any()
