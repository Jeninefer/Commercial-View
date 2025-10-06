"""
Production data validation for Commercial-View
Ensures all data sources are real commercial lending data
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
import re

class ProductionDataValidator:
    """Validates that all data is production-ready commercial lending data"""
    
    def __init__(self):
        self.data_dir = Path("/Users/jenineferderas/Commercial-View/data")
        self.real_data_indicators = [
            r'^[A-Z]{2}\d{6}$',  # Real loan IDs like CL123456
            r'^CUST\d{4}$',      # Real customer IDs like CUST0001  
            r'^\d{4}-\d{2}-\d{2}$',  # Real dates YYYY-MM-DD
        ]
        
        self.demo_data_flags = [
            # Demo customer names
            'john doe', 'jane smith', 'acme corp', 'test company',
            'example inc', 'sample business', 'demo customer',
            
            # Demo amounts (too round/obvious)
            '100000.00', '50000.00', '25000.00', '10000.00',
            
            # Demo phone/email patterns
            '555-0', 'example.com', 'test.com', 'demo.com',
            
            # Placeholder text
            'lorem ipsum', 'placeholder', 'tbd', 'xxx',
        ]
    
    def validate_all_datasets(self) -> Dict[str, any]:
        """Validate all CSV datasets for production readiness"""
        
        validation_results = {
            "datasets_validated": 0,
            "production_ready": 0,
            "issues_found": [],
            "dataset_details": {}
        }
        
        csv_files = list(self.data_dir.rglob("*.csv"))
        
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                dataset_result = self._validate_dataset(df, csv_file.name)
                
                validation_results["datasets_validated"] += 1
                validation_results["dataset_details"][csv_file.name] = dataset_result
                
                if dataset_result["production_ready"]:
                    validation_results["production_ready"] += 1
                else:
                    validation_results["issues_found"].extend(dataset_result["issues"])
                    
            except Exception as e:
                validation_results["issues_found"].append({
                    "file": csv_file.name,
                    "issue": f"Failed to load: {e}"
                })
        
        validation_results["all_production_ready"] = (
            validation_results["production_ready"] == validation_results["datasets_validated"] and
            len(validation_results["issues_found"]) == 0
        )
        
        return validation_results
    
    def _validate_dataset(self, df: pd.DataFrame, filename: str) -> Dict[str, any]:
        """Validate individual dataset for production data"""
        
        issues = []
        
        # Check for demo data patterns in string columns
        string_columns = df.select_dtypes(include=['object']).columns
        
        for col in string_columns:
            for demo_flag in self.demo_data_flags:
                if df[col].astype(str).str.lower().str.contains(demo_flag, na=False).any():
                    issues.append({
                        "column": col,
                        "issue": f"Demo data pattern detected: {demo_flag}",
                        "severity": "high"
                    })
        
        # Check for unrealistic data patterns
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            # Check for too many round numbers (indicates generated data)
            if col.lower() in ['amount', 'balance', 'principal']:
                round_numbers = df[col].apply(lambda x: x % 1000 == 0 if pd.notna(x) else False).sum()
                if round_numbers > len(df) * 0.8:  # More than 80% round numbers
                    issues.append({
                        "column": col,
                        "issue": f"Too many round numbers ({round_numbers}/{len(df)})",
                        "severity": "medium"
                    })
        
        # Check for realistic commercial lending data characteristics
        if 'loan_id' in df.columns or any('loan' in col.lower() for col in df.columns):
            if not self._validate_commercial_loan_data(df, issues):
                pass  # Issues already added to list
        
        return {
            "production_ready": len([i for i in issues if i["severity"] == "high"]) == 0,
            "issues": issues,
            "record_count": len(df),
            "column_count": len(df.columns)
        }
    
    def _validate_commercial_loan_data(self, df: pd.DataFrame, issues: List) -> bool:
        """Validate commercial loan specific data patterns"""
        
        # Check for realistic loan amounts (commercial lending typically $25K+)
        amount_cols = [col for col in df.columns if 'amount' in col.lower() or 'principal' in col.lower()]
        
        for col in amount_cols:
            if col in df.columns:
                small_loans = df[df[col] < 25000][col].count()
                if small_loans > len(df) * 0.5:  # More than 50% under $25K
                    issues.append({
                        "column": col,
                        "issue": f"Too many small loans for commercial lending ({small_loans}/{len(df)})",
                        "severity": "medium"
                    })
        
        # Check for realistic interest rates (commercial lending typically 8-35%)
        rate_cols = [col for col in df.columns if 'rate' in col.lower() or 'apr' in col.lower()]
        
        for col in rate_cols:
            if col in df.columns:
                unrealistic_rates = df[(df[col] < 0.05) | (df[col] > 0.40)][col].count()
                if unrealistic_rates > len(df) * 0.1:  # More than 10% unrealistic
                    issues.append({
                        "column": col,
                        "issue": f"Unrealistic interest rates detected ({unrealistic_rates}/{len(df)})",
                        "severity": "high"
                    })
        
        return len(issues) == 0

def main():
    """Run production data validation"""
    print("🏦 COMMERCIAL-VIEW PRODUCTION DATA VALIDATION")
    print("=" * 50)
    
    validator = ProductionDataValidator()
    results = validator.validate_all_datasets()
    
    print(f"Datasets Validated: {results['datasets_validated']}")
    print(f"Production Ready: {results['production_ready']}")
    print(f"Issues Found: {len(results['issues_found'])}")
    
    if results["all_production_ready"]:
        print("\n✅ ALL DATASETS ARE PRODUCTION-READY COMMERCIAL LENDING DATA")
    else:
        print("\n❌ DEMO DATA OR ISSUES DETECTED:")
        for issue in results["issues_found"][:10]:  # Show first 10 issues
            print(f"  - {issue}")
    
    return results["all_production_ready"]

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
