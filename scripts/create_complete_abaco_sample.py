"""
Create Complete Abaco Sample Data Generator

Generates sample CSV files that match the exact Abaco schema structure:
- Loan Data Table (28 columns)
- Historic Real Payment Table (18 columns)
- Payment Schedule Table (16 columns)

All data matches the validated schema with Spanish client names,
USD factoring products, and bullet payment structures.
"""

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict


class AbacoSampleDataGenerator:
    """Generate sample Abaco loan tape data matching exact schema."""

    def __init__(self, num_loans: int = 100):
        """Initialize the sample data generator.
        
        Args:
            num_loans: Number of sample loans to generate (default: 100)
        """
        self.num_loans = num_loans
        self.output_dir = Path("data")
        self.output_dir.mkdir(exist_ok=True)
        
        # Sample data from validated schema
        self.companies = ["Abaco Technologies", "Abaco Financial"]
        
        self.spanish_clients = [
            "SERVICIOS TECNICOS MEDICOS, S.A. DE C.V.",
            "PRODUCTOS DE CONCRETO, S.A. DE C.V.",
            "KEVIN ENRIQUE CABEZAS MORALES",
            "DISTRIBUIDORA COMERCIAL, S.A. DE C.V.",
            "CONSTRUCCIONES Y OBRAS, S.A.",
            "INVERSIONES FINANCIERAS, S.R.L.",
            "GRUPO INDUSTRIAL DEL SUR, S.A. DE C.V.",
            "COMERCIALIZADORA INTERNACIONAL, S.A.",
            "SERVICIOS PROFESIONALES INTEGRADOS, S.A. DE C.V.",
            "TECNOLOGIA Y SOLUCIONES, S.A. DE C.V."
        ]
        
        self.spanish_payers = [
            "HOSPITAL NACIONAL \"SAN JUAN DE DIOS\" SAN MIGUEL",
            "ASSA COMPAÑIA DE SEGUROS, S.A.",
            "EMPRESA TRANSMISORA DE EL SALVADOR, S.A. DE C.V. ETESAL, S.A. DE C.V.",
            "MINISTERIO DE SALUD PUBLICA Y ASISTENCIA SOCIAL",
            "INSTITUTO SALVADOREÑO DEL SEGURO SOCIAL",
            "FONDO DE CONSERVACION VIAL",
            "ADMINISTRACION NACIONAL DE ACUEDUCTOS Y ALCANTARILLADOS",
            "COMISION EJECUTIVA HIDROELECTRICA DEL RIO LEMPA",
            "FONDO SOLIDARIO PARA LA FAMILIA MICROEMPRESARIA"
        ]
        
        self.loan_statuses = ["Current", "Complete", "Default"]
        self.payment_statuses = ["Late", "On Time", "Prepayment"]
        self.terms = [30, 90, 120]  # days
        
        # Interest rate range from schema: 29.47% - 36.99%
    # Class-level constants for APR rates
    MIN_APR_RATE = 0.2947
    MAX_APR_RATE = 0.3699
    def generate_loan_id(self, index: int) -> str:
        """Generate a loan ID in Abaco format."""
        year = random.randint(17, 25)
        month = random.randint(1, 12)
        seq = str(index + 1).zfill(3)
        return f"DSB{year}{str(month).zfill(2)}-{seq}"

    def generate_customer_id(self, index: int) -> str:
        """Generate a customer ID in Abaco format."""
        seq = str(index + 1).zfill(6)
        return f"CLIAB{seq}"

    def generate_loan_data(self) -> List[Dict]:
        """Generate Loan Data Table records."""
        loans = []
        base_date = datetime(2025, 9, 1)
        
        for i in range(self.num_loans):
            # Generate core identifiers
            loan_id = self.generate_loan_id(i)
            customer_id = self.generate_customer_id(i)
            
            # Financial amounts
            tpv = round(random.uniform(88.48, 77175.0), 2)
            disbursement_amount = round(tpv * 0.963, 2)  # ~96.3% of TPV
            origination_fee = round(tpv * 0.0325, 2)
            origination_fee_taxes = round(origination_fee * 0.13, 2)
            
            # Random date within range
            days_offset = random.randint(0, 60)
            disbursement_date = (base_date + timedelta(days=days_offset)).strftime("%Y-%m-%d")
            
            # Interest rate within validated range
            interest_rate = round(random.uniform(self.MIN_APR_RATE, self.MAX_APR_RATE), 4)
            
            # Term selection
            term = random.choice(self.terms)
            
            # Outstanding value (may differ from TPV based on payments)
            outstanding = round(random.uniform(0, tpv), 2) if random.random() > 0.3 else tpv
            
            loan = {
                "Company": random.choice(self.companies),
                "Customer ID": customer_id,
                "Cliente": random.choice(self.spanish_clients),
                "Pagador": random.choice(self.spanish_payers),
                "Application ID": loan_id,
                "Loan ID": loan_id,
                "Product Type": "factoring",
                "Disbursement Date": disbursement_date,
                "TPV": tpv,
                "Disbursement Amount": disbursement_amount,
                "Origination Fee": origination_fee,
                "Origination Fee Taxes": origination_fee_taxes,
                "Loan Currency": "USD",
                "Interest Rate APR": interest_rate,
                "Term": term,
                "Term Unit": "days",
                "Payment Frequency": "bullet",
                "Days in Default": random.choice([0, 0, 0, 1, 3]),  # Mostly 0
                "Pledge To": "",  # Empty (null in original)
                "Pledge Date": "",  # Empty (null in original)
                "Loan Status": random.choice(self.loan_statuses),
                "Outstanding Loan Value": outstanding,
                "Other": "",  # Empty (null in original)
                "New Loan ID": "",  # Empty (null in original)
                "New Loan Date": "",  # Empty (null in original)
                "Old Loan ID": "",  # Empty (null in original)
                "Recovery Date": "",  # Empty (null in original)
                "Recovery Value": "",  # Empty (null in original)
            }
            loans.append(loan)
        
        return loans

    def generate_payment_history(self, loans: List[Dict]) -> List[Dict]:
        """Generate Historic Real Payment Table records."""
        payments = []
        
        # Generate 1-2 payment records per loan (slightly more records than loans)
        for loan in loans:
            num_payments = random.choice([1, 1, 1, 2])  # Mostly 1, sometimes 2
            
            loan_date = datetime.strptime(loan["Disbursement Date"], "%Y-%m-%d")
            
            for payment_num in range(num_payments):
                # Payment date after disbursement
                days_after = random.randint(15, loan["Term"] + 10)
                payment_date = (loan_date + timedelta(days=days_after)).strftime("%Y-%m-%d")
                
                # Payment amounts
                tpv = loan["TPV"]
                principal = round(random.uniform(tpv * 0.7, tpv), 2)
                interest = round(principal * loan["Interest Rate APR"] * (loan["Term"] / 365), 2)
                fee = round(random.uniform(0, 100), 2)
                tax = round(fee * 0.13, 2)
                other = round(random.uniform(0, 50), 2) if random.random() > 0.8 else 0
                
                total_payment = round(principal + interest + fee + other + tax, 2)
                outstanding = round(max(0, tpv - principal), 2)
                
                payment = {
                    "Company": loan["Company"],
                    "Customer ID": loan["Customer ID"],
                    "Cliente": loan["Cliente"],
                    "Pagador": loan["Pagador"],
                    "Loan ID": loan["Loan ID"],
                    "True Payment Date": payment_date,
                    "True Devolution": round(random.uniform(0, 1000), 2) if random.random() > 0.9 else 0,
                    "True Total Payment": total_payment,
                    "True Payment Currency": "USD",
                    "True Principal Payment": principal,
                    "True Interest Payment": interest,
                    "True Fee Payment": fee,
                    "True Other Payment": other,
                    "True Tax Payment": tax,
                    "True Fee Tax Payment": round(fee * 0.13, 2),
                    "True Rebates": 0,  # Usually 0
                    "True Outstanding Loan Value": outstanding,
                    "True Payment Status": random.choice(self.payment_statuses)
                }
                payments.append(payment)
        
        return payments

    def generate_payment_schedule(self, loans: List[Dict]) -> List[Dict]:
        """Generate Payment Schedule Table records."""
        schedules = []
        
        # One schedule record per loan
        for loan in loans:
            loan_date = datetime.strptime(loan["Disbursement Date"], "%Y-%m-%d")
            
            # Scheduled payment date (disbursement + term)
            payment_date = (loan_date + timedelta(days=loan["Term"])).strftime("%Y-%m-%d")
            
            # Scheduled amounts
            tpv = loan["TPV"]
            principal = tpv
            interest = round(principal * loan["Interest Rate APR"] * (loan["Term"] / 365), 2)
            fee = round(random.uniform(50, 200), 2)
            tax = round(fee * 0.13, 2)
            other = round(random.uniform(0, 50), 2) if random.random() > 0.8 else 0
            
            total_payment = round(principal + interest + fee + other + tax, 2)
            
            schedule = {
                "Company": loan["Company"],
                "Customer ID": loan["Customer ID"],
                "Cliente": loan["Cliente"],
                "Pagador": loan["Pagador"],
                "Loan ID": loan["Loan ID"],
                "Payment Date": payment_date,
                "TPV": tpv,
                "Total Payment": total_payment,
                "Currency": "USD",
                "Principal Payment": principal,
                "Interest Payment": interest,
                "Fee Payment": fee,
                "Other Payment": other,
                "Tax Payment": tax,
                "All Rebates": 0,
                "Outstanding Loan Value": 0  # After final payment
            }
            schedules.append(schedule)
        
        return schedules

    def save_csv(self, data: List[Dict], filename: str):
        """Save data to CSV file."""
        if not data:
            print(f"⚠️  No data to save for {filename}")
            return
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = data[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerows(data)
        
        print(f"✅ Created {filename}: {len(data)} records")

    def generate_all(self):
        """Generate all sample data files."""
        print("🏦 Abaco Sample Data Generator")
        print("=" * 50)
        print(f"📊 Generating {self.num_loans} sample loans...")
        print()
        
        # Generate loan data
        loans = self.generate_loan_data()
        self.save_csv(loans, "Abaco - Loan Tape_Loan Data_Table.csv")
        
        # Generate payment history (slightly more records)
        payments = self.generate_payment_history(loans)
        self.save_csv(payments, "Abaco - Loan Tape_Historic Real Payment_Table.csv")
        
        # Generate payment schedule (same count as loans)
        schedules = self.generate_payment_schedule(loans)
        self.save_csv(schedules, "Abaco - Loan Tape_Payment Schedule_Table.csv")
        
        print()
        print("=" * 50)
        print("✅ Sample data generation complete!")
        print(f"📁 Files saved to: {self.output_dir.absolute()}")
        print()
        print("📋 Summary:")
        print(f"   • Loan Data: {len(loans)} records")
        print(f"   • Payment History: {len(payments)} records")
        print(f"   • Payment Schedule: {len(schedules)} records")
        print(f"   • Total: {len(loans) + len(payments) + len(schedules)} records")
        print()
        print("🔍 Data characteristics:")
        print("   • Currency: USD exclusively")
        print("   • Product: factoring exclusively")
        print("   • Payment Type: bullet exclusively")
        print(f"   • Interest Rates: {self.MIN_APR_RATE*100:.2f}% - {self.MAX_APR_RATE*100:.2f}% APR")
        print("   • Spanish client names included")
        print("   • Terms: 30, 90, 120 days")
        print()
        print("🚀 Next steps:")
        print("   python portfolio.py --config config")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate complete Abaco sample data matching exact schema"
    )
    parser.add_argument(
        "--records",
        type=int,
        default=100,
        help="Number of loan records to generate (default: 100)"
    )
    
    args = parser.parse_args()
    
    # Generate sample data
    generator = AbacoSampleDataGenerator(num_loans=args.records)
    generator.generate_all()
    
    return True


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
