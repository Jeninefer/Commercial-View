"""
Google Sheets integration module.
Provides access to data stored in Google Sheets.
"""

from typing import List, Dict, Any, Optional
import gspread
from google.oauth2.credentials import Credentials
import pickle

from config import TOKEN_FILE


class GoogleSheetsClient:
    """Client for reading data from Google Sheets."""
    
    def __init__(self):
        self.client = None
        self.creds: Optional[Credentials] = None
        
    def authenticate(self) -> bool:
        """
        Authenticate with Google Sheets using saved credentials.
        Returns True if authentication successful.
        """
        if not TOKEN_FILE.exists():
            raise FileNotFoundError(
                "Token file not found. Please run Google Drive authentication first."
            )
        
        with open(TOKEN_FILE, 'rb') as token:
            self.creds = pickle.load(token)
        
        self.client = gspread.authorize(self.creds)
        return True
    
    def read_sheet(self, sheet_id: str, worksheet_name: str = None) -> List[Dict[str, Any]]:
        """
        Read data from a Google Sheet and return as list of dictionaries.
        
        Args:
            sheet_id: The Google Sheets ID
            worksheet_name: Name of the worksheet (tab). If None, uses first sheet.
            
        Returns:
            List of dictionaries where keys are column headers
        """
        if not self.client:
            self.authenticate()
        
        spreadsheet = self.client.open_by_key(sheet_id)
        
        if worksheet_name:
            worksheet = spreadsheet.worksheet(worksheet_name)
        else:
            worksheet = spreadsheet.get_worksheet(0)
        
        # Get all records as list of dictionaries
        records = worksheet.get_all_records()
        return records
    
    def read_range(self, sheet_id: str, range_name: str) -> List[List[Any]]:
        """
        Read a specific range from a Google Sheet.
        
        Args:
            sheet_id: The Google Sheets ID
            range_name: Range in A1 notation (e.g., 'Sheet1!A1:D10')
            
        Returns:
            List of lists representing rows and columns
        """
        if not self.client:
            self.authenticate()
        
        spreadsheet = self.client.open_by_key(sheet_id)
        values = spreadsheet.values_get(range_name)
        return values.get('values', [])
    
    def get_all_worksheets(self, sheet_id: str) -> List[str]:
        """
        Get list of all worksheet names in a spreadsheet.
        
        Args:
            sheet_id: The Google Sheets ID
            
        Returns:
            List of worksheet names
        """
        if not self.client:
            self.authenticate()
        
        spreadsheet = self.client.open_by_key(sheet_id)
        worksheets = spreadsheet.worksheets()
        return [ws.title for ws in worksheets]


def read_google_sheet(sheet_id: str, worksheet_name: str = None) -> List[Dict[str, Any]]:
    """
    Convenience function to read data from Google Sheets.
    """
    client = GoogleSheetsClient()
    return client.read_sheet(sheet_id, worksheet_name)
