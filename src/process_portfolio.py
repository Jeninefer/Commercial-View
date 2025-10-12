#!/usr/bin/env python3
"""
Commercial View - Portfolio Processing Module
Main entry point for loan portfolio analysis and processing
"""

import sys
import os
import logging
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

try:
    from data_loader import DataLoader
    from feature_engineer import FeatureEngineer
    from kpi_calculator import KPICalculator
    from pricing_enricher import PricingEnricher
    from dpd_analyzer import DPDAnalyzer
    from payment_processor import PaymentProcessor
    from metrics_registry import MetricsRegistry
except ImportError as e:
    logging.warning(f"Some modules not available: {e}")
    # Fallback imports or create minimal versions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('portfolio_processing.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class PortfolioProcessor:
    """Main portfolio processing orchestrator"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the portfolio processor"""
        self.config_path = config_path or "config"
        self.data_loader = None
        self.feature_engineer = None
        self.kpi_calculator = None
        self.pricing_enricher = None
        self.dpd_analyzer = None
        self.payment_processor = None
        self.metrics_registry = MetricsRegistry()
        
        self.setup_directories()
        
    def setup_directories(self):
        """Create necessary output directories"""
        directories = [
            "abaco_runtime/exports/dpd",
            "abaco_runtime/exports/kpi/json",
            "abaco_runtime/exports/pricing",
            "abaco_runtime/exports/analytics"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            
    def load_data(self) -> Dict[str, pd.DataFrame]:
        """Load all portfolio data"""
        logger.info("Loading portfolio data...")
        
        data_files = {
            "customer_data": "data/raw/Abaco - Loan Tape_Customer Data_Table",
            "loan_data": "data/raw/Abaco - Loan Tape_Loan Data_Table", 
            "payment_history": "data/raw/Abaco - Loan Tape_Historic Real Payment_Table",
            "payment_schedule": "data/raw/Abaco - Loan Tape_Payment Schedule_Table"
        }
        
        datasets = {}
        for name, filepath in data_files.items():
            try:
                if os.path.exists(filepath):
                    logger.info(f"Loading {name} from {filepath}")
                    datasets[name] = pd.read_excel(filepath)
                    logger.info(f"Loaded {len(datasets[name])} rows for {name}")
                else:
                    logger.warning(f"File not found: {filepath}")
            except Exception as e:
                logger.error(f"Error loading {name}: {e}")
                
        return datasets
    
    def process_portfolio(self) -> Dict:
        """Main portfolio processing pipeline"""
        logger.info("Starting portfolio processing...")
        
        # Load data
        datasets = self.load_data()
        
        if not datasets:
            logger.error("No data loaded. Cannot proceed with processing.")
            return {"status": "error", "message": "No data available"}
        
        results = {
            "processing_timestamp": datetime.now().isoformat(),
            "datasets_loaded": list(datasets.keys()),
            "total_records": {name: len(df) for name, df in datasets.items()}
        }
        
        # Basic data analysis
        try:
            # Customer analysis
            if "customer_data" in datasets:
                customer_df = datasets["customer_data"]
                results["customer_analysis"] = {
                    "total_customers": len(customer_df),
                    "unique_customers": customer_df.iloc[:, 0].nunique() if len(customer_df.columns) > 0 else 0
                }
            
            # Loan analysis
            if "loan_data" in datasets:
                loan_df = datasets["loan_data"]
                results["loan_analysis"] = {
                    "total_loans": len(loan_df),
                    "columns": list(loan_df.columns) if len(loan_df.columns) > 0 else []
                }
            
            # Payment analysis
            if "payment_history" in datasets:
                payment_df = datasets["payment_history"]
                results["payment_analysis"] = {
                    "total_payments": len(payment_df),
                    "columns": list(payment_df.columns) if len(payment_df.columns) > 0 else []
                }
                
        except Exception as e:
            logger.error(f"Error in analysis: {e}")
            results["analysis_error"] = str(e)
        
        # Export results
        self.export_results(results)
        
        logger.info("Portfolio processing completed")
        return results
    
    def export_results(self, results: Dict):
        """Export processing results"""
        
        # Export to JSON
        output_file = f"abaco_runtime/exports/analytics/portfolio_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f"Results exported to {output_file}")
        except Exception as e:
            logger.error(f"Error exporting results: {e}")

def main():
    """Main execution function"""
    logger.info("=== Commercial View Portfolio Processor ===")
    
    try:
        processor = PortfolioProcessor()
        results = processor.process_portfolio()
        
        print("\n" + "="*50)
        print("PORTFOLIO PROCESSING SUMMARY")
        print("="*50)
        print(f"Status: {'SUCCESS' if 'error' not in results else 'ERROR'}")
        print(f"Timestamp: {results.get('processing_timestamp', 'N/A')}")
        print(f"Datasets loaded: {len(results.get('datasets_loaded', []))}")
        
        if 'total_records' in results:
            print("\nRecord counts:")
            for dataset, count in results['total_records'].items():
                print(f"  - {dataset}: {count:,} records")
        
        if 'customer_analysis' in results:
            print("Customer Analysis:")
            print(f"  - Total customers: {results['customer_analysis']['total_customers']:,}")
            print(f"  - Unique customers: {results['customer_analysis']['unique_customers']:,}")
        
        if 'loan_analysis' in results:
            print("Loan Analysis:")
            print(f"  - Total loans: {results['loan_analysis']['total_loans']:,}")
            print(f"  - Data columns: {len(results['loan_analysis']['columns'])}")
        
        if 'payment_analysis' in results:
            print("Payment Analysis:")
            print(f"  - Total payments: {results['payment_analysis']['total_payments']:,}")
            print(f"  - Data columns: {len(results['payment_analysis']['columns'])}")
        
        print("\n" + "="*50)
        
        # Portfolio Overview
        print("📊 PORTFOLIO OVERVIEW")
        for dataset, count in results['total_records'].items():
            print(f"- {dataset.replace('_', ' ').title()}: {count:,} registros")
        
        total_records = sum(results['total_records'].values())
        print(f"- Total Records: {total_records:,} registros")
        
        return results
        
    except Exception as e:
        logger.error(f"Fatal error in main execution: {e}")
        print(f"\nERROR: {e}")
        return None

if __name__ == "__main__":
    main()
