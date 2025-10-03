import unittest
import pandas as pd
import numpy as np
import os
import tempfile
import shutil
from pathlib import Path
import sys

# Add parent directory to path to import abaco_core
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from abaco_core.pricing import PricingEnricher


class TestPricingEnricher(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.exports_dir = os.path.join(self.test_dir, "exports")
        os.makedirs(self.exports_dir, exist_ok=True)
        
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_initialization_default_paths(self):
        """Test initialization with default paths"""
        enricher = PricingEnricher()
        self.assertEqual(enricher.pricing_paths, PricingEnricher.DEFAULT_PRICING_PATHS)
        self.assertIsNone(enricher.pricing_grid)
        self.assertIsNone(enricher.recommended_pricing)
    
    def test_initialization_custom_paths(self):
        """Test initialization with custom paths"""
        custom_paths = ["/custom/path1", "/custom/path2"]
        enricher = PricingEnricher(pricing_paths=custom_paths)
        self.assertEqual(enricher.pricing_paths, custom_paths)
    
    def test_find_pricing_files_empty(self):
        """Test finding pricing files when no files exist"""
        enricher = PricingEnricher(pricing_paths=[self.test_dir])
        found = enricher.find_pricing_files()
        self.assertEqual(found, {})
    
    def test_find_pricing_files_grid(self):
        """Test finding pricing grid file"""
        enricher = PricingEnricher(pricing_paths=[self.exports_dir])
        
        # Create a pricing grid CSV
        grid_file = os.path.join(self.exports_dir, "pricing_grid_2024.csv")
        pd.DataFrame({"segment": ["A", "B"], "rate": [0.05, 0.06]}).to_csv(grid_file, index=False)
        
        found = enricher.find_pricing_files()
        self.assertIn("pricing_grid", found)
        self.assertEqual(found["pricing_grid"], grid_file)
    
    def test_find_pricing_files_recommended(self):
        """Test finding recommended pricing file"""
        enricher = PricingEnricher(pricing_paths=[self.exports_dir])
        
        # Create a recommended pricing CSV
        rec_file = os.path.join(self.exports_dir, "recommended_pricing.csv")
        pd.DataFrame({"segment": ["A", "B"], "rate": [0.04, 0.05]}).to_csv(rec_file, index=False)
        
        found = enricher.find_pricing_files()
        self.assertIn("recommended_pricing", found)
        self.assertEqual(found["recommended_pricing"], rec_file)
    
    def test_find_pricing_files_both(self):
        """Test finding both pricing grid and recommended files"""
        enricher = PricingEnricher(pricing_paths=[self.exports_dir])
        
        # Create both files
        grid_file = os.path.join(self.exports_dir, "pricing_grid.csv")
        pd.DataFrame({"segment": ["A", "B"], "rate": [0.05, 0.06]}).to_csv(grid_file, index=False)
        
        rec_file = os.path.join(self.exports_dir, "pricing_recommendations.csv")
        pd.DataFrame({"segment": ["A", "B"], "rate": [0.04, 0.05]}).to_csv(rec_file, index=False)
        
        found = enricher.find_pricing_files()
        self.assertEqual(len(found), 2)
        self.assertIn("pricing_grid", found)
        self.assertIn("recommended_pricing", found)
    
    def test_find_pricing_files_ignores_non_csv(self):
        """Test that non-CSV files are ignored"""
        enricher = PricingEnricher(pricing_paths=[self.exports_dir])
        
        # Create non-CSV file
        txt_file = os.path.join(self.exports_dir, "pricing_grid.txt")
        with open(txt_file, 'w') as f:
            f.write("test")
        
        found = enricher.find_pricing_files()
        self.assertEqual(found, {})
    
    def test_load_pricing_data_no_files(self):
        """Test loading pricing data when no files exist"""
        enricher = PricingEnricher(pricing_paths=[self.test_dir])
        result = enricher.load_pricing_data()
        self.assertFalse(result)
        self.assertIsNone(enricher.pricing_grid)
        self.assertIsNone(enricher.recommended_pricing)
    
    def test_load_pricing_data_grid_only(self):
        """Test loading only pricing grid data"""
        enricher = PricingEnricher(pricing_paths=[self.exports_dir])
        
        # Create a pricing grid CSV
        grid_file = os.path.join(self.exports_dir, "pricing_grid.csv")
        df = pd.DataFrame({"segment": ["A", "B"], "rate": [0.05, 0.06]})
        df.to_csv(grid_file, index=False)
        
        result = enricher.load_pricing_data()
        self.assertTrue(result)
        self.assertIsNotNone(enricher.pricing_grid)
        self.assertIsNone(enricher.recommended_pricing)
        pd.testing.assert_frame_equal(enricher.pricing_grid, df)
    
    def test_load_pricing_data_recommended_only(self):
        """Test loading only recommended pricing data"""
        enricher = PricingEnricher(pricing_paths=[self.exports_dir])
        
        # Create a recommended pricing CSV
        rec_file = os.path.join(self.exports_dir, "recommended_pricing.csv")
        df = pd.DataFrame({"segment": ["A", "B"], "rate": [0.04, 0.05]})
        df.to_csv(rec_file, index=False)
        
        result = enricher.load_pricing_data()
        self.assertTrue(result)
        self.assertIsNone(enricher.pricing_grid)
        self.assertIsNotNone(enricher.recommended_pricing)
        pd.testing.assert_frame_equal(enricher.recommended_pricing, df)
    
    def test_load_pricing_data_both(self):
        """Test loading both pricing data types"""
        enricher = PricingEnricher(pricing_paths=[self.exports_dir])
        
        # Create both files
        grid_file = os.path.join(self.exports_dir, "pricing_grid.csv")
        grid_df = pd.DataFrame({"segment": ["A", "B"], "rate": [0.05, 0.06]})
        grid_df.to_csv(grid_file, index=False)
        
        rec_file = os.path.join(self.exports_dir, "recommended_pricing.csv")
        rec_df = pd.DataFrame({"segment": ["A", "B"], "rate": [0.04, 0.05]})
        rec_df.to_csv(rec_file, index=False)
        
        result = enricher.load_pricing_data()
        self.assertTrue(result)
        self.assertIsNotNone(enricher.pricing_grid)
        self.assertIsNotNone(enricher.recommended_pricing)
        pd.testing.assert_frame_equal(enricher.pricing_grid, grid_df)
        pd.testing.assert_frame_equal(enricher.recommended_pricing, rec_df)
    
    def test_load_pricing_data_with_explicit_files(self):
        """Test loading pricing data with explicit file paths"""
        enricher = PricingEnricher()
        
        # Create files
        grid_file = os.path.join(self.exports_dir, "custom_grid.csv")
        grid_df = pd.DataFrame({"segment": ["A", "B"], "rate": [0.05, 0.06]})
        grid_df.to_csv(grid_file, index=False)
        
        files = {"pricing_grid": grid_file}
        result = enricher.load_pricing_data(pricing_files=files)
        self.assertTrue(result)
        pd.testing.assert_frame_equal(enricher.pricing_grid, grid_df)
    
    def test_auto_join_keys_segment(self):
        """Test automatic join key detection for segment"""
        enricher = PricingEnricher()
        
        loan_df = pd.DataFrame({"client_segment": ["A", "B"], "amount": [1000, 2000]})
        pricing_df = pd.DataFrame({"segment": ["A", "B"], "rate": [0.05, 0.06]})
        
        loan_keys, price_keys = enricher._auto_join_keys(loan_df, pricing_df)
        self.assertEqual(loan_keys, ["client_segment"])
        self.assertEqual(price_keys, ["segment"])
    
    def test_auto_join_keys_multiple(self):
        """Test automatic join key detection with multiple keys"""
        enricher = PricingEnricher()
        
        loan_df = pd.DataFrame({
            "segment": ["A", "B"],
            "term": [12, 24],
            "amount": [1000, 2000]
        })
        pricing_df = pd.DataFrame({
            "segment": ["A", "B"],
            "term": [12, 24],
            "rate": [0.05, 0.06]
        })
        
        loan_keys, price_keys = enricher._auto_join_keys(loan_df, pricing_df)
        self.assertIn("segment", loan_keys)
        self.assertIn("term", loan_keys)
        self.assertIn("segment", price_keys)
        self.assertIn("term", price_keys)
    
    def test_auto_join_keys_no_match(self):
        """Test automatic join key detection with no matching keys"""
        enricher = PricingEnricher()
        
        loan_df = pd.DataFrame({"customer_id": [1, 2], "loan_id": [101, 102]})
        pricing_df = pd.DataFrame({"price_id": [1, 2], "rate": [0.05, 0.06]})
        
        loan_keys, price_keys = enricher._auto_join_keys(loan_df, pricing_df)
        self.assertEqual(loan_keys, [])
        self.assertEqual(price_keys, [])
    
    def test_enrich_loan_data_empty_df(self):
        """Test enrichment with empty dataframe"""
        enricher = PricingEnricher()
        loan_df = pd.DataFrame()
        result = enricher.enrich_loan_data(loan_df)
        self.assertTrue(result.empty)
    
    def test_enrich_loan_data_no_pricing(self):
        """Test enrichment with no pricing data available"""
        enricher = PricingEnricher(pricing_paths=[self.test_dir])
        loan_df = pd.DataFrame({"segment": ["A", "B"], "amount": [1000, 2000]})
        result = enricher.enrich_loan_data(loan_df, autoload=False)
        pd.testing.assert_frame_equal(result, loan_df)
    
    def test_enrich_loan_data_with_recommended_pricing(self):
        """Test enrichment with recommended pricing"""
        enricher = PricingEnricher(pricing_paths=[self.exports_dir])
        
        # Create recommended pricing file
        rec_file = os.path.join(self.exports_dir, "recommended_pricing.csv")
        rec_df = pd.DataFrame({
            "segment": ["A", "B"],
            "recommended_rate": [0.04, 0.05]
        })
        rec_df.to_csv(rec_file, index=False)
        
        enricher.load_pricing_data()
        
        loan_df = pd.DataFrame({"segment": ["A", "B"], "amount": [1000, 2000]})
        result = enricher.enrich_loan_data(loan_df, autoload=False)
        
        self.assertIn("recommended_rate", result.columns)
        self.assertEqual(result.loc[0, "recommended_rate"], 0.04)
        self.assertEqual(result.loc[1, "recommended_rate"], 0.05)
    
    def test_enrich_loan_data_with_grid(self):
        """Test enrichment with pricing grid"""
        enricher = PricingEnricher(pricing_paths=[self.exports_dir])
        
        # Create pricing grid file
        grid_file = os.path.join(self.exports_dir, "pricing_grid.csv")
        grid_df = pd.DataFrame({
            "segment": ["A", "B"],
            "grid_rate": [0.05, 0.06]
        })
        grid_df.to_csv(grid_file, index=False)
        
        enricher.load_pricing_data()
        
        loan_df = pd.DataFrame({"segment": ["A", "B"], "amount": [1000, 2000]})
        result = enricher.enrich_loan_data(loan_df, autoload=False)
        
        self.assertIn("grid_rate", result.columns)
        self.assertEqual(result.loc[0, "grid_rate"], 0.05)
        self.assertEqual(result.loc[1, "grid_rate"], 0.06)
    
    def test_enrich_loan_data_apr_eir_spread(self):
        """Test APR-EIR spread calculation"""
        enricher = PricingEnricher(pricing_paths=[self.test_dir])
        
        loan_df = pd.DataFrame({
            "segment": ["A", "B"],
            "APR": [0.08, 0.10],
            "EIR": [0.07, 0.08]
        })
        
        result = enricher.enrich_loan_data(loan_df, autoload=False)
        
        self.assertIn("apr_eir_spread", result.columns)
        self.assertAlmostEqual(result.loc[0, "apr_eir_spread"], 0.01)
        self.assertAlmostEqual(result.loc[1, "apr_eir_spread"], 0.02)
    
    def test_enrich_loan_data_with_explicit_join_keys(self):
        """Test enrichment with explicit join keys"""
        enricher = PricingEnricher(pricing_paths=[self.exports_dir])
        
        # Create pricing file
        rec_file = os.path.join(self.exports_dir, "recommended_pricing.csv")
        rec_df = pd.DataFrame({
            "cat": ["X", "Y"],
            "rate": [0.04, 0.05]
        })
        rec_df.to_csv(rec_file, index=False)
        
        enricher.load_pricing_data()
        
        loan_df = pd.DataFrame({
            "category": ["X", "Y"],
            "amount": [1000, 2000]
        })
        
        # Manual rename to match keys
        enricher.recommended_pricing = enricher.recommended_pricing.rename(columns={"cat": "category"})
        
        result = enricher.enrich_loan_data(loan_df, join_keys=["category"], autoload=False)
        
        self.assertIn("rate", result.columns)
        self.assertEqual(result.loc[0, "rate"], 0.04)
    
    def test_enrich_loan_data_autoload(self):
        """Test enrichment with autoload enabled"""
        enricher = PricingEnricher(pricing_paths=[self.exports_dir])
        
        # Create recommended pricing file
        rec_file = os.path.join(self.exports_dir, "recommended_pricing.csv")
        rec_df = pd.DataFrame({
            "segment": ["A", "B"],
            "rate": [0.04, 0.05]
        })
        rec_df.to_csv(rec_file, index=False)
        
        loan_df = pd.DataFrame({"segment": ["A", "B"], "amount": [1000, 2000]})
        result = enricher.enrich_loan_data(loan_df, autoload=True)
        
        self.assertIsNotNone(enricher.recommended_pricing)
        self.assertIn("rate", result.columns)
    
    def test_enrich_loan_data_with_band_keys(self):
        """Test enrichment with band keys for interval matching"""
        enricher = PricingEnricher(pricing_paths=[self.exports_dir])
        
        # Create pricing grid with ranges
        grid_file = os.path.join(self.exports_dir, "pricing_grid.csv")
        grid_df = pd.DataFrame({
            "amount_min": [0, 1000, 5000],
            "amount_max": [999, 4999, 10000],
            "rate": [0.08, 0.06, 0.04]
        })
        grid_df.to_csv(grid_file, index=False)
        
        enricher.load_pricing_data()
        
        loan_df = pd.DataFrame({
            "loan_amount": [500, 2000, 7000]
        })
        
        band_keys = {"loan_amount": ("amount_min", "amount_max")}
        result = enricher.enrich_loan_data(loan_df, band_keys=band_keys, autoload=False)
        
        # Check that interval matching worked
        self.assertIn("rate_grid", result.columns)
    
    def test_enrich_loan_data_preserves_original(self):
        """Test that enrichment preserves original dataframe"""
        enricher = PricingEnricher(pricing_paths=[self.test_dir])
        
        loan_df = pd.DataFrame({"segment": ["A", "B"], "amount": [1000, 2000]})
        original_df = loan_df.copy()
        
        result = enricher.enrich_loan_data(loan_df, autoload=False)
        
        # Original should be unchanged
        pd.testing.assert_frame_equal(loan_df, original_df)
        # Result should be a copy
        self.assertIsNot(result, loan_df)


if __name__ == '__main__':
    unittest.main()
