"""
Tests for the pricing enrichment functionality.
"""

import pytest
import pandas as pd
import yaml
from pathlib import Path
import tempfile
import shutil

from commercial_view import enrich_with_pricing


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_loans_df():
    """Create a sample loans DataFrame."""
    return pd.DataFrame({
        'loan_id': [1, 2, 3, 4, 5],
        'country': ['USA', 'USA', 'UK', 'UK', 'USA'],
        'sector': ['tech', 'retail', 'tech', 'finance', 'tech'],
        'risk_band': ['A', 'B', 'A', 'B', 'C'],
        'amount': [100000, 50000, 75000, 120000, 90000]
    })


@pytest.fixture
def sample_loans_with_intervals_df():
    """Create a sample loans DataFrame with interval columns."""
    return pd.DataFrame({
        'loan_id': [1, 2, 3, 4],
        'country': ['USA', 'USA', 'UK', 'UK'],
        'risk_band': ['A', 'B', 'A', 'B'],
        'tenor_days': [90, 180, 60, 365],
        'ticket_usd': [50000, 100000, 75000, 150000]
    })


@pytest.fixture
def pricing_parquet_file(temp_dir, sample_loans_df):
    """Create a sample pricing grid parquet file."""
    pricing_data = pd.DataFrame({
        'country': ['USA', 'USA', 'USA', 'UK', 'UK', 'UK'],
        'sector': ['tech', 'retail', 'finance', 'tech', 'retail', 'finance'],
        'risk_band': ['A', 'B', 'C', 'A', 'B', 'C'],
        'base_rate': [0.05, 0.07, 0.10, 0.06, 0.08, 0.11],
        'margin': [0.02, 0.03, 0.05, 0.025, 0.035, 0.045]
    })
    
    file_path = Path(temp_dir) / 'pricing_grid.parquet'
    pricing_data.to_parquet(file_path)
    return str(file_path)


@pytest.fixture
def pricing_yaml_file(temp_dir):
    """Create a sample pricing grid YAML file with intervals."""
    pricing_data = [
        {
            'country': 'USA',
            'risk_band': 'A',
            'tenor_min': 30,
            'tenor_max': 120,
            'ticket_min': 10000,
            'ticket_max': 100000,
            'apr': 0.05,
            'eir': 0.051,
            'recommended_rate': 0.052
        },
        {
            'country': 'USA',
            'risk_band': 'B',
            'tenor_min': 121,
            'tenor_max': 365,
            'ticket_min': 50000,
            'ticket_max': 200000,
            'apr': 0.08,
            'eir': 0.083,
            'recommended_rate': 0.085
        },
        {
            'country': 'UK',
            'risk_band': 'A',
            'tenor_min': 30,
            'tenor_max': 90,
            'ticket_min': 20000,
            'ticket_max': 100000,
            'apr': 0.06,
            'eir': 0.062,
            'recommended_rate': 0.063
        },
        {
            'country': 'UK',
            'risk_band': 'B',
            'tenor_min': 180,
            'tenor_max': 730,
            'ticket_min': 100000,
            'ticket_max': 500000,
            'apr': 0.09,
            'eir': 0.093,
            'recommended_rate': 0.095
        }
    ]
    
    file_path = Path(temp_dir) / 'pricing_grid.yaml'
    with open(file_path, 'w') as f:
        yaml.safe_dump(pricing_data, f)
    return str(file_path)


class TestEnrichWithPricingExactKeys:
    """Tests for exact key joins (parquet files)."""
    
    def test_exact_join_with_parquet(self, sample_loans_df, pricing_parquet_file):
        """Test exact key join with parquet file."""
        result = enrich_with_pricing(
            sample_loans_df,
            pricing_parquet_file,
            join_keys=["country", "sector", "risk_band"]
        )
        
        # Check that the result has the expected columns
        assert 'base_rate' in result.columns
        assert 'margin' in result.columns
        assert len(result) == len(sample_loans_df)
        
        # Check specific values
        usa_tech_a = result[(result['country'] == 'USA') & 
                           (result['sector'] == 'tech') & 
                           (result['risk_band'] == 'A')]
        assert len(usa_tech_a) == 1
        assert all(usa_tech_a['base_rate'] == 0.05)
        assert all(usa_tech_a['margin'] == 0.02)
    
    def test_exact_join_with_missing_keys(self, sample_loans_df, pricing_parquet_file):
        """Test exact key join when some keys don't match."""
        # Add a loan with no matching pricing
        df_with_extra = sample_loans_df.copy()
        df_with_extra.loc[len(df_with_extra)] = [6, 'Canada', 'tech', 'A', 80000]
        
        result = enrich_with_pricing(
            df_with_extra,
            pricing_parquet_file,
            join_keys=["country", "sector", "risk_band"]
        )
        
        # Check that all rows are present
        assert len(result) == len(df_with_extra)
        
        # Check that the Canada row has NaN for pricing columns
        canada_row = result[result['country'] == 'Canada']
        assert pd.isna(canada_row['base_rate'].iloc[0])


class TestEnrichWithPricingIntervalKeys:
    """Tests for interval/band key joins (YAML files)."""
    
    def test_interval_join_with_yaml(self, sample_loans_with_intervals_df, pricing_yaml_file):
        """Test interval join with YAML file."""
        result = enrich_with_pricing(
            sample_loans_with_intervals_df,
            pricing_yaml_file,
            join_keys=["country", "risk_band"],
            band_keys={
                "tenor_days": ["tenor_min", "tenor_max"],
                "ticket_usd": ["ticket_min", "ticket_max"]
            },
            rate_cols=("apr", "eir"),
            recommended_col="recommended_rate"
        )
        
        # Check that the result has the expected columns
        assert 'apr' in result.columns
        assert 'eir' in result.columns
        assert 'recommended_rate' in result.columns
        assert len(result) == len(sample_loans_with_intervals_df)
        
        # Check specific matches
        # Loan 1: USA, A, 90 days, $50,000 -> should match first rule
        loan1 = result[result['loan_id'] == 1]
        assert loan1['apr'].iloc[0] == 0.05
        assert loan1['eir'].iloc[0] == 0.051
        assert loan1['recommended_rate'].iloc[0] == 0.052
        
        # Loan 3: UK, A, 60 days, $75,000 -> should match third rule
        loan3 = result[result['loan_id'] == 3]
        assert loan3['apr'].iloc[0] == 0.06
        assert loan3['eir'].iloc[0] == 0.062
        assert loan3['recommended_rate'].iloc[0] == 0.063
    
    def test_interval_join_no_match(self, sample_loans_with_intervals_df, pricing_yaml_file):
        """Test interval join when some loans don't match any interval."""
        # Loan 2: USA, B, 180 days, $100,000 -> should match second rule
        result = enrich_with_pricing(
            sample_loans_with_intervals_df,
            pricing_yaml_file,
            join_keys=["country", "risk_band"],
            band_keys={
                "tenor_days": ["tenor_min", "tenor_max"],
                "ticket_usd": ["ticket_min", "ticket_max"]
            }
        )
        
        assert len(result) == len(sample_loans_with_intervals_df)
        
        # Loan 2 should match
        loan2 = result[result['loan_id'] == 2]
        assert not pd.isna(loan2['apr'].iloc[0])
        
    def test_interval_join_without_rate_filtering(self, sample_loans_with_intervals_df, pricing_yaml_file):
        """Test interval join without filtering rate columns."""
        result = enrich_with_pricing(
            sample_loans_with_intervals_df,
            pricing_yaml_file,
            join_keys=["country", "risk_band"],
            band_keys={
                "tenor_days": ["tenor_min", "tenor_max"],
                "ticket_usd": ["ticket_min", "ticket_max"]
            }
        )
        
        # All pricing columns should be present
        assert 'apr' in result.columns
        assert 'eir' in result.columns
        assert 'recommended_rate' in result.columns
        assert 'tenor_min' in result.columns
        assert 'tenor_max' in result.columns


class TestEnrichWithPricingEdgeCases:
    """Tests for edge cases and error conditions."""
    
    def test_unsupported_file_format(self, sample_loans_df, temp_dir):
        """Test that unsupported file formats raise an error."""
        file_path = Path(temp_dir) / 'pricing.csv'
        sample_loans_df.to_csv(file_path, index=False)
        
        with pytest.raises(ValueError, match="Unsupported file format"):
            enrich_with_pricing(
                sample_loans_df,
                str(file_path),
                join_keys=["country"]
            )
    
    def test_empty_dataframe(self, pricing_parquet_file):
        """Test with empty DataFrame."""
        empty_df = pd.DataFrame(columns=['country', 'sector', 'risk_band'])
        
        result = enrich_with_pricing(
            empty_df,
            pricing_parquet_file,
            join_keys=["country", "sector", "risk_band"]
        )
        
        assert len(result) == 0
        assert 'base_rate' in result.columns
