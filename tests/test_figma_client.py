import sys
import types
from unittest.mock import Mock
from pathlib import Path

ROOT_DIR = str(Path(__file__).parent.parent.resolve())
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

sys.modules.setdefault("requests", types.SimpleNamespace(get=None))
from src import figma_client


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
