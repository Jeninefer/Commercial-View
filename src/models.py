from pydantic import BaseModel
from typing import Optional
from datetime import date

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