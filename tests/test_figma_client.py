import sys
import types
from pathlib import Path
from unittest.mock import Mock

sys.modules.setdefault("requests", types.SimpleNamespace(get=None))
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

import figma_client


def test_get_figma_file_success(monkeypatch):
    sample_payload = {"document": {"id": "123"}}
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_response.json.return_value = sample_payload

    monkeypatch.setenv("FIGMA_TOKEN", "test-token")
    monkeypatch.setattr(figma_client.requests, "get", Mock(return_value=mock_response))

    result = figma_client.get_figma_file("file-key")

    assert result == sample_payload
    mock_response.raise_for_status.assert_called_once()
    mock_response.json.assert_called_once()
