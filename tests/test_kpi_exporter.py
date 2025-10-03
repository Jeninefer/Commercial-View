"""Tests for KPI Exporter functionality."""

import json
import logging
import os
import tempfile
import time
from datetime import datetime
from unittest.mock import patch

import pytest

from src.kpi_exporter import KPIExporter


class TestKPIExporter:
    """Test suite for KPIExporter class."""

    def test_init_default_path(self):
        """Test initialization with default export path."""
        exporter = KPIExporter()
        assert exporter.export_path == "exports"

    def test_init_custom_path(self):
        """Test initialization with custom export path."""
        custom_path = "/custom/path"
        exporter = KPIExporter(export_path=custom_path)
        assert exporter.export_path == custom_path

    def test_export_json_creates_directory(self):
        """Test that _export_json creates the export directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            export_path = os.path.join(tmpdir, "test_exports")
            exporter = KPIExporter(export_path=export_path)
            
            payload = {"metric": "revenue", "value": 1000}
            result = exporter._export_json(payload, "test_kpi")
            
            assert os.path.exists(export_path)
            assert os.path.isdir(export_path)

    def test_export_json_file_created(self):
        """Test that _export_json creates a JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = KPIExporter(export_path=tmpdir)
            
            payload = {"metric": "sales", "value": 5000}
            result = exporter._export_json(payload, "test_kpi")
            
            assert os.path.exists(result)
            assert result.endswith(".json")

    def test_export_json_filename_format(self):
        """Test that _export_json creates files with correct naming format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = KPIExporter(export_path=tmpdir)
            
            payload = {"metric": "profit", "value": 2000}
            result = exporter._export_json(payload, "kpi_data")
            
            filename = os.path.basename(result)
            assert filename.startswith("kpi_data_")
            assert filename.endswith(".json")
            # Check timestamp format: kpi_data_YYYYMMDDTHHMMSSZ.json
            assert len(filename) == len("kpi_data_20231231T235959Z.json")

    def test_export_json_timestamp_format(self):
        """Test that _export_json uses correct timestamp format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = KPIExporter(export_path=tmpdir)
            
            # Mock datetime to get predictable timestamp
            mock_dt = datetime(2023, 12, 25, 10, 30, 45)
            with patch('src.kpi_exporter.datetime') as mock_datetime:
                mock_datetime.utcnow.return_value = mock_dt
                
                payload = {"metric": "test"}
                result = exporter._export_json(payload, "test")
                
                filename = os.path.basename(result)
                assert "20231225T103045Z" in filename

    def test_export_json_content(self):
        """Test that _export_json writes correct JSON content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = KPIExporter(export_path=tmpdir)
            
            payload = {
                "metric": "revenue",
                "value": 10000,
                "currency": "USD",
                "nested": {"key": "value"}
            }
            result = exporter._export_json(payload, "test_kpi")
            
            with open(result, "r") as f:
                loaded_data = json.load(f)
            
            assert loaded_data == payload

    def test_export_json_indentation(self):
        """Test that _export_json writes JSON with proper indentation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = KPIExporter(export_path=tmpdir)
            
            payload = {"key1": "value1", "key2": {"nested": "value"}}
            result = exporter._export_json(payload, "test")
            
            with open(result, "r") as f:
                content = f.read()
            
            # Check that content has proper indentation (2 spaces)
            assert '\n  "key1"' in content or '\n  "key2"' in content

    def test_export_json_default_str_serialization(self):
        """Test that _export_json uses default=str for non-serializable objects."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = KPIExporter(export_path=tmpdir)
            
            # Include a datetime object which is not JSON serializable by default
            payload = {
                "metric": "daily_sales",
                "timestamp": datetime(2023, 12, 25, 10, 30, 45)
            }
            result = exporter._export_json(payload, "test")
            
            with open(result, "r") as f:
                loaded_data = json.load(f)
            
            # datetime should be converted to string
            assert isinstance(loaded_data["timestamp"], str)
            assert "2023-12-25" in loaded_data["timestamp"]

    def test_export_json_returns_filepath(self):
        """Test that _export_json returns the full file path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = KPIExporter(export_path=tmpdir)
            
            payload = {"metric": "test"}
            result = exporter._export_json(payload, "test_kpi")
            
            assert isinstance(result, str)
            assert result.startswith(tmpdir)
            assert os.path.isabs(result)

    def test_export_json_logging(self, caplog):
        """Test that _export_json logs the export information."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = KPIExporter(export_path=tmpdir)
            
            with caplog.at_level(logging.INFO):
                payload = {"metric": "test"}
                result = exporter._export_json(payload, "test_kpi")
            
            assert any("KPIs exported:" in record.message for record in caplog.records)
            assert any(result in record.message for record in caplog.records)

    def test_export_json_multiple_exports(self):
        """Test that multiple exports create separate files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = KPIExporter(export_path=tmpdir)
            
            payload1 = {"metric": "test1"}
            payload2 = {"metric": "test2"}
            
            result1 = exporter._export_json(payload1, "kpi")
            time.sleep(1.1)  # Ensure different timestamps
            result2 = exporter._export_json(payload2, "kpi")
            
            assert result1 != result2
            assert os.path.exists(result1)
            assert os.path.exists(result2)

    def test_export_json_empty_payload(self):
        """Test that _export_json handles empty payload."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = KPIExporter(export_path=tmpdir)
            
            payload = {}
            result = exporter._export_json(payload, "empty_kpi")
            
            assert os.path.exists(result)
            with open(result, "r") as f:
                loaded_data = json.load(f)
            assert loaded_data == {}
