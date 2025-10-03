#!/usr/bin/env python3
"""
Main entry point for Commercial View Platform.
Demonstrates core functionality and workflows.
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config import validate_config, get_config_summary
from ingestion import load_sample_data
from analysis import calculate_portfolio_kpis, analyze_data
from optimization import optimize_disbursements


def print_banner():
    """Print application banner."""
    banner = """
    ╔═══════════════════════════════════════════╗
    ║                                           ║
    ║      Commercial View Platform v1.0        ║
    ║                                           ║
    ║      Financial Analysis & Optimization    ║
    ║                                           ║
    ╚═══════════════════════════════════════════╝
    """
    print(banner)


def check_configuration():
    """Validate configuration."""
    print("🔍 Checking configuration...")
    is_valid, errors = validate_config()
    
    if not is_valid:
        print("\n⚠️  Configuration issues found:")
        for error in errors:
            print(f"   - {error}")
        print("\nPlease check your .env file.")
        return False
    
    print("✅ Configuration valid")
    
    # Show summary
    summary = get_config_summary()
    print("\n📋 Configuration Summary:")
    for key, value in summary.items():
        print(f"   {key}: {value}")
    
    return True


def run_analysis():
    """Run portfolio analysis."""
    print("\n" + "="*50)
    print("📊 PORTFOLIO ANALYSIS")
    print("="*50)
    
    # Load data
    print("\n1. Loading data...")
    data = load_sample_data()
    print(f"   ✅ Loaded {len(data['loan_tape'])} loans")
    print(f"   ✅ Loaded {len(data['disbursement_requests'])} disbursement requests")
    print(f"   ✅ Loaded {len(data['clients'])} clients")
    
    # Calculate KPIs
    print("\n2. Calculating KPIs...")
    kpis = calculate_portfolio_kpis(data['loan_tape'])
    
    print(f"\n   Portfolio Metrics:")
    print(f"   - Total Principal: ${kpis['total_principal']:,.2f}")
    print(f"   - Active Loans: {kpis['active_loans']}")
    print(f"   - Average APR: {kpis['portfolio_apr']*100:.2f}%")
    print(f"   - Rotation Speed: {kpis['rotation_speed_days']:.0f} days")
    print(f"   - Client Concentration: {kpis['client_concentration']*100:.1f}%")
    print(f"   - Sector Concentration: {kpis['sector_concentration']*100:.1f}%")
    print(f"   - Average DPD: {kpis['avg_dpd']:.1f} days")
    print(f"   - Overdue Ratio: {kpis['overdue_ratio']*100:.1f}%")
    
    return data, kpis


def run_optimization(data):
    """Run disbursement optimization."""
    print("\n" + "="*50)
    print("🎯 DISBURSEMENT OPTIMIZATION")
    print("="*50)
    
    available_cash = 1_000_000
    print(f"\n💰 Available Cash: ${available_cash:,.2f}")
    
    # Run optimization
    print("\n⚙️  Running optimization (greedy method)...")
    result = optimize_disbursements(
        requests=data['disbursement_requests'],
        portfolio=data['loan_tape'],
        available_cash=available_cash,
        method='greedy'
    )
    
    print(f"\n✨ Recommendation Summary:")
    print(f"   - Loans to Approve: {result['num_loans']}")
    print(f"   - Total Disbursement: ${result['total_disbursement']:,.2f}")
    print(f"   - Cash Utilization: {result['cash_utilization']*100:.1f}%")
    print(f"   - Remaining Cash: ${result['remaining_cash']:,.2f}")
    
    print(f"\n📈 Expected Portfolio Impact:")
    kpis = result['expected_kpis']
    print(f"   - APR Score: {kpis['apr_score']*100:.1f}%")
    print(f"   - Rotation Score: {kpis['rotation_score']*100:.1f}%")
    print(f"   - Concentration Score: {kpis['concentration_score']*100:.1f}%")
    print(f"   - Growth Score: {kpis['growth_score']*100:.1f}%")
    print(f"   - Credit Quality Score: {kpis['dpd_score']*100:.1f}%")
    print(f"   - Overall Score: {kpis['overall_score']*100:.1f}%")
    
    if result['num_loans'] > 0:
        print(f"\n📋 Top 5 Recommended Loans:")
        for i, (_, loan) in enumerate(result['selected_loans'].head(5).iterrows(), 1):
            print(f"   {i}. {loan['client_name']}: ${loan['requested_amount']:,.2f} @ {loan['proposed_apr']*100:.1f}%")
    
    return result


def run_ai_insights(kpis):
    """Generate AI insights (demo mode)."""
    print("\n" + "="*50)
    print("🤖 AI-POWERED INSIGHTS")
    print("="*50)
    
    print("\n💡 Note: Using demo mode (configure API keys for real AI analysis)")
    
    # Prepare data summary
    data_summary = {
        'kpis': kpis,
        'timestamp': '2024-01-15T08:00:00'
    }
    
    # Simulate AI analysis
    print("\n📝 Sample Executive Insights:")
    print("""
    CEO Perspective:
    - Portfolio shows healthy diversification across sectors
    - APR levels competitive but room for optimization
    - Consider strategic expansion in high-margin segments
    
    CFO Perspective:
    - Cash flow management optimal with current utilization
    - DPD levels acceptable, implement monitoring alerts
    - Concentration risk within acceptable parameters
    
    Treasury Manager Perspective:
    - Liquidity position strong
    - Rotation speed supports cash flow objectives
    - Recommend maintaining 15-20% cash buffer
    """)


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(description='Commercial View Platform')
    parser.add_argument('--mode', choices=['analysis', 'optimize', 'insights', 'all'], 
                       default='all', help='Run mode')
    parser.add_argument('--dashboard', action='store_true', 
                       help='Launch dashboard instead')
    parser.add_argument('--scheduler', action='store_true',
                       help='Start scheduler')
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Check configuration
    if not check_configuration():
        sys.exit(1)
    
    # Launch dashboard
    if args.dashboard:
        print("\n🚀 Launching dashboard...")
        import subprocess
        subprocess.run(['streamlit', 'run', 'dashboard/app.py'])
        return
    
    # Start scheduler
    if args.scheduler:
        print("\n⏰ Starting scheduler...")
        from scheduler import start_scheduler
        start_scheduler()
        return
    
    # Run analysis workflows
    data = None
    kpis = None
    
    if args.mode in ['analysis', 'all']:
        data, kpis = run_analysis()
    
    if args.mode in ['optimize', 'all']:
        if data is None:
            data, kpis = run_analysis()
        run_optimization(data)
    
    if args.mode in ['insights', 'all']:
        if kpis is None:
            data, kpis = run_analysis()
        run_ai_insights(kpis)
    
    print("\n" + "="*50)
    print("✅ Analysis complete!")
    print("\n💡 Next steps:")
    print("   - Run dashboard: python main.py --dashboard")
    print("   - Start scheduler: python main.py --scheduler")
    print("   - View docs: cat README.md")
    print("="*50 + "\n")


if __name__ == "__main__":
    main()
