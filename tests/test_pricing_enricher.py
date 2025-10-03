"""
Tests for the Pricing Enricher module
"""

import os
import sys
import unittest
import tempfile
import shutil
import pandas as pd
import numpy as np
import yaml
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pricing_enricher import PricingEnricher, _load_any


class TestLoadAny(unittest.TestCase):
    """Tests for the _load_any helper function"""
    
    def setUp(self):
        """Create temporary directory for test files"""
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.test_dir)
    
    def test_load_csv(self):
        """Test loading CSV files"""
        csv_path = os.path.join(self.test_dir, "test.csv")
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        df.to_csv(csv_path, index=False)
        
        loaded = _load_any(csv_path)
        pd.testing.assert_frame_equal(loaded, df)
    
    def test_load_json(self):
        """Test loading JSON files"""
        json_path = os.path.join(self.test_dir, "test.json")
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        df.to_json(json_path, orient="records")
        
        loaded = _load_any(json_path)
        pd.testing.assert_frame_equal(loaded, df)
    
    def test_load_parquet(self):
        """Test loading Parquet files"""
        parquet_path = os.path.join(self.test_dir, "test.parquet")
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        df.to_parquet(parquet_path, index=False)
        
        loaded = _load_any(parquet_path)
        pd.testing.assert_frame_equal(loaded, df)
    
    def test_load_yaml_with_pricing_grid(self):
        """Test loading YAML files with pricing_grid key"""
        yaml_path = os.path.join(self.test_dir, "test.yaml")
        data = {"pricing_grid": [{"a": 1, "b": 4}, {"a": 2, "b": 5}, {"a": 3, "b": 6}]}
        with open(yaml_path, "w") as f:
            yaml.dump(data, f)
        
        loaded = _load_any(yaml_path)
        expected = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        pd.testing.assert_frame_equal(loaded, expected)
    
    def test_load_yaml_with_recommended_pricing(self):
        """Test loading YAML files with recommended_pricing key"""
        yaml_path = os.path.join(self.test_dir, "test.yml")
        data = {"recommended_pricing": [{"a": 1, "b": 4}, {"a": 2, "b": 5}]}
        with open(yaml_path, "w") as f:
            yaml.dump(data, f)
        
        loaded = _load_any(yaml_path)
        expected = pd.DataFrame({"a": [1, 2], "b": [4, 5]})
        pd.testing.assert_frame_equal(loaded, expected)
    
    def test_load_yaml_direct_data(self):
        """Test loading YAML files with direct data (no special keys)"""
        yaml_path = os.path.join(self.test_dir, "test.yaml")
        data = [{"a": 1, "b": 4}, {"a": 2, "b": 5}]
        with open(yaml_path, "w") as f:
            yaml.dump(data, f)
        
        loaded = _load_any(yaml_path)
        expected = pd.DataFrame({"a": [1, 2], "b": [4, 5]})
        pd.testing.assert_frame_equal(loaded, expected)
    
    def test_unsupported_extension(self):
        """Test that unsupported file types raise ValueError"""
        with self.assertRaises(ValueError) as ctx:
            _load_any("/path/to/file.txt")
        self.assertIn("Unsupported file type", str(ctx.exception))


class TestPricingEnricher(unittest.TestCase):
    """Tests for the PricingEnricher class"""
    
    def setUp(self):
        """Create temporary directory for test files"""
        self.test_dir = tempfile.mkdtemp()
        self.pricing_dir = os.path.join(self.test_dir, "pricing")
        os.makedirs(self.pricing_dir)
        
    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.test_dir)
    
    def test_init_default_paths(self):
        """Test initialization with default paths"""
        enricher = PricingEnricher()
        self.assertEqual(enricher.pricing_paths, PricingEnricher.DEFAULT_PRICING_PATHS)
        self.assertIsNone(enricher.pricing_grid)
        self.assertIsNone(enricher.recommended_pricing)
    
    def test_init_custom_paths(self):
        """Test initialization with custom paths"""
        custom_paths = ["/path/1", "/path/2"]
        enricher = PricingEnricher(pricing_paths=custom_paths)
        self.assertEqual(enricher.pricing_paths, custom_paths)
    
    def test_find_pricing_files_empty_directory(self):
        """Test finding pricing files in empty directory"""
        enricher = PricingEnricher(pricing_paths=[self.pricing_dir])
        files = enricher.find_pricing_files()
        self.assertEqual(files, {})
    
    def test_find_pricing_files_grid(self):
        """Test finding pricing grid files"""
        grid_path = os.path.join(self.pricing_dir, "pricing_grid.csv")
        pd.DataFrame({"a": [1, 2]}).to_csv(grid_path, index=False)
        
        enricher = PricingEnricher(pricing_paths=[self.pricing_dir])
        files = enricher.find_pricing_files()
        
        self.assertIn("pricing_grid", files)
        self.assertEqual(files["pricing_grid"], grid_path)
    
    def test_find_pricing_files_recommended(self):
        """Test finding recommended pricing files"""
        rec_path = os.path.join(self.pricing_dir, "recommended_pricing.csv")
        pd.DataFrame({"a": [1, 2]}).to_csv(rec_path, index=False)
        
        enricher = PricingEnricher(pricing_paths=[self.pricing_dir])
        files = enricher.find_pricing_files()
        
        self.assertIn("recommended_pricing", files)
        self.assertEqual(files["recommended_pricing"], rec_path)
    
    def test_find_pricing_files_classification(self):
        """Test file classification by name patterns"""
        # Create files with different patterns
        files_to_create = {
            "recommend_rates.csv": "recommended_pricing",
            "pricing_matrix.json": "recommended_pricing",
            "price_list.csv": "pricing_grid",
            "grid_data.parquet": "pricing_grid",
        }
        
        for filename, expected_type in files_to_create.items():
            path = os.path.join(self.pricing_dir, filename)
            pd.DataFrame({"a": [1]}).to_csv(path, index=False)
        
        enricher = PricingEnricher(pricing_paths=[self.pricing_dir])
        files = enricher.find_pricing_files()
        
        # Should find at least one of each type
        self.assertIn("pricing_grid", files)
        self.assertIn("recommended_pricing", files)
    
    def test_load_pricing_data_success(self):
        """Test successful loading of pricing data"""
        grid_path = os.path.join(self.pricing_dir, "pricing_grid.csv")
        rec_path = os.path.join(self.pricing_dir, "recommended_pricing.csv")
        
        grid_df = pd.DataFrame({"country": ["US", "UK"], "rate": [0.05, 0.06]})
        rec_df = pd.DataFrame({"country": ["US", "UK"], "rate": [0.04, 0.045]})
        
        grid_df.to_csv(grid_path, index=False)
        rec_df.to_csv(rec_path, index=False)
        
        enricher = PricingEnricher(pricing_paths=[self.pricing_dir])
        result = enricher.load_pricing_data()
        
        self.assertTrue(result)
        self.assertIsNotNone(enricher.pricing_grid)
        self.assertIsNotNone(enricher.recommended_pricing)
        pd.testing.assert_frame_equal(enricher.pricing_grid, grid_df)
        pd.testing.assert_frame_equal(enricher.recommended_pricing, rec_df)
    
    def test_load_pricing_data_no_files(self):
        """Test loading when no pricing files are found"""
        enricher = PricingEnricher(pricing_paths=[self.pricing_dir])
        result = enricher.load_pricing_data()
        
        self.assertFalse(result)
    
    def test_detect_join_keys_exact_match(self):
        """Test detecting join keys with exact column name matches"""
        loan_df = pd.DataFrame({
            "country": ["US", "UK"],
            "sector": ["tech", "finance"],
            "amount": [1000, 2000]
        })
        
        pricing_df = pd.DataFrame({
            "country": ["US", "UK"],
            "sector": ["tech", "finance"],
            "rate": [0.05, 0.06]
        })
        
        enricher = PricingEnricher()
        loan_keys, pricing_keys = enricher.detect_join_keys(loan_df, pricing_df)
        
        self.assertEqual(loan_keys, ["country", "sector"])
        self.assertEqual(pricing_keys, ["country", "sector"])
    
    def test_detect_join_keys_case_insensitive(self):
        """Test detecting join keys with case-insensitive matching"""
        loan_df = pd.DataFrame({
            "country": ["US"],
            "segment": ["retail"]
        })
        
        pricing_df = pd.DataFrame({
            "COUNTRY": ["US"],
            "SEGMENT": ["retail"]
        })
        
        enricher = PricingEnricher()
        loan_keys, pricing_keys = enricher.detect_join_keys(loan_df, pricing_df)
        
        self.assertEqual(loan_keys, ["country", "segment"])
        self.assertEqual(pricing_keys, ["COUNTRY", "SEGMENT"])
    
    def test_detect_join_keys_alias_mapping(self):
        """Test detecting join keys with aliased column names"""
        loan_df = pd.DataFrame({
            "client_segment": ["retail"],
            "loan_amount": [1000]
        })
        
        pricing_df = pd.DataFrame({
            "segment": ["retail"],
            "amount": [1000]
        })
        
        enricher = PricingEnricher()
        loan_keys, pricing_keys = enricher.detect_join_keys(loan_df, pricing_df)
        
        self.assertIn("client_segment", loan_keys)
        self.assertIn("segment", pricing_keys)
    
    def test_enrich_loan_data_exact_join(self):
        """Test enriching loan data with exact joins"""
        loan_df = pd.DataFrame({
            "loan_id": [1, 2, 3],
            "country": ["US", "UK", "US"],
            "sector": ["tech", "finance", "retail"]
        })
        
        pricing_df = pd.DataFrame({
            "country": ["US", "UK"],
            "sector": ["tech", "finance"],
            "recommended_rate": [0.05, 0.06]
        })
        
        enricher = PricingEnricher(pricing_paths=[self.pricing_dir])
        enricher.recommended_pricing = pricing_df
        
        result = enricher.enrich_loan_data(
            loan_df,
            join_keys=["country", "sector"]
        )
        
        self.assertIn("recommended_rate", result.columns)
        self.assertIn("has_pricing", result.columns)
        self.assertEqual(result.loc[0, "recommended_rate"], 0.05)
        self.assertEqual(result.loc[1, "recommended_rate"], 0.06)
        self.assertTrue(pd.isna(result.loc[2, "recommended_rate"]))
    
    def test_enrich_loan_data_with_bands(self):
        """Test enriching loan data with band matching"""
        loan_df = pd.DataFrame({
            "loan_id": [1, 2, 3],
            "tenor_days": [30, 90, 180],
            "ticket_usd": [1000, 5000, 10000]
        })
        
        pricing_grid = pd.DataFrame({
            "tenor_min": [0, 60, 120],
            "tenor_max": [60, 120, 365],
            "ticket_min": [0, 2500, 7500],
            "ticket_max": [2500, 7500, 15000],
            "recommended_rate": [0.05, 0.06, 0.07]
        })
        
        enricher = PricingEnricher(pricing_paths=[self.pricing_dir])
        enricher.pricing_grid = pricing_grid
        
        result = enricher.enrich_loan_data(
            loan_df,
            band_keys={
                "tenor_days": ("tenor_min", "tenor_max"),
                "ticket_usd": ("ticket_min", "ticket_max")
            }
        )
        
        self.assertIn("recommended_rate", result.columns)
        # First loan: tenor 30 (0-60), ticket 1000 (0-2500) -> rate 0.05
        self.assertEqual(result.loc[0, "recommended_rate"], 0.05)
    
    def test_enrich_loan_data_apr_eir_spread(self):
        """Test APR-EIR spread calculation"""
        loan_df = pd.DataFrame({
            "loan_id": [1, 2],
            "apr": [0.10, 0.15],
            "eir": [0.08, 0.12]
        })
        
        enricher = PricingEnricher()
        result = enricher.enrich_loan_data(loan_df)
        
        self.assertIn("apr_eir_spread", result.columns)
        self.assertAlmostEqual(result.loc[0, "apr_eir_spread"], 0.02, places=5)
        self.assertAlmostEqual(result.loc[1, "apr_eir_spread"], 0.03, places=5)
    
    def test_enrich_loan_data_has_pricing_flag(self):
        """Test that has_pricing flag is set correctly"""
        loan_df = pd.DataFrame({
            "loan_id": [1, 2],
            "country": ["US", "UK"]
        })
        
        pricing_df = pd.DataFrame({
            "country": ["US"],
            "recommended_rate": [0.05]
        })
        
        enricher = PricingEnricher()
        enricher.recommended_pricing = pricing_df
        
        result = enricher.enrich_loan_data(
            loan_df,
            join_keys=["country"]
        )
        
        self.assertIn("has_pricing", result.columns)
        self.assertTrue(result.loc[0, "has_pricing"])
        self.assertFalse(result.loc[1, "has_pricing"])
    
    def test_enrich_loan_data_no_pricing_available(self):
        """Test enrichment when no pricing data is available"""
        loan_df = pd.DataFrame({
            "loan_id": [1, 2],
            "country": ["US", "UK"]
        })
        
        enricher = PricingEnricher(pricing_paths=[self.pricing_dir])
        result = enricher.enrich_loan_data(loan_df)
        
        # Should return original dataframe unchanged (except has_pricing)
        self.assertEqual(len(result), len(loan_df))
        self.assertIn("loan_id", result.columns)
        self.assertIn("country", result.columns)


class TestIntegration(unittest.TestCase):
    """Integration tests for complete workflows"""
    
    def setUp(self):
        """Create temporary directory structure"""
        self.test_dir = tempfile.mkdtemp()
        self.pricing_dir = os.path.join(self.test_dir, "pricing")
        os.makedirs(self.pricing_dir)
        
    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.test_dir)
    
    def test_full_workflow(self):
        """Test complete workflow from file discovery to enrichment"""
        # Create pricing files
        grid_path = os.path.join(self.pricing_dir, "pricing_grid.csv")
        rec_path = os.path.join(self.pricing_dir, "recommended_pricing.csv")
        
        grid_df = pd.DataFrame({
            "country": ["US", "UK", "DE"],
            "sector": ["tech", "finance", "retail"],
            "recommended_rate": [0.05, 0.06, 0.055]
        })
        
        rec_df = pd.DataFrame({
            "country": ["US"],
            "sector": ["tech"],
            "recommended_rate": [0.045]
        })
        
        grid_df.to_csv(grid_path, index=False)
        rec_df.to_csv(rec_path, index=False)
        
        # Create loan data
        loan_df = pd.DataFrame({
            "loan_id": [1, 2, 3],
            "country": ["US", "UK", "FR"],
            "sector": ["tech", "finance", "tech"]
        })
        
        # Run full workflow
        enricher = PricingEnricher(pricing_paths=[self.pricing_dir])
        files = enricher.find_pricing_files()
        
        self.assertEqual(len(files), 2)
        
        loaded = enricher.load_pricing_data(files)
        self.assertTrue(loaded)
        
        result = enricher.enrich_loan_data(
            loan_df,
            join_keys=["country", "sector"]
        )
        
        # Verify enrichment
        self.assertIn("recommended_rate", result.columns)
        self.assertIn("has_pricing", result.columns)
        
        # US/tech should get recommended pricing (0.045)
        self.assertEqual(result.loc[0, "recommended_rate"], 0.045)
        self.assertTrue(result.loc[0, "has_pricing"])
        
        # UK/finance should get grid pricing (0.06)
        self.assertEqual(result.loc[1, "recommended_rate"], 0.06)
        self.assertTrue(result.loc[1, "has_pricing"])
        
        # FR/tech has no pricing
        self.assertTrue(pd.isna(result.loc[2, "recommended_rate"]))
        self.assertFalse(result.loc[2, "has_pricing"])


if __name__ == "__main__":
    unittest.main()
