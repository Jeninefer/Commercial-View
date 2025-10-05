"""
Module: looker_client

Description:
    This module provides an interface to interact with the Looker API, allowing
    users to fetch dashboard and look data. It includes the LookerClient class,
    which handles authentication and API requests.

Configuration Requirements:
    - LOOKER_BASE_URL: Base URL for the Looker API
    - LOOKER_CLIENT_ID: Client ID for Looker API authentication
    - LOOKER_CLIENT_SECRET: Client secret for Looker API authentication

Quick Checks:
    To verify your environment setup, you can run the following commands after
    setting up your environment variables:
    
    >>> from looker_client import LookerClient
    >>> client = LookerClient()
    >>> client.get_dashboard("123")  # Replace "123" with an actual dashboard ID

Usage Example:
    Here's a quick example of how to use the LookerClient to fetch a dashboard:
    
    ```python
    from looker_client import LookerClient

    client = LookerClient()
    dashboard = client.get_dashboard("123")
    print(f"Dashboard title: {dashboard['title']}")
    ```
"""

import os
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import date
import requests
from requests.exceptions import RequestException, HTTPError, Timeout
from functools import lru_cache

# Add missing environment variable imports
LOOKER_BASE_URL = os.getenv("LOOKER_BASE_URL")
LOOKER_CLIENT_ID = os.getenv("LOOKER_CLIENT_ID")
LOOKER_CLIENT_SECRET = os.getenv("LOOKER_CLIENT_SECRET")

class LoanData(BaseModel):
    Company: str
    CustomerID: str
    Cliente: str
    Pagador: str
    ApplicationID: str
    LoanID: str
    ProductType: str
    DisbursementDate: date
    TPV: float
    DisbursementAmount: float
    OriginationFee: float
    OriginationFeeTaxes: float
    LoanCurrency: str
    InterestRateAPR: float
    Term: int
    TermUnit: str
    PaymentFrequency: str
    DaysInDefault: int
    PledgeTo: Optional[float] = None
    PledgeDate: Optional[date] = None
    LoanStatus: str
    OutstandingLoanValue: float
    Other: Optional[float] = None
    NewLoanID: Optional[str] = None
    NewLoanDate: Optional[date] = None
    OldLoanID: Optional[str] = None
    RecoveryDate: Optional[date] = None
    RecoveryValue: Optional[float] = None

class HistoricRealPayment(BaseModel):
    Company: str
    CustomerID: str
    Cliente: str
    Pagador: str
    LoanID: str
    TruePaymentDate: date
    TrueDevolution: float
    TrueTotalPayment: float
    TruePaymentCurrency: str
    TruePrincipalPayment: float
    TrueInterestPayment: float
    TrueFeePayment: float
    TrueOtherPayment: Optional[float] = None
    TrueTaxPayment: float
    TrueFeeTaxPayment: float
    TrueRabates: int
    TrueOutstandingLoanValue: float
    TruePaymentStatus: str

class PaymentSchedule(BaseModel):
    Company: str
    CustomerID: str
    Cliente: str
    Pagador: str
    LoanID: str
    PaymentDate: date
    TPV: float
    TotalPayment: float
    Currency: str
    PrincipalPayment: float
    InterestPayment: float
    FeePayment: float
    OtherPayment: Optional[float] = None
    TaxPayment: float
    AllRebates: Optional[float] = None
    OutstandingLoanValue: int

class CustomerData(BaseModel):
    business_year_founded: Optional[int] = None
    equifax_score: Optional[str] = None
    category: Optional[str] = None
    credit_line_category: Optional[str] = None
    subcategory: Optional[str] = None
    credit_line_subcategory: Optional[str] = None
    industry: Optional[str] = None
    birth_year: Optional[int] = None
    occupation: Optional[str] = None
    client_type: Optional[str] = None
    location_city: Optional[str] = None
    location_state_province: Optional[str] = None
    location_country: Optional[str] = None
    customer_id: str
    customer_name: str

class Collateral(BaseModel):
    customer_id: str
    customer_name: str
    loan_id: str
    collateral_id: str
    collateral_original_value: float
    collateral_current_value: float

class LookerClient:
    def __init__(self):
        """Initialize the Looker client and authenticate."""
        self.session = requests.Session()
        # Strip trailing slashes from base URL to avoid double-slash issues
        self.base_url = LOOKER_BASE_URL.rstrip('/') if LOOKER_BASE_URL else ""
        # Create a single API prefix to reuse
        self.api_base = f"{self.base_url}/api/4.0"
        self._authenticate()

    def _authenticate(self) -> None:
        """Authenticate with the Looker API using client credentials."""
        if not all([self.base_url, LOOKER_CLIENT_ID, LOOKER_CLIENT_SECRET]):
            raise ValueError("Looker API credentials are not fully set in the environment variables.")
        
        auth_url = f"{self.api_base}/login"
        payload = {
            "client_id": LOOKER_CLIENT_ID,
            "client_secret": LOOKER_CLIENT_SECRET
        }
        
        try:
            response = self.session.post(auth_url, data=payload, timeout=10)
            response.raise_for_status()
            access_token = response.json().get("access_token")
            self.session.headers.update({"Authorization": f"token {access_token}"})
        except HTTPError as e:
            raise RuntimeError(f"Looker authentication failed: {e.response.text}") from e
        except Timeout:
            raise RuntimeError("Looker authentication timed out. Check network or server status.") 
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to authenticate with Looker API: {str(e)}") from e

    @lru_cache(maxsize=32)
    def get_dashboard(self, dashboard_id: str) -> Dict[str, Any]:
        """Fetches a Looker dashboard by its ID.
        
        Args:
            dashboard_id: The ID of the dashboard to retrieve
            
        Returns:
            Dictionary containing dashboard data
            
        Raises:
            RuntimeError: If the request fails with details about the failure
            Timeout: If the request times out
        """
        url = f"{self.api_base}/dashboards/{dashboard_id}"
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            raise RuntimeError(f"Failed to fetch dashboard {dashboard_id}: {e.response.text}") from e
        except Timeout:
            raise RuntimeError(f"Request to fetch dashboard {dashboard_id} timed out")
        except ValueError as e:
            raise RuntimeError(f"Invalid JSON response for dashboard {dashboard_id}") from e

    @lru_cache(maxsize=32)
    def get_look(self, look_id: str) -> Dict[str, Any]:
        """Fetches a Looker Look by its ID.
        
        Args:
            look_id: The ID of the look to retrieve
            
        Returns:
            Dictionary containing look data
            
        Raises:
            RuntimeError: If the request fails with details about the failure
            Timeout: If the request times out
        """
        url = f"{self.api_base}/looks/{look_id}"
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            raise RuntimeError(f"Failed to fetch look {look_id}: {e.response.text}") from e
        except Timeout:
            raise RuntimeError(f"Request to fetch look {look_id} timed out")
        except ValueError as e:
            raise RuntimeError(f"Invalid JSON response for look {look_id}") from e
    
    def close(self):
        """Close the session to free resources."""
        self.session.close()
    
    def __enter__(self):
        """Support for context manager usage with 'with' statement."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close session when exiting context manager."""
        self.close()


# Example usage
if __name__ == "__main__":
    client = LookerClient()
    try:
        dashboard = client.get_dashboard("42")
        print(f"Dashboard title: {dashboard['title']}")
        
        # Example of context manager usage
        with LookerClient() as another_client:
            look = another_client.get_look("12")
            print(f"Look title: {look['title']}")
    finally:
        client.close()