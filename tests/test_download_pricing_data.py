from __future__ import annotations

from pathlib import Path

import pytest

from scripts import download_pricing_data
from src import data_loader


def _stub_downloader(folder_id: str, destination: Path) -> list[Path]:
    created = []
    for filename in data_loader.PRICING_FILENAMES.values():
        file_path = destination / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text("dummy,data\n1,2\n")
        created.append(file_path)
    return created


def test_sync_pricing_data_replaces_directory(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    pricing_dir = tmp_path / "data" / "pricing"
    pricing_dir.mkdir(parents=True)

    legacy_file = pricing_dir / "legacy.csv"
    legacy_file.write_text("legacy")

    caplog.set_level("INFO")

    download_pricing_data.sync_pricing_data(
        folder_id="dummy",
        data_dir=pricing_dir,
        downloader=_stub_downloader,
    )

    assert not legacy_file.exists(), "Legacy files should be removed during refresh."

    for filename in data_loader.PRICING_FILENAMES.values():
        assert (pricing_dir / filename).exists()

    assert "Pricing data refresh completed successfully." in caplog.text
