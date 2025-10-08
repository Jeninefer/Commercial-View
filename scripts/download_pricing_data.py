"""CLI utility for refreshing the local pricing dataset from Google Drive."""

from __future__ import annotations

import argparse
import logging
import shutil
import tempfile
from pathlib import Path
import os
from zipfile import ZipFile
from zipfile import ZipFile
from src.data_loader import PRICING_FILENAMES


LOGGER = logging.getLogger("download_pricing_data")
DEFAULT_FOLDER_ID = os.environ.get("PRICING_GDRIVE_FOLDER_ID", "1qIg_BnIf_IWYcWqCuvLaYU_Gu4C2-Dj8")
DEFAULT_DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "pricing"


Downloader = Callable[[str, Path], Sequence[Path]]


def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s:%(name)s:%(message)s")


def _ensure_pricing_directory(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    if resolved.exists() and not resolved.is_dir():
        raise NotADirectoryError(f"Expected '{resolved}' to be a directory.")

    default_dir = DEFAULT_DATA_DIR.resolve()
    if resolved != default_dir and resolved.name != "pricing":
        raise ValueError(
            f"Safety check failed: expected a directory named 'pricing', received '{resolved.name}'."
        )

    if not resolved.exists():
        LOGGER.info("Creating pricing directory at %s", resolved)
        resolved.mkdir(parents=True, exist_ok=True)

    return resolved


def _clear_directory(directory: Path) -> None:
    for item in directory.iterdir():
        if item.is_dir():
            LOGGER.debug("Removing directory %s", item)
            shutil.rmtree(item)
        else:
            LOGGER.debug("Removing file %s", item)
            item.unlink()


def _extract_archives(artifacts: Iterable[Path], destination: Path) -> list[Path]:
    extracted: list[Path] = []
    for artifact in artifacts:
        if artifact.suffix.lower() == ".zip":
            LOGGER.info("Extracting archive %s", artifact)
            with ZipFile(artifact) as archive:
                archive.extractall(destination)
            extracted.extend(path for path in destination.glob("**/*") if path.is_file())
    return extracted


def _gdown_downloader(folder_id: str, destination: Path) -> Sequence[Path]:
    LOGGER.info("Downloading pricing bundle from Google Drive folder %s", folder_id)
    try:
        import gdown
    except ImportError as exc:  # pragma: no cover - explicit error path
        raise RuntimeError(
            "gdown is required for downloading pricing data. Install it with 'pip install gdown'."
        ) from exc

    downloaded = gdown.download_folder(
        id=folder_id,
        output=str(destination),
        quiet=False,
        use_cookies=False,
    )

    if downloaded is None:
        msg = (
            f"Failed to download folder with id '{folder_id}' to '{destination}'. "
            "This may be due to network connectivity issues, an invalid folder ID, or insufficient permissions. "
            "Please check your internet connection, verify the folder ID, and ensure you have access to the folder."
        )
        LOGGER.error(msg)
        raise RuntimeError(msg)
    return [Path(p) for p in downloaded]


def _collect_csv_sources(temp_dir: Path) -> dict[str, Path]:
    csv_files = {path.name: path for path in temp_dir.glob("**/*.csv")}
    return csv_files


def sync_pricing_data(
    *,
    folder_id: str = DEFAULT_FOLDER_ID,
    data_dir: Optional[Path] = None,
    downloader: Optional[Downloader] = None,
) -> None:
    """Download the pricing dataset and refresh ``data/pricing``.

    Parameters
    ----------
    folder_id:
        Google Drive folder identifier containing the CSV bundle.
    data_dir:
        Target directory for pricing CSV files. Defaults to ``data/pricing``.
    downloader:
        Optional callable that performs the download. Injected in tests.
    """

    target_dir = _ensure_pricing_directory(data_dir or DEFAULT_DATA_DIR)
    LOGGER.info("Refreshing pricing data in %s", target_dir)
    _clear_directory(target_dir)

    downloader = downloader or _gdown_downloader

    with tempfile.TemporaryDirectory(prefix="pricing_download_") as tmp:
        temp_dir = Path(tmp)
        downloaded_artifacts = downloader(folder_id, temp_dir)
        LOGGER.debug("Downloader returned %d artifacts", len(downloaded_artifacts))

        # Some distributions provide a zipped bundle; extract archives eagerly.
        extracted_artifacts = _extract_archives(downloaded_artifacts, temp_dir)
        if extracted_artifacts:
            LOGGER.debug("Extracted %d files from archives", len(extracted_artifacts))

        csv_sources = _collect_csv_sources(temp_dir)
        missing = [name for name in PRICING_FILENAMES.values() if name not in csv_sources]
        if missing:
            raise FileNotFoundError(
                "The downloaded bundle is missing required files: "
                + ", ".join(missing)
                + ". Found files: "
                + ", ".join(sorted(csv_sources.keys()))
            )

        for logical_name, filename in PRICING_FILENAMES.items():
            source = csv_sources[filename]
            destination = target_dir / filename
            LOGGER.info("Updating %s from %s", logical_name, source)
            shutil.copy2(source, destination)

    LOGGER.info("Pricing data refresh completed successfully.")


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--folder-id",
        default=DEFAULT_FOLDER_ID,
        help="Google Drive folder ID to download from (defaults to the production folder).",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DEFAULT_DATA_DIR,
        help="Target directory for pricing CSV files (defaults to data/pricing).",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging for troubleshooting.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)
    _configure_logging(args.verbose)
    sync_pricing_data(folder_id=args.folder_id, data_dir=args.data_dir)


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
