"""Test suite for JSON-safe conversion of pandas/numpy types."""

import pytest
import pandas as pd
import numpy as np
import json
from run import _to_json_safe


class TestJSONSafeConversion:
    """Test class for JSON-safe conversion functionality."""
    
    def test_json_safe_with_numpy_int64(self):
        """Test conversion of numpy int64 to native Python int."""
        df = pd.DataFrame({
            'col1': [np.int64(1), np.int64(2), np.int64(3)]
        })
        result = _to_json_safe(df)
        
        assert len(result) == 3
        assert all(isinstance(r['col1'], int) for r in result)
        
        # Verify JSON serialization works
        json_str = json.dumps(result)
        assert json_str is not None
    
    def test_json_safe_with_numpy_float64(self):
        """Test conversion of numpy float64 to native Python float."""
        df = pd.DataFrame({
            'col1': [np.float64(1.5), np.float64(2.5), np.float64(3.5)]
        })
        result = _to_json_safe(df)
        
        assert len(result) == 3
        assert all(isinstance(r['col1'], float) for r in result)
        
        # Verify JSON serialization works
        json_str = json.dumps(result)
        assert json_str is not None
    
    def test_json_safe_with_timestamps(self):
        """Test conversion of pandas Timestamp to ISO string."""
        df = pd.DataFrame({
            'date_col': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03'])
        })
        result = _to_json_safe(df)
        
        assert len(result) == 3
        assert all(isinstance(r['date_col'], str) for r in result)
        assert '2024-01-01' in result[0]['date_col']
        
        # Verify JSON serialization works
        json_str = json.dumps(result)
        assert json_str is not None
    
    def test_json_safe_with_nan(self):
        """Test conversion of NaN to None (null in JSON)."""
        df = pd.DataFrame({
            'col1': [1.0, np.nan, 3.0]
        })
        result = _to_json_safe(df)
        
        assert len(result) == 3
        assert result[0]['col1'] == 1.0
        assert result[1]['col1'] is None
        assert result[2]['col1'] == 3.0
        
        # Verify JSON serialization works
        json_str = json.dumps(result)
        assert json_str is not None
        assert 'null' in json_str
    
    def test_json_safe_with_nat(self):
        """Test conversion of NaT (Not a Time) to None."""
        df = pd.DataFrame({
            'date_col': [pd.Timestamp('2024-01-01'), pd.NaT, pd.Timestamp('2024-01-03')]
        })
        result = _to_json_safe(df)
        
        assert len(result) == 3
        assert isinstance(result[0]['date_col'], str)
        assert result[1]['date_col'] is None
        assert isinstance(result[2]['date_col'], str)
        
        # Verify JSON serialization works
        json_str = json.dumps(result)
        assert json_str is not None
    
    def test_json_safe_with_mixed_types(self):
        """Test conversion with various pandas/numpy types in one DataFrame."""
        df = pd.DataFrame({
            'int_col': [np.int64(1), np.int64(2)],
            'float_col': [np.float64(1.5), np.float64(2.5)],
            'date_col': pd.to_datetime(['2024-01-01', '2024-01-02']),
            'str_col': ['A', 'B'],
            'nan_col': [1.0, np.nan],
            'nat_col': [pd.Timestamp('2024-01-01'), pd.NaT]
        })
        result = _to_json_safe(df)
        
        assert len(result) == 2
        
        # Verify all types are JSON-safe
        json_str = json.dumps(result)
        assert json_str is not None
        
        # Verify types
        assert isinstance(result[0]['int_col'], int)
        assert isinstance(result[0]['float_col'], float)
        assert isinstance(result[0]['date_col'], str)
        assert isinstance(result[0]['str_col'], str)
        assert result[1]['nan_col'] is None
        assert result[1]['nat_col'] is None
    
    def test_json_safe_with_empty_dataframe(self):
        """Test conversion with empty DataFrame."""
        df = pd.DataFrame()
        result = _to_json_safe(df)
        
        assert result == []
        
        # Verify JSON serialization works
        json_str = json.dumps(result)
        assert json_str == '[]'
    
    def test_json_safe_with_none_dataframe(self):
        """Test conversion with None DataFrame."""
        result = _to_json_safe(None)
        
        assert result == []
        
        # Verify JSON serialization works
        json_str = json.dumps(result)
        assert json_str == '[]'
