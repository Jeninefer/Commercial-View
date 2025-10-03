"""
Unit tests for the Pricing Enrichment Module
"""

import unittest
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import tempfile
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from pricing_enrichment import PricingEnricher, enrich_pricing


class TestPricingEnricher(unittest.TestCase):
    """Test cases for PricingEnricher class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.enricher = PricingEnricher()
    
    def test_initialization(self):
        """Test PricingEnricher initialization"""
        enricher = PricingEnricher()
        self.assertIsNone(enricher.pricing_grid)
        self.assertIsNone(enricher.recommended_pricing)
        self.assertEqual(enricher.pricing_paths, [])
    
    def test_initialization_with_paths(self):
        """Test PricingEnricher initialization with paths"""
        paths = ['path1.csv', 'path2.csv']
        enricher = PricingEnricher(pricing_paths=paths)
        self.assertEqual(enricher.pricing_paths, paths)
    
    def test_identify_rate_columns_with_hints(self):
        """Test rate column identification with explicit hints"""
        df = pd.DataFrame({
            'apr_rate': [0.05, 0.06],
            'eir_rate': [0.04, 0.05],
            'amount': [1000, 2000]
        })
        
        apr_col, eir_col = self.enricher._identify_rate_columns(
            df, 
            apr_col_hint='apr_rate',
            eir_col_hint='eir_rate'
        )
        
        self.assertEqual(apr_col, 'apr_rate')
        self.assertEqual(eir_col, 'eir_rate')
    
    def test_identify_rate_columns_auto(self):
        """Test automatic rate column identification"""
        df = pd.DataFrame({
            'APR': [0.05, 0.06],
            'EIR': [0.04, 0.05],
            'amount': [1000, 2000]
        })
        
        apr_col, eir_col = self.enricher._identify_rate_columns(df)
        
        self.assertEqual(apr_col, 'APR')
        self.assertEqual(eir_col, 'EIR')
    
    def test_identify_rate_columns_not_found(self):
        """Test rate column identification when columns don't exist"""
        df = pd.DataFrame({
            'amount': [1000, 2000],
            'tenor': [12, 24]
        })
        
        apr_col, eir_col = self.enricher._identify_rate_columns(df)
        
        self.assertIsNone(apr_col)
        self.assertIsNone(eir_col)
    
    def test_enrich_loan_data_basic(self):
        """Test basic loan data enrichment without pricing data"""
        loan_df = pd.DataFrame({
            'loan_id': [1, 2],
            'APR': [0.05, 0.06],
            'EIR': [0.04, 0.05],
            'amount': [1000, 2000]
        })
        
        result = self.enricher.enrich_loan_data(loan_df)
        
        self.assertIn('apr_eir_spread', result.columns)
        self.assertAlmostEqual(result.loc[0, 'apr_eir_spread'], 0.01)
        self.assertAlmostEqual(result.loc[1, 'apr_eir_spread'], 0.01)
    
    def test_enrich_loan_data_with_join_keys(self):
        """Test loan data enrichment with join keys"""
        loan_df = pd.DataFrame({
            'loan_id': [1, 2],
            'product': ['A', 'B'],
            'APR': [0.05, 0.06],
            'EIR': [0.04, 0.05]
        })
        
        recommended_pricing = pd.DataFrame({
            'product': ['A', 'B'],
            'recommended_rate': [0.045, 0.055]
        })
        
        self.enricher.recommended_pricing = recommended_pricing
        
        result = self.enricher.enrich_loan_data(
            loan_df,
            join_keys=['product']
        )
        
        self.assertIn('recommended_rate', result.columns)
        self.assertEqual(result.loc[0, 'recommended_rate'], 0.045)
        self.assertEqual(result.loc[1, 'recommended_rate'], 0.055)
    
    def test_enrich_loan_data_with_band_keys(self):
        """Test loan data enrichment with band/interval matching"""
        loan_df = pd.DataFrame({
            'loan_id': [1, 2],
            'tenor_days': [90, 180],
            'APR': [0.05, 0.06],
            'EIR': [0.04, 0.05]
        })
        
        pricing_grid = pd.DataFrame({
            'tenor_min': [0, 120],
            'tenor_max': [120, 365],
            'rate_adjustment': [0.01, 0.02]
        })
        
        self.enricher.pricing_grid = pricing_grid
        
        result = self.enricher.enrich_loan_data(
            loan_df,
            band_keys={'tenor_days': ('tenor_min', 'tenor_max')}
        )
        
        self.assertIn('rate_adjustment', result.columns)
        self.assertEqual(result.loc[0, 'rate_adjustment'], 0.01)
        self.assertEqual(result.loc[1, 'rate_adjustment'], 0.02)


class TestEnrichPricingFunction(unittest.TestCase):
    """Test cases for enrich_pricing function"""
    
    def test_enrich_pricing_empty_dataframe(self):
        """Test that empty DataFrame raises ValueError"""
        empty_df = pd.DataFrame()
        
        with self.assertRaises(ValueError) as context:
            enrich_pricing(empty_df)
        
        self.assertIn("non-empty DataFrame", str(context.exception))
    
    def test_enrich_pricing_none_dataframe(self):
        """Test that None DataFrame raises ValueError"""
        with self.assertRaises(ValueError) as context:
            enrich_pricing(None)
        
        self.assertIn("non-empty DataFrame", str(context.exception))
    
    def test_enrich_pricing_basic(self):
        """Test basic enrich_pricing function"""
        loan_df = pd.DataFrame({
            'loan_id': [1, 2],
            'APR': [0.05, 0.06],
            'EIR': [0.04, 0.05],
            'amount': [1000, 2000]
        })
        
        result = enrich_pricing(loan_df, autoload=False)
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertIn('apr_eir_spread', result.columns)
    
    def test_enrich_pricing_with_explicit_columns(self):
        """Test enrich_pricing with explicit APR/EIR columns"""
        loan_df = pd.DataFrame({
            'loan_id': [1, 2],
            'annual_percentage_rate': [0.05, 0.06],
            'effective_interest_rate': [0.04, 0.05],
            'amount': [1000, 2000]
        })
        
        result = enrich_pricing(
            loan_df,
            apr_col_hint='annual_percentage_rate',
            eir_col_hint='effective_interest_rate',
            autoload=False
        )
        
        self.assertIn('apr_eir_spread', result.columns)
        self.assertAlmostEqual(result.loc[0, 'apr_eir_spread'], 0.01)
    
    def test_enrich_pricing_preserves_original_data(self):
        """Test that original DataFrame is not modified"""
        loan_df = pd.DataFrame({
            'loan_id': [1, 2],
            'APR': [0.05, 0.06],
            'EIR': [0.04, 0.05]
        })
        
        original_columns = set(loan_df.columns)
        result = enrich_pricing(loan_df, autoload=False)
        
        # Original DataFrame should not be modified
        self.assertEqual(set(loan_df.columns), original_columns)
        # Result should have additional columns
        self.assertTrue(len(result.columns) >= len(loan_df.columns))


class TestPricingDataLoading(unittest.TestCase):
    """Test cases for pricing data loading"""
    
    def setUp(self):
        """Set up temporary test files"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test pricing grid CSV
        self.pricing_grid_path = os.path.join(self.temp_dir, 'pricing_grid.csv')
        pricing_grid_df = pd.DataFrame({
            'tenor_min': [0, 120],
            'tenor_max': [120, 365],
            'rate': [0.05, 0.06]
        })
        pricing_grid_df.to_csv(self.pricing_grid_path, index=False)
        
        # Create test recommended pricing CSV
        self.recommended_pricing_path = os.path.join(self.temp_dir, 'recommended_pricing.csv')
        recommended_df = pd.DataFrame({
            'product': ['A', 'B'],
            'recommended_rate': [0.045, 0.055]
        })
        recommended_df.to_csv(self.recommended_pricing_path, index=False)
    
    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_load_pricing_data_from_paths(self):
        """Test loading pricing data from specified paths"""
        enricher = PricingEnricher(pricing_paths=[
            self.pricing_grid_path,
            self.recommended_pricing_path
        ])
        
        enricher.load_pricing_data()
        
        self.assertIsNotNone(enricher.pricing_grid)
        self.assertIsNotNone(enricher.recommended_pricing)
        self.assertEqual(len(enricher.pricing_grid), 2)
        self.assertEqual(len(enricher.recommended_pricing), 2)


if __name__ == '__main__':
    unittest.main()
