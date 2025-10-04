from typing import Any, Dict

import pytest

from src.figma_client import FIGMA_API_BASE_URL, get_figma_file


class DummyResponse:
    def __init__(self, payload: Dict[str, Any]):
        self._payload = payload
        self.raise_called = False

    def raise_for_status(self) -> None:
        self.raise_called = True

    def json(self) -> Dict[str, Any]:
        return self._payload


def test_get_figma_file_success(monkeypatch: pytest.MonkeyPatch) -> None:
    file_key = "abc123"
    expected_payload = {"document": {"id": "1"}}
    dummy_response = DummyResponse(expected_payload)

    def fake_get(url: str, headers: Dict[str, str]) -> DummyResponse:
        assert url == f"{FIGMA_API_BASE_URL}files/{file_key}"
        assert headers == {"X-Figma-Token": "test-token"}
        return dummy_response

    monkeypatch.setenv("FIGMA_TOKEN", "test-token")
    monkeypatch.setattr("src.figma_client.requests.get", fake_get)

    result = get_figma_file(file_key)

    assert dummy_response.raise_called is True
    assert result == expected_payload
