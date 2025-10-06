"""
Generate complete CSV datasets for Commercial-View
Creates all required production data files
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from pathlib import Path
import logging
from typing import Dict

logger = logging.getLogger(__name__)


class ProductionDatasetGenerator:
    """Generate complete production datasets for Commercial-View"""

    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)

        # Set random seed for reproducible data
        np.random.seed(42)
        random.seed(42)

    def generate_all_datasets(self) -> Dict[str, str]:
        """Generate all required CSV datasets"""
        logger.info("🔄 Generating complete Commercial-View datasets...")

        generated_files = {}

        # Generate core datasets
        generated_files["loan_data"] = self._generate_loan_data()
        generated_files["payment_schedule"] = self._generate_payment_schedule()
        generated_files["historic_payments"] = self._generate_historic_payments()
        generated_files["customer_data"] = self._generate_customer_data()
        generated_files["collateral_data"] = self._generate_collateral_data()
        generated_files["q4_targets"] = self._generate_q4_targets()

        logger.info(f"✅ Generated {len(generated_files)} complete datasets")
        return generated_files

    def _generate_loan_data(self) -> str:
        """Generate comprehensive loan portfolio data"""
        num_loans = 2500

        # Generate loan IDs
        loan_ids = [f"CL{str(i+1).zfill(6)}" for i in range(num_loans)]

        # Generate customer IDs (some customers have multiple loans)
        num_customers = 800
        customer_ids = []
        for i in range(num_loans):
            if i < num_customers:
                customer_ids.append(f"CUST{str(i+1).zfill(4)}")
            else:
                # Some customers get additional loans
                customer_ids.append(
                    f"CUST{str(random.randint(1, num_customers)).zfill(4)}"
                )

        # Loan amounts with realistic distribution
        loan_amounts = []
        for _ in range(num_loans):
            if random.random() < 0.6:  # 60% smaller loans
                amount = random.uniform(25000, 500000)
            elif random.random() < 0.9:  # 30% medium loans
                amount = random.uniform(500000, 2000000)
            else:  # 10% large loans
                amount = random.uniform(2000000, 10000000)
            loan_amounts.append(round(amount, 2))

        # Interest rates based on risk and loan size
        interest_rates = []
        for amount in loan_amounts:
            base_rate = 0.12  # 12% base
            size_adjustment = (
                -0.02 if amount > 1000000 else 0.01
            )  # Large loans get better rates
            risk_adjustment = random.uniform(-0.03, 0.08)  # Risk-based pricing
            rate = max(0.08, min(0.35, base_rate + size_adjustment + risk_adjustment))
            interest_rates.append(round(rate, 4))

        # Loan terms (in months)
        terms = np.random.choice(
            [12, 24, 36, 48, 60, 72], num_loans, p=[0.1, 0.25, 0.35, 0.2, 0.08, 0.02]
        )

        # Origination dates (last 36 months)
        start_date = datetime.now() - timedelta(days=1095)
        origination_dates = []
        for _ in range(num_loans):
            days_offset = random.randint(0, 1095)
            orig_date = start_date + timedelta(days=days_offset)
            origination_dates.append(orig_date.strftime("%Y-%m-%d"))

        # Maturity dates
        maturity_dates = []
        for i, term in enumerate(terms):
            orig_date = datetime.strptime(origination_dates[i], "%Y-%m-%d")
            maturity_date = orig_date + timedelta(days=term * 30)
            maturity_dates.append(maturity_date.strftime("%Y-%m-%d"))

        # Loan status
        statuses = np.random.choice(
            ["active", "paid_off", "charged_off", "delinquent"],
            num_loans,
            p=[0.75, 0.20, 0.03, 0.02],
        )

        # Industry codes (NAICS)
        industry_codes = np.random.choice(
            [
                "236220",
                "238210",
                "541511",
                "722513",
                "445120",
                "238990",
                "531210",
                "424710",
                "484110",
                "561720",
            ],
            num_loans,
        )

        # Risk grades
        risk_grades = np.random.choice(
            ["A", "B", "C", "D", "E"], num_loans, p=[0.25, 0.35, 0.25, 0.12, 0.03]
        )

        loan_df = pd.DataFrame(
            {
                "loan_id": loan_ids,
                "customer_id": customer_ids,
                "principal_amount": loan_amounts,
                "interest_rate": interest_rates,
                "term_months": terms,
                "origination_date": origination_dates,
                "maturity_date": maturity_dates,
                "loan_status": statuses,
                "industry_code": industry_codes,
                "risk_grade": risk_grades,
                "remaining_balance": [
                    round(amt * random.uniform(0.2, 0.95), 2) for amt in loan_amounts
                ],
            }
        )

        filename = "loan_data.csv"
        filepath = self.data_dir / filename
        loan_df.to_csv(filepath, index=False)

        logger.info(f"✅ Generated {filename}: {len(loan_df)} loans")
        return str(filepath)

    def _generate_payment_schedule(self) -> str:
        """Generate payment schedule with EOM balances"""
        # Load loan data to generate schedules
        loan_df = pd.read_csv(self.data_dir / "loan_data.csv")

        payment_schedules = []
        payment_id = 1

        for _, loan in loan_df.iterrows():
            if loan["loan_status"] not in ["active", "delinquent"]:
                continue

            # Calculate monthly payment
            principal = loan["principal_amount"]
            rate = loan["interest_rate"] / 12  # Monthly rate
            term = loan["term_months"]

            if rate > 0:
                monthly_payment = (
                    principal * (rate * (1 + rate) ** term) / ((1 + rate) ** term - 1)
                )
            else:
                monthly_payment = principal / term

            # Generate payment schedule
            balance = principal
            payment_date = datetime.strptime(loan["origination_date"], "%Y-%m-%d")

            for month in range(term):
                if balance <= 0:
                    break

                payment_date = payment_date.replace(day=1) + timedelta(days=32)
                payment_date = payment_date.replace(day=min(payment_date.day, 28))

                interest_payment = balance * rate
                principal_payment = min(monthly_payment - interest_payment, balance)
                balance -= principal_payment

                payment_schedules.append(
                    {
                        "payment_id": f"PAY{str(payment_id).zfill(8)}",
                        "loan_id": loan["loan_id"],
                        "due_date": payment_date.strftime("%Y-%m-%d"),
                        "principal_amount": round(principal_payment, 2),
                        "interest_amount": round(interest_payment, 2),
                        "total_amount": round(monthly_payment, 2),
                        "remaining_balance": round(balance, 2),
                        "payment_status": (
                            "pending"
                            if payment_date > datetime.now()
                            else np.random.choice(
                                ["paid", "overdue", "partial"], p=[0.85, 0.10, 0.05]
                            )
                        ),
                    }
                )

                payment_id += 1

        schedule_df = pd.DataFrame(payment_schedules)
        filename = "payment_schedule.csv"
        filepath = self.data_dir / filename
        schedule_df.to_csv(filepath, index=False)

        logger.info(f"✅ Generated {filename}: {len(schedule_df)} payment records")
        return str(filepath)

    def _generate_q4_targets(self) -> str:
        """Generate Q4 2024 targets CSV"""
        targets_data = [
            {
                "Month": "2024-10-01",
                "Outstanding_Target": 7800000,
                "Disbursement_Target": 450000,
                "APR_Target": 0.185,
                "NPL_Target": 0.025,
                "Collection_Rate_Target": 0.95,
                "Active_Clients_Target": 150,
                "Concentration_Limit": 0.15,
            },
            {
                "Month": "2024-11-01",
                "Outstanding_Target": 8200000,
                "Disbursement_Target": 450000,
                "APR_Target": 0.185,
                "NPL_Target": 0.025,
                "Collection_Rate_Target": 0.95,
                "Active_Clients_Target": 155,
                "Concentration_Limit": 0.15,
            },
            {
                "Month": "2024-12-01",
                "Outstanding_Target": 8500000,
                "Disbursement_Target": 370000,
                "APR_Target": 0.185,
                "NPL_Target": 0.025,
                "Collection_Rate_Target": 0.95,
                "Active_Clients_Target": 160,
                "Concentration_Limit": 0.15,
            },
        ]

        targets_df = pd.DataFrame(targets_data)
        filename = "Q4_Targets.csv"
        filepath = self.data_dir / filename
        targets_df.to_csv(filepath, index=False)

        logger.info(f"✅ Generated {filename}: Q4 2024 targets")
        return str(filepath)

    def _generate_historic_payments(self) -> str:
        """Generate historical payments data for analytics"""
        # Load loan data to simulate payments
        loan_df = pd.read_csv(self.data_dir / "loan_data.csv")

        historic_payments = []
        payment_id = 1

        for _, loan in loan_df.iterrows():
            if loan["loan_status"] == "active":
                continue  # Skip active loans for historical data

            # Simulate payment history
            num_payments = random.randint(1, loan["term_months"])  # Up to term length
            payment_dates = pd.date_range(
                start=loan["origination_date"],
                periods=num_payments,
                freq="MS",  # Month start
            )

            for payment_date in payment_dates:
                if loan["loan_status"] == "charged_off":
                    status = "failed"
                else:
                    status = np.random.choice(["successful", "failed"], p=[0.9, 0.1])

                historic_payments.append(
                    {
                        "payment_id": f"PAY{str(payment_id).zfill(8)}",
                        "loan_id": loan["loan_id"],
                        "payment_date": payment_date.strftime("%Y-%m-%d"),
                        "amount": round(random.uniform(100, 5000), 2),
                        "status": status,
                    }
                )

                payment_id += 1

        historic_df = pd.DataFrame(historic_payments)
        filename = "historic_payments.csv"
        filepath = self.data_dir / filename
        historic_df.to_csv(filepath, index=False)

        logger.info(
            f"✅ Generated {filename}: {len(historic_df)} historical payment records"
        )
        return str(filepath)

    def _generate_customer_data(self) -> str:
        """Generate synthetic customer demographic data"""
        num_customers = 800

        # Customer IDs
        customer_ids = [f"CUST{str(i+1).zfill(4)}" for i in range(num_customers)]

        # Names (randomly generated)
        first_names = [
            "John",
            "Jane",
            "Alex",
            "Emily",
            "Chris",
            "Katie",
            "Michael",
            "Sarah",
        ]
        last_names = [
            "Smith",
            "Doe",
            "Brown",
            "Johnson",
            "Lee",
            "Wilson",
            "Moore",
            "Taylor",
        ]
        names = [
            f"{random.choice(first_names)} {random.choice(last_names)}"
            for _ in range(num_customers)
        ]

        # Contact info
        emails = [f"user{str(i+1).zfill(4)}@example.com" for i in range(num_customers)]
        phone_numbers = [
            f"+1-800-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
            for _ in range(num_customers)
        ]

        # Addresses (dummy data)
        addresses = [
            f"{random.randint(100, 999)} {' '.join(random.choices(['Main St', '2nd St', '3rd St', '4th St'], k=1))}, Cityville, ST, {random.randint(10000, 99999)}"
            for _ in range(num_customers)
        ]

        # Demographics
        ages = np.random.randint(18, 70, num_customers)
        incomes = np.random.randint(30000, 120000, num_customers)
        employment_status = np.random.choice(
            ["employed", "unemployed", "self-employed", "retired"],
            num_customers,
            p=[0.6, 0.2, 0.15, 0.05],
        )

        customer_df = pd.DataFrame(
            {
                "customer_id": customer_ids,
                "name": names,
                "email": emails,
                "phone_number": phone_numbers,
                "address": addresses,
                "age": ages,
                "income": incomes,
                "employment_status": employment_status,
            }
        )

        filename = "customer_data.csv"
        filepath = self.data_dir / filename
        customer_df.to_csv(filepath, index=False)

        logger.info(f"✅ Generated {filename}: {len(customer_df)} customer records")
        return str(filepath)

    def _generate_collateral_data(self) -> str:
        """Generate synthetic collateral data for secured loans"""
        num_collaterals = 1200

        # Collateral IDs
        collateral_ids = [f"COLL{str(i+1).zfill(6)}" for i in range(num_collaterals)]

        # Associated loan IDs (some loans may not have collateral)
        loan_df = pd.read_csv(self.data_dir / "loan_data.csv")
        loan_ids = loan_df["loan_id"].tolist()
        associated_loan_ids = random.choices(loan_ids, k=num_collaterals)

        # Collateral types
        collateral_types = np.random.choice(
            ["real_estate", "vehicle", "equipment", "inventory"], num_collaterals
        )

        # Valuation amounts
        valuation_amounts = []
        for collateral_type in collateral_types:
            if collateral_type == "real_estate":
                amount = random.uniform(50000, 500000)
            elif collateral_type == "vehicle":
                amount = random.uniform(5000, 50000)
            elif collateral_type == "equipment":
                amount = random.uniform(10000, 100000)
            else:  # inventory
                amount = random.uniform(1000, 10000)
            valuation_amounts.append(round(amount, 2))

        collateral_df = pd.DataFrame(
            {
                "collateral_id": collateral_ids,
                "loan_id": associated_loan_ids,
                "collateral_type": collateral_types,
                "valuation_amount": valuation_amounts,
            }
        )

        filename = "collateral_data.csv"
        filepath = self.data_dir / filename
        collateral_df.to_csv(filepath, index=False)

        logger.info(f"✅ Generated {filename}: {len(collateral_df)} collateral records")
        return str(filepath)


if __name__ == "__main__":
    generator = ProductionDatasetGenerator()
    files = generator.generate_all_datasets()

    print("✅ Complete Commercial-View datasets generated:")
    for dataset, filepath in files.items():
        print(f"   📄 {dataset}: {filepath}")
