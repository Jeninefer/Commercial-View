"""
Production data refresh script
Downloads and processes real CSV files only
"""

import sys
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data_loader import ProductionDataLoader
from configs.production_config import ProductionConfig

logger = logging.getLogger(__name__)


def refresh_production_data():
    """Refresh production data from Google Drive"""

    logger.info("Starting production data refresh...")

    # Initialize production data loader
    loader = ProductionDataLoader()

    # Download fresh data from Google Drive
    download_results = loader.download_production_data()

    if not any(download_results.values()):
        logger.error("❌ No production data could be downloaded")
        return False

    # Load and validate datasets
    datasets = loader.load_production_datasets()
    validation = loader.validate_production_data(datasets)

    # Report results
    logger.info(f"✅ Downloaded {len(datasets)} production datasets")

    for name, df in datasets.items():
        logger.info(f"  - {name}: {len(df):,} records")

    if validation["validation_passed"]:
        logger.info("✅ All production data validation passed")
    else:
        logger.warning("⚠️  Data validation issues:")
        for issue in validation["issues"]:
            logger.warning(f"    - {issue}")

    return True


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    success = refresh_production_data()

    if success:
        print("✅ Production data refresh completed successfully")
    else:
        print("❌ Production data refresh failed")
        sys.exit(1)
