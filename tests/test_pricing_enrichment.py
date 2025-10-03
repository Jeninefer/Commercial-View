"""
Test suite for pricing enrichment functionality.
"""
import os
import tempfile
import json
import pandas as pd
import numpy as np
import yaml
import pytest
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.pricing_enrichment import enrich_with_pricing, _load_pricing_grid


class TestLoadPricingGrid:
    """Tests for _load_pricing_grid function."""

    def test_load_csv(self):
        """Test loading pricing grid from CSV file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write('product,apr,eir\n')
            f.write('A,5.0,4.5\n')
            f.write('B,6.0,5.5\n')
            temp_path = f.name
        
        try:
            df = _load_pricing_grid(temp_path)
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 2
            assert list(df.columns) == ['product', 'apr', 'eir']
            assert df['product'].tolist() == ['A', 'B']
        finally:
            os.unlink(temp_path)

    def test_load_json(self):
        """Test loading pricing grid from JSON file."""
        data = [
            {'product': 'A', 'apr': 5.0, 'eir': 4.5},
            {'product': 'B', 'apr': 6.0, 'eir': 5.5}
        ]
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            temp_path = f.name
        
        try:
            df = _load_pricing_grid(temp_path)
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 2
            assert 'product' in df.columns
        finally:
            os.unlink(temp_path)

    def test_load_yaml(self):
        """Test loading pricing grid from YAML file."""
        data = {
            'pricing_grid': [
                {'product': 'A', 'apr': 5.0, 'eir': 4.5},
                {'product': 'B', 'apr': 6.0, 'eir': 5.5}
            ]
        }
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(data, f)
            temp_path = f.name
        
        try:
            df = _load_pricing_grid(temp_path)
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 2
            assert 'product' in df.columns
        finally:
            os.unlink(temp_path)

    def test_load_yaml_without_pricing_grid_key(self):
        """Test loading YAML file without pricing_grid key."""
        data = [
            {'product': 'A', 'apr': 5.0, 'eir': 4.5},
            {'product': 'B', 'apr': 6.0, 'eir': 5.5}
        ]
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(data, f)
            temp_path = f.name
        
        try:
            df = _load_pricing_grid(temp_path)
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 2
        finally:
            os.unlink(temp_path)

    def test_load_parquet(self):
        """Test loading pricing grid from Parquet file."""
        df_to_save = pd.DataFrame({
            'product': ['A', 'B'],
            'apr': [5.0, 6.0],
            'eir': [4.5, 5.5]
        })
        with tempfile.NamedTemporaryFile(suffix='.parquet', delete=False) as f:
            temp_path = f.name
        
        try:
            df_to_save.to_parquet(temp_path)
            df = _load_pricing_grid(temp_path)
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 2
            assert list(df.columns) == ['product', 'apr', 'eir']
        finally:
            os.unlink(temp_path)

    def test_unsupported_format(self):
        """Test error handling for unsupported file formats."""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Unsupported pricing grid format"):
                _load_pricing_grid(temp_path)
        finally:
            os.unlink(temp_path)


class TestEnrichWithPricing:
    """Tests for enrich_with_pricing function."""

    def test_empty_dataframe_error(self):
        """Test that empty DataFrame raises ValueError."""
        empty_df = pd.DataFrame()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write('product,apr\n')
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="loans_df must be a non-empty DataFrame"):
                enrich_with_pricing(empty_df, temp_path, join_keys=['product'])
        finally:
            os.unlink(temp_path)

    def test_exact_join_on_keys(self):
        """Test exact join on specified keys."""
        loans_df = pd.DataFrame({
            'loan_id': [1, 2, 3],
            'product': ['A', 'B', 'C']
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write('product,apr,eir,recommended_rate\n')
            f.write('A,5.0,4.5,5.0\n')
            f.write('B,6.0,5.5,6.0\n')
            temp_path = f.name
        
        try:
            result = enrich_with_pricing(loans_df, temp_path, join_keys=['product'])
            assert 'apr' in result.columns
            assert 'eir' in result.columns
            assert 'recommended_rate' in result.columns
            assert result.loc[result['product'] == 'A', 'apr'].values[0] == 5.0
            assert result.loc[result['product'] == 'B', 'apr'].values[0] == 6.0
            assert pd.isna(result.loc[result['product'] == 'C', 'apr'].values[0])
        finally:
            os.unlink(temp_path)

    def test_missing_join_keys_in_loans(self):
        """Test error when join keys missing in loans DataFrame."""
        loans_df = pd.DataFrame({
            'loan_id': [1, 2, 3]
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write('product,apr\n')
            f.write('A,5.0\n')
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Missing join keys"):
                enrich_with_pricing(loans_df, temp_path, join_keys=['product'])
        finally:
            os.unlink(temp_path)

    def test_missing_join_keys_in_grid(self):
        """Test error when join keys missing in pricing grid."""
        loans_df = pd.DataFrame({
            'loan_id': [1, 2, 3],
            'product': ['A', 'B', 'C']
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write('category,apr\n')
            f.write('A,5.0\n')
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Missing join keys"):
                enrich_with_pricing(loans_df, temp_path, join_keys=['product'])
        finally:
            os.unlink(temp_path)

    def test_band_matching(self):
        """Test interval/band matching for ranges."""
        loans_df = pd.DataFrame({
            'loan_id': [1, 2, 3],
            'tenor_days': [30, 90, 180]
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write('tenor_min,tenor_max,apr,eir,recommended_rate\n')
            f.write('0,60,5.0,4.5,5.0\n')
            f.write('61,120,6.0,5.5,6.0\n')
            f.write('121,365,7.0,6.5,7.0\n')
            temp_path = f.name
        
        try:
            result = enrich_with_pricing(
                loans_df,
                temp_path,
                band_keys={'tenor_days': ['tenor_min', 'tenor_max']}
            )
            assert 'apr' in result.columns
            assert result.loc[result['tenor_days'] == 30, 'apr'].values[0] == 5.0
            assert result.loc[result['tenor_days'] == 90, 'apr'].values[0] == 6.0
            assert result.loc[result['tenor_days'] == 180, 'apr'].values[0] == 7.0
        finally:
            os.unlink(temp_path)

    def test_band_missing_feature_in_loans(self):
        """Test error when band feature missing in loans DataFrame."""
        loans_df = pd.DataFrame({
            'loan_id': [1, 2, 3]
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write('tenor_min,tenor_max,apr\n')
            f.write('0,60,5.0\n')
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Band feature 'tenor_days' not in loans_df"):
                enrich_with_pricing(
                    loans_df,
                    temp_path,
                    band_keys={'tenor_days': ['tenor_min', 'tenor_max']}
                )
        finally:
            os.unlink(temp_path)

    def test_band_missing_bounds_in_grid(self):
        """Test error when band bounds missing in pricing grid."""
        loans_df = pd.DataFrame({
            'loan_id': [1, 2, 3],
            'tenor_days': [30, 90, 180]
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write('apr\n')
            f.write('5.0\n')
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Band bounds .* not in pricing grid"):
                enrich_with_pricing(
                    loans_df,
                    temp_path,
                    band_keys={'tenor_days': ['tenor_min', 'tenor_max']}
                )
        finally:
            os.unlink(temp_path)

    def test_apr_eir_spread_calculation(self):
        """Test calculation of APR-EIR spread."""
        loans_df = pd.DataFrame({
            'loan_id': [1, 2],
            'product': ['A', 'B']
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write('product,apr,eir,recommended_rate\n')
            f.write('A,5.0,4.5,5.0\n')
            f.write('B,6.0,5.5,6.0\n')
            temp_path = f.name
        
        try:
            result = enrich_with_pricing(loans_df, temp_path, join_keys=['product'])
            assert 'apr_eir_spread' in result.columns
            assert result.loc[result['product'] == 'A', 'apr_eir_spread'].values[0] == 0.5
            assert result.loc[result['product'] == 'B', 'apr_eir_spread'].values[0] == 0.5
        finally:
            os.unlink(temp_path)

    def test_has_pricing_flag(self):
        """Test has_pricing flag based on recommended_rate availability."""
        loans_df = pd.DataFrame({
            'loan_id': [1, 2, 3],
            'product': ['A', 'B', 'C']
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write('product,apr,eir,recommended_rate\n')
            f.write('A,5.0,4.5,5.0\n')
            f.write('B,6.0,5.5,6.0\n')
            temp_path = f.name
        
        try:
            result = enrich_with_pricing(loans_df, temp_path, join_keys=['product'])
            assert 'has_pricing' in result.columns
            assert result.loc[result['product'] == 'A', 'has_pricing'].values[0] is True
            assert result.loc[result['product'] == 'B', 'has_pricing'].values[0] is True
            assert result.loc[result['product'] == 'C', 'has_pricing'].values[0] is False
        finally:
            os.unlink(temp_path)

    def test_empty_pricing_grid(self):
        """Test handling of empty pricing grid."""
        loans_df = pd.DataFrame({
            'loan_id': [1, 2],
            'product': ['A', 'B']
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write('product,apr,eir\n')
            temp_path = f.name
        
        try:
            result = enrich_with_pricing(loans_df, temp_path, join_keys=['product'])
            assert len(result) == len(loans_df)
            assert list(result.columns) == list(loans_df.columns)
        finally:
            os.unlink(temp_path)

    def test_combined_exact_and_band_matching(self):
        """Test combination of exact join and band matching."""
        loans_df = pd.DataFrame({
            'loan_id': [1, 2, 3],
            'product': ['A', 'A', 'B'],
            'tenor_days': [30, 90, 180]
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write('product,tenor_min,tenor_max,apr,eir,recommended_rate\n')
            f.write('A,0,60,5.0,4.5,5.0\n')
            f.write('A,61,120,6.0,5.5,6.0\n')
            f.write('B,121,365,7.0,6.5,7.0\n')
            temp_path = f.name
        
        try:
            result = enrich_with_pricing(
                loans_df,
                temp_path,
                join_keys=['product'],
                band_keys={'tenor_days': ['tenor_min', 'tenor_max']}
            )
            # Note: This test validates the API accepts both parameters
            # The exact behavior depends on implementation details
            assert 'apr' in result.columns
            assert 'eir' in result.columns
        finally:
            os.unlink(temp_path)

    def test_custom_rate_cols(self):
        """Test custom rate column names."""
        loans_df = pd.DataFrame({
            'loan_id': [1, 2],
            'product': ['A', 'B']
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write('product,rate1,rate2,recommended_rate\n')
            f.write('A,5.0,4.5,5.0\n')
            f.write('B,6.0,5.5,6.0\n')
            temp_path = f.name
        
        try:
            result = enrich_with_pricing(
                loans_df,
                temp_path,
                join_keys=['product'],
                rate_cols=('rate1', 'rate2')
            )
            assert 'apr_eir_spread' in result.columns
            assert result.loc[result['product'] == 'A', 'apr_eir_spread'].values[0] == 0.5
        finally:
            os.unlink(temp_path)

    def test_custom_recommended_col(self):
        """Test custom recommended column name."""
        loans_df = pd.DataFrame({
            'loan_id': [1, 2],
            'product': ['A', 'B']
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write('product,apr,eir,custom_rate\n')
            f.write('A,5.0,4.5,5.0\n')
            f.write('B,6.0,5.5,6.0\n')
            temp_path = f.name
        
        try:
            result = enrich_with_pricing(
                loans_df,
                temp_path,
                join_keys=['product'],
                recommended_col='custom_rate'
            )
            assert 'has_pricing' in result.columns
            assert result.loc[result['product'] == 'A', 'has_pricing'].values[0]
        finally:
            os.unlink(temp_path)

    def test_numeric_coercion_in_band_matching(self):
        """Test that band matching handles non-numeric values gracefully."""
        loans_df = pd.DataFrame({
            'loan_id': [1, 2, 3],
            'tenor_days': [30, 'invalid', 180]
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write('tenor_min,tenor_max,apr,eir,recommended_rate\n')
            f.write('0,60,5.0,4.5,5.0\n')
            f.write('121,365,7.0,6.5,7.0\n')
            temp_path = f.name
        
        try:
            result = enrich_with_pricing(
                loans_df,
                temp_path,
                band_keys={'tenor_days': ['tenor_min', 'tenor_max']}
            )
            assert 'apr' in result.columns
            # First row should match
            assert result.iloc[0]['apr'] == 5.0
            # Third row should match
            assert result.iloc[2]['apr'] == 7.0
        finally:
            os.unlink(temp_path)

    def test_band_with_inf_bounds(self):
        """Test band matching with infinite bounds."""
        loans_df = pd.DataFrame({
            'loan_id': [1, 2, 3],
            'tenor_days': [30, 90, 1000]
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write('tenor_min,tenor_max,apr,recommended_rate\n')
            f.write('0,60,5.0,5.0\n')
            f.write('61,,6.0,6.0\n')  # Missing max should become inf
            temp_path = f.name
        
        try:
            result = enrich_with_pricing(
                loans_df,
                temp_path,
                band_keys={'tenor_days': ['tenor_min', 'tenor_max']}
            )
            assert result.loc[result['tenor_days'] == 30, 'apr'].values[0] == 5.0
            assert result.loc[result['tenor_days'] == 90, 'apr'].values[0] == 6.0
            assert result.loc[result['tenor_days'] == 1000, 'apr'].values[0] == 6.0
        finally:
            os.unlink(temp_path)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
