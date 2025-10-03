"""Tests for PaymentProcessor class"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from abaco_core.payment_logic import PaymentProcessor


class TestPaymentProcessorInit:
    """Test PaymentProcessor initialization"""

    def test_default_threshold(self):
        processor = PaymentProcessor()
        assert processor.dpd_threshold == 180

    def test_custom_threshold(self):
        processor = PaymentProcessor(dpd_threshold=90)
        assert processor.dpd_threshold == 90

    def test_none_threshold_uses_default(self):
        processor = PaymentProcessor(dpd_threshold=None)
        assert processor.dpd_threshold == 180


class TestFieldDetection:
    """Test field detection functionality"""

    def test_detect_field_exact_match(self):
        processor = PaymentProcessor()
        df = pd.DataFrame(columns=["loan_id", "amount", "date"])
        
        result = processor._detect_field(df, [r"^loan_id$"])
        assert result == "loan_id"

    def test_detect_field_case_insensitive(self):
        processor = PaymentProcessor()
        df = pd.DataFrame(columns=["LOAN_ID", "amount", "date"])
        
        result = processor._detect_field(df, [r"^loan_id$"])
        assert result == "LOAN_ID"

    def test_detect_field_contains(self):
        processor = PaymentProcessor()
        df = pd.DataFrame(columns=["my_loan_id", "amount", "date"])
        
        result = processor._detect_field(df, ["loan_id"])
        assert result == "my_loan_id"

    def test_detect_field_regex(self):
        processor = PaymentProcessor()
        df = pd.DataFrame(columns=["application_loan_id", "amount", "date"])
        
        result = processor._detect_field(df, [r"loan.*id"])
        assert result == "application_loan_id"

    def test_detect_field_not_found(self):
        processor = PaymentProcessor()
        df = pd.DataFrame(columns=["customer_id", "amount", "date"])
        
        result = processor._detect_field(df, [r"^loan_id$"])
        assert result is None


class TestStandardizeDataframes:
    """Test dataframe standardization"""

    def test_standardize_basic(self):
        processor = PaymentProcessor()
        
        schedule = pd.DataFrame({
            "loan_id": ["L001", "L001"],
            "due_date": ["2024-01-01", "2024-02-01"],
            "due_amount": [100, 100]
        })
        
        payments = pd.DataFrame({
            "loan_id": ["L001"],
            "payment_date": ["2024-01-05"],
            "payment_amount": [100]
        })
        
        sched, pays = processor.standardize_dataframes(schedule, payments)
        
        assert "loan_id" in sched.columns
        assert "due_date" in sched.columns
        assert "due_amount" in sched.columns
        assert "loan_id" in pays.columns
        assert "payment_date" in pays.columns
        assert "payment_amount" in pays.columns

    def test_standardize_different_column_names(self):
        processor = PaymentProcessor()
        
        schedule = pd.DataFrame({
            "id_loan": ["L001", "L001"],
            "fecha_vencimiento": ["2024-01-01", "2024-02-01"],
            "cuota": [100, 100]
        })
        
        payments = pd.DataFrame({
            "id_loan": ["L001"],
            "fecha_pago": ["2024-01-05"],
            "monto_pago": [100]
        })
        
        sched, pays = processor.standardize_dataframes(schedule, payments)
        
        assert "loan_id" in sched.columns
        assert "due_date" in sched.columns
        assert "due_amount" in sched.columns

    def test_standardize_missing_id_raises_error(self):
        processor = PaymentProcessor()
        
        schedule = pd.DataFrame({
            "unknown_id": ["L001"],
            "due_date": ["2024-01-01"],
            "due_amount": [100]
        })
        
        payments = pd.DataFrame({
            "loan_id": ["L001"],
            "payment_date": ["2024-01-05"],
            "payment_amount": [100]
        })
        
        with pytest.raises(ValueError, match="Loan ID field not found"):
            processor.standardize_dataframes(schedule, payments)

    def test_standardize_converts_dates(self):
        processor = PaymentProcessor()
        
        schedule = pd.DataFrame({
            "loan_id": ["L001"],
            "due_date": ["2024-01-01"],
            "due_amount": [100]
        })
        
        payments = pd.DataFrame({
            "loan_id": ["L001"],
            "payment_date": ["2024-01-05"],
            "payment_amount": [100]
        })
        
        sched, pays = processor.standardize_dataframes(schedule, payments)
        
        assert isinstance(sched["due_date"].iloc[0], date)
        assert isinstance(pays["payment_date"].iloc[0], date)

    def test_standardize_converts_amounts_to_numeric(self):
        processor = PaymentProcessor()
        
        schedule = pd.DataFrame({
            "loan_id": ["L001"],
            "due_date": ["2024-01-01"],
            "due_amount": ["100.50"]
        })
        
        payments = pd.DataFrame({
            "loan_id": ["L001"],
            "payment_date": ["2024-01-05"],
            "payment_amount": ["100.50"]
        })
        
        sched, pays = processor.standardize_dataframes(schedule, payments)
        
        assert isinstance(sched["due_amount"].iloc[0], (int, float, np.number))
        assert isinstance(pays["payment_amount"].iloc[0], (int, float, np.number))


class TestCalculatePaymentTimeline:
    """Test payment timeline calculation"""

    def test_timeline_basic(self):
        processor = PaymentProcessor()
        
        schedule = pd.DataFrame({
            "loan_id": ["L001", "L001"],
            "due_date": ["2024-01-01", "2024-02-01"],
            "due_amount": [100, 100]
        })
        
        payments = pd.DataFrame({
            "loan_id": ["L001"],
            "payment_date": ["2024-01-05"],
            "payment_amount": [100]
        })
        
        ref_date = date(2024, 3, 1)
        timeline = processor.calculate_payment_timeline(schedule, payments, ref_date)
        
        assert "loan_id" in timeline.columns
        assert "date" in timeline.columns
        assert "cumulative_due" in timeline.columns
        assert "cumulative_paid" in timeline.columns
        assert "cumulative_gap" in timeline.columns

    def test_timeline_cumulative_calculations(self):
        processor = PaymentProcessor()
        
        schedule = pd.DataFrame({
            "loan_id": ["L001", "L001", "L001"],
            "due_date": ["2024-01-01", "2024-02-01", "2024-03-01"],
            "due_amount": [100, 100, 100]
        })
        
        payments = pd.DataFrame({
            "loan_id": ["L001", "L001"],
            "payment_date": ["2024-01-05", "2024-02-05"],
            "payment_amount": [50, 50]
        })
        
        ref_date = date(2024, 4, 1)
        timeline = processor.calculate_payment_timeline(schedule, payments, ref_date)
        
        # Check cumulative values
        last_row = timeline.iloc[-1]
        assert last_row["cumulative_due"] == 300
        assert last_row["cumulative_paid"] == 100
        assert last_row["cumulative_gap"] == 200

    def test_timeline_filters_by_reference_date(self):
        processor = PaymentProcessor()
        
        schedule = pd.DataFrame({
            "loan_id": ["L001", "L001", "L001"],
            "due_date": ["2024-01-01", "2024-02-01", "2024-03-01"],
            "due_amount": [100, 100, 100]
        })
        
        payments = pd.DataFrame({
            "loan_id": ["L001"],
            "payment_date": ["2024-01-05"],
            "payment_amount": [100]
        })
        
        ref_date = date(2024, 1, 15)
        timeline = processor.calculate_payment_timeline(schedule, payments, ref_date)
        
        # Only entries up to reference date should be included
        assert all(timeline["date"] <= ref_date)


class TestCalculateDPD:
    """Test DPD (Days Past Due) calculation"""

    def test_dpd_current_loan(self):
        processor = PaymentProcessor()
        
        schedule = pd.DataFrame({
            "loan_id": ["L001", "L001"],
            "due_date": ["2024-01-01", "2024-02-01"],
            "due_amount": [100, 100]
        })
        
        payments = pd.DataFrame({
            "loan_id": ["L001", "L001"],
            "payment_date": ["2024-01-01", "2024-02-01"],
            "payment_amount": [100, 100]
        })
        
        ref_date = date(2024, 3, 1)
        dpd = processor.calculate_dpd(schedule, payments, ref_date)
        
        assert dpd["days_past_due"].iloc[0] == 0
        assert dpd["past_due_amount"].iloc[0] == 0
        assert dpd["is_default"].iloc[0] == False

    def test_dpd_late_payment(self):
        processor = PaymentProcessor()
        
        schedule = pd.DataFrame({
            "loan_id": ["L001", "L001"],
            "due_date": ["2024-01-01", "2024-02-01"],
            "due_amount": [100, 100]
        })
        
        payments = pd.DataFrame({
            "loan_id": ["L001"],
            "payment_date": ["2024-01-01"],
            "payment_amount": [100]
        })
        
        ref_date = date(2024, 3, 1)
        dpd = processor.calculate_dpd(schedule, payments, ref_date)
        
        # Second payment is due but not made, so 29 days past due from Feb 1 to Mar 1
        assert dpd["days_past_due"].iloc[0] == 29
        assert dpd["past_due_amount"].iloc[0] == 100

    def test_dpd_default_threshold(self):
        processor = PaymentProcessor(dpd_threshold=30)
        
        schedule = pd.DataFrame({
            "loan_id": ["L001"],
            "due_date": ["2024-01-01"],
            "due_amount": [100]
        })
        
        payments = pd.DataFrame({
            "loan_id": ["L001"],
            "payment_date": ["2024-01-01"],
            "payment_amount": [0]
        })
        
        ref_date = date(2024, 2, 15)
        dpd = processor.calculate_dpd(schedule, payments, ref_date)
        
        # 45 days past due, should be marked as default with 30-day threshold
        assert dpd["is_default"].iloc[0] == True

    def test_dpd_output_columns(self):
        processor = PaymentProcessor()
        
        schedule = pd.DataFrame({
            "loan_id": ["L001"],
            "due_date": ["2024-01-01"],
            "due_amount": [100]
        })
        
        payments = pd.DataFrame({
            "loan_id": ["L001"],
            "payment_date": ["2024-01-01"],
            "payment_amount": [100]
        })
        
        ref_date = date(2024, 3, 1)
        dpd = processor.calculate_dpd(schedule, payments, ref_date)
        
        expected_columns = [
            "loan_id", "past_due_amount", "days_past_due", 
            "first_arrears_date", "last_payment_date", "last_due_date",
            "is_default", "reference_date"
        ]
        for col in expected_columns:
            assert col in dpd.columns


class TestAssignDPDBuckets:
    """Test DPD bucket assignment"""

    def test_bucket_current(self):
        processor = PaymentProcessor()
        
        dpd_df = pd.DataFrame({
            "loan_id": ["L001"],
            "days_past_due": [0]
        })
        
        result = processor.assign_dpd_buckets(dpd_df)
        
        assert result["dpd_bucket"].iloc[0] == "Current"
        assert result["dpd_bucket_value"].iloc[0] == 0
        assert result["dpd_bucket_description"].iloc[0] == "No payment due"
        assert result["default_flag"].iloc[0] == False

    def test_bucket_early_delinquency(self):
        processor = PaymentProcessor()
        
        dpd_df = pd.DataFrame({
            "loan_id": ["L001"],
            "days_past_due": [15]
        })
        
        result = processor.assign_dpd_buckets(dpd_df)
        
        assert result["dpd_bucket"].iloc[0] == "1-29"
        assert result["dpd_bucket_value"].iloc[0] == 1
        assert result["dpd_bucket_description"].iloc[0] == "Early delinquency"

    def test_bucket_30_days(self):
        processor = PaymentProcessor()
        
        dpd_df = pd.DataFrame({
            "loan_id": ["L001"],
            "days_past_due": [45]
        })
        
        result = processor.assign_dpd_buckets(dpd_df)
        
        assert result["dpd_bucket"].iloc[0] == "30-59"
        assert result["dpd_bucket_value"].iloc[0] == 30

    def test_bucket_180_plus(self):
        processor = PaymentProcessor()
        
        dpd_df = pd.DataFrame({
            "loan_id": ["L001"],
            "days_past_due": [200]
        })
        
        result = processor.assign_dpd_buckets(dpd_df)
        
        assert result["dpd_bucket"].iloc[0] == "180+"
        assert result["dpd_bucket_value"].iloc[0] == 180
        assert result["default_flag"].iloc[0] == True

    def test_all_buckets(self):
        processor = PaymentProcessor()
        
        dpd_df = pd.DataFrame({
            "loan_id": ["L001", "L002", "L003", "L004", "L005", "L006", "L007", "L008"],
            "days_past_due": [0, 15, 45, 75, 105, 135, 165, 200]
        })
        
        result = processor.assign_dpd_buckets(dpd_df)
        
        expected_buckets = ["Current", "1-29", "30-59", "60-89", "90-119", "120-149", "150-179", "180+"]
        assert list(result["dpd_bucket"]) == expected_buckets

    def test_bucket_preserves_original_columns(self):
        processor = PaymentProcessor()
        
        dpd_df = pd.DataFrame({
            "loan_id": ["L001"],
            "days_past_due": [15],
            "other_column": ["value"]
        })
        
        result = processor.assign_dpd_buckets(dpd_df)
        
        assert "loan_id" in result.columns
        assert "days_past_due" in result.columns
        assert "other_column" in result.columns


class TestIntegration:
    """Integration tests combining multiple methods"""

    def test_full_workflow(self):
        processor = PaymentProcessor()
        
        schedule = pd.DataFrame({
            "loan_id": ["L001", "L001", "L001", "L002", "L002"],
            "due_date": ["2024-01-01", "2024-02-01", "2024-03-01", "2024-01-15", "2024-02-15"],
            "due_amount": [100, 100, 100, 200, 200]
        })
        
        payments = pd.DataFrame({
            "loan_id": ["L001", "L001", "L002"],
            "payment_date": ["2024-01-05", "2024-02-05", "2024-01-20"],
            "payment_amount": [100, 50, 200]
        })
        
        ref_date = date(2024, 3, 15)
        
        # Calculate DPD
        dpd = processor.calculate_dpd(schedule, payments, ref_date)
        
        # Assign buckets
        result = processor.assign_dpd_buckets(dpd)
        
        assert len(result) == 2
        assert "dpd_bucket" in result.columns
        assert "default_flag" in result.columns

    def test_multiple_loans_timeline(self):
        processor = PaymentProcessor()
        
        schedule = pd.DataFrame({
            "loan_id": ["L001", "L001", "L002", "L002"],
            "due_date": ["2024-01-01", "2024-02-01", "2024-01-01", "2024-02-01"],
            "due_amount": [100, 100, 200, 200]
        })
        
        payments = pd.DataFrame({
            "loan_id": ["L001", "L002"],
            "payment_date": ["2024-01-05", "2024-01-10"],
            "payment_amount": [100, 150]
        })
        
        ref_date = date(2024, 2, 15)
        timeline = processor.calculate_payment_timeline(schedule, payments, ref_date)
        
        # Should have data for both loans
        assert len(timeline["loan_id"].unique()) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
