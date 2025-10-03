"""Data ingestion package for Commercial View Platform."""

from .csv_reader import CSVDataReader, load_sample_data

# Optional Google imports (require google-api packages)
try:
    from .google_drive import GoogleDriveClient, download_data_from_drive
    from .google_sheets import GoogleSheetsClient, read_google_sheet
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    GoogleDriveClient = None
    download_data_from_drive = None
    GoogleSheetsClient = None
    read_google_sheet = None

__all__ = [
    'GoogleDriveClient',
    'download_data_from_drive',
    'GoogleSheetsClient',
    'read_google_sheet',
    'CSVDataReader',
    'load_sample_data',
    'GOOGLE_AVAILABLE',
]
