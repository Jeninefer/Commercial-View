"""
Daily batch job scheduler for automated data processing and analysis.
"""

import schedule
import time
import logging
from datetime import datetime
from pathlib import Path
import pandas as pd

from config import (
    DAILY_JOB_TIME,
    TIMEZONE,
    GOOGLE_DRIVE_FOLDER_URL,
    OUTPUT_DIR,
    OUTPUT_FORMAT,
    OUTPUT_DESTINATION,
    LOG_DIR
)
from ingestion import download_data_from_drive, load_sample_data
from analysis import calculate_portfolio_kpis, analyze_data
from optimization import optimize_disbursements

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'daily_job.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_daily_job():
    """
    Execute the daily batch job.
    This includes:
    1. Download latest data from Google Drive
    2. Calculate KPIs
    3. Generate AI insights
    4. Run optimization (if configured)
    5. Export results
    """
    logger.info("=" * 50)
    logger.info("Starting daily batch job")
    logger.info("=" * 50)
    
    try:
        # Step 1: Data ingestion
        logger.info("Step 1: Loading data...")
        data_dir = OUTPUT_DIR / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        
        if GOOGLE_DRIVE_FOLDER_URL:
            try:
                result = download_data_from_drive(GOOGLE_DRIVE_FOLDER_URL, data_dir)
                logger.info(f"Downloaded {result['successful']} files successfully")
            except Exception as e:
                logger.warning(f"Could not download from Google Drive: {e}")
                logger.info("Using sample data instead")
                data = load_sample_data()
        else:
            logger.info("Using sample data")
            data = load_sample_data()
        
        # Load data if downloaded
        if isinstance(data, dict):
            loan_tape = data['loan_tape']
            disbursement_requests = data['disbursement_requests']
        else:
            # Load from CSV files
            from ingestion import CSVDataReader
            reader = CSVDataReader(data_dir)
            loan_tape = reader.read_loan_tape()
            disbursement_requests = reader.read_disbursement_requests()
        
        # Step 2: Calculate KPIs
        logger.info("Step 2: Calculating KPIs...")
        kpis = calculate_portfolio_kpis(loan_tape)
        logger.info(f"Portfolio APR: {kpis['portfolio_apr']*100:.2f}%")
        logger.info(f"Active Loans: {kpis['active_loans']}")
        
        # Step 3: Generate AI insights
        logger.info("Step 3: Generating AI insights...")
        data_summary = {
            'kpis': kpis,
            'total_requests': len(disbursement_requests),
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            ai_analysis = analyze_data(data_summary)
            logger.info("AI insights generated successfully")
        except Exception as e:
            logger.warning(f"Could not generate AI insights: {e}")
            ai_analysis = None
        
        # Step 4: Export results
        logger.info("Step 4: Exporting results...")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Export KPIs
        kpi_df = pd.DataFrame([kpis])
        kpi_output_path = OUTPUT_DIR / f"kpis_{timestamp}.{OUTPUT_FORMAT}"
        if OUTPUT_FORMAT == 'csv':
            kpi_df.to_csv(kpi_output_path, index=False)
        else:
            kpi_df.to_excel(kpi_output_path, index=False)
        logger.info(f"KPIs exported to {kpi_output_path}")
        
        # Export AI insights
        if ai_analysis:
            insights_path = OUTPUT_DIR / f"ai_insights_{timestamp}.txt"
            with open(insights_path, 'w') as f:
                f.write(ai_analysis['summary'])
            logger.info(f"AI insights exported to {insights_path}")
        
        logger.info("=" * 50)
        logger.info("Daily batch job completed successfully")
        logger.info("=" * 50)
        
        return True
        
    except Exception as e:
        logger.error(f"Error in daily batch job: {e}", exc_info=True)
        return False


def send_notification(status: bool, message: str = ""):
    """
    Send notification email about job status.
    """
    from config import SENDGRID_API_KEY, NOTIFICATION_EMAIL_FROM, NOTIFICATION_EMAIL_TO
    
    if not SENDGRID_API_KEY:
        logger.info("Email notifications not configured")
        return
    
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail
        
        subject = "✅ Daily Job Success" if status else "❌ Daily Job Failed"
        content = f"""
        Commercial View Daily Job Report
        
        Status: {'Success' if status else 'Failed'}
        Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        {message}
        """
        
        message = Mail(
            from_email=NOTIFICATION_EMAIL_FROM,
            to_emails=NOTIFICATION_EMAIL_TO,
            subject=subject,
            plain_text_content=content
        )
        
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        logger.info(f"Notification sent: {response.status_code}")
        
    except Exception as e:
        logger.error(f"Could not send notification: {e}")


def job_with_notification():
    """Wrapper to run job and send notification."""
    status = run_daily_job()
    send_notification(status)


def start_scheduler():
    """
    Start the job scheduler.
    Runs the job at the configured time daily.
    """
    logger.info(f"Scheduling daily job at {DAILY_JOB_TIME}")
    
    # Schedule the job
    schedule.every().day.at(DAILY_JOB_TIME).do(job_with_notification)
    
    logger.info("Scheduler started. Press Ctrl+C to stop.")
    
    # Run immediately on startup (optional)
    # job_with_notification()
    
    # Keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


def run_job_now():
    """
    Run the job immediately (for testing or manual execution).
    """
    job_with_notification()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--now":
        # Run immediately
        run_job_now()
    else:
        # Start scheduler
        start_scheduler()
