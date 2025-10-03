"""
Tests for the Calculator class safe_division method
"""

import unittest
import numpy as np
import pandas as pd
from commercial_view import Calculator


class TestSafeDivision(unittest.TestCase):
    """Test cases for the safe_division method"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.calc = Calculator()
    
    def test_scalar_division_normal(self):
        """Test normal scalar division"""
        result = self.calc.safe_division(10, 2)
        self.assertEqual(result, 5.0)
        
    def test_scalar_division_by_zero(self):
        """Test scalar division by zero returns default"""
        result = self.calc.safe_division(10, 0)
        self.assertTrue(np.isnan(result))
        
    def test_scalar_division_by_zero_with_custom_default(self):
        """Test scalar division by zero with custom default"""
        result = self.calc.safe_division(10, 0, default=0)
        self.assertEqual(result, 0)
        
    def test_series_division_normal(self):
        """Test normal Series division"""
        num = pd.Series([10, 20, 30])
        den = pd.Series([2, 4, 5])
        result = self.calc.safe_division(num, den)
        expected = pd.Series([5.0, 5.0, 6.0])
        pd.testing.assert_series_equal(result, expected)
        
    def test_series_division_with_zero(self):
        """Test Series division with zeros"""
        num = pd.Series([10, 20, 30])
        den = pd.Series([2, 0, 5])
        result = self.calc.safe_division(num, den)
        self.assertEqual(result[0], 5.0)
        self.assertTrue(np.isnan(result[1]))
        self.assertEqual(result[2], 6.0)
        
    def test_series_division_with_custom_default(self):
        """Test Series division with custom default"""
        num = pd.Series([10, 20, 30])
        den = pd.Series([2, 0, 5])
        result = self.calc.safe_division(num, den, default=0)
        expected = pd.Series([5.0, 0.0, 6.0])
        pd.testing.assert_series_equal(result, expected)
        
    def test_array_division_normal(self):
        """Test normal array division"""
        num = np.array([10, 20, 30])
        den = np.array([2, 4, 5])
        result = self.calc.safe_division(num, den)
        expected = np.array([5.0, 5.0, 6.0])
        np.testing.assert_array_equal(result, expected)
        
    def test_array_division_with_zero(self):
        """Test array division with zeros"""
        num = np.array([10, 20, 30])
        den = np.array([2, 0, 5])
        result = self.calc.safe_division(num, den)
        self.assertEqual(result[0], 5.0)
        self.assertTrue(np.isnan(result[1]))
        self.assertEqual(result[2], 6.0)
        
    def test_array_division_with_custom_default(self):
        """Test array division with custom default"""
        num = np.array([10, 20, 30])
        den = np.array([2, 0, 5])
        result = self.calc.safe_division(num, den, default=-1)
        expected = np.array([5.0, -1.0, 6.0])
        np.testing.assert_array_equal(result, expected)
        
    def test_series_index_preserved(self):
        """Test that Series index is preserved"""
        num = pd.Series([10, 20, 30], index=['a', 'b', 'c'])
        den = pd.Series([2, 4, 5], index=['a', 'b', 'c'])
        result = self.calc.safe_division(num, den)
        self.assertTrue(result.index.equals(num.index))
        
    def test_mixed_numeric_strings_in_series(self):
        """Test that non-numeric values are coerced to NaN"""
        num = pd.Series([10, 'abc', 30])
        den = pd.Series([2, 4, 5])
        result = self.calc.safe_division(num, den)
        self.assertEqual(result[0], 5.0)
        self.assertTrue(np.isnan(result[1]))
        self.assertEqual(result[2], 6.0)
        
    def test_inf_handling(self):
        """Test that infinite values are replaced with default"""
        num = pd.Series([10, 20, 30])
        den = pd.Series([2, 0, 5])
        result = self.calc.safe_division(num, den, default=999)
        self.assertEqual(result[0], 5.0)
        self.assertEqual(result[1], 999)
        self.assertEqual(result[2], 6.0)
        
    def test_negative_numbers(self):
        """Test division with negative numbers"""
        result = self.calc.safe_division(-10, 2)
        self.assertEqual(result, -5.0)
        
        num = pd.Series([-10, 20, -30])
        den = pd.Series([2, -4, 5])
        result = self.calc.safe_division(num, den)
        expected = pd.Series([-5.0, -5.0, -6.0])
        pd.testing.assert_series_equal(result, expected)
        
    def test_float_division(self):
        """Test division with float numbers"""
        result = self.calc.safe_division(10.5, 2.5)
        self.assertAlmostEqual(result, 4.2, places=10)
        

if __name__ == '__main__':
    unittest.main()
