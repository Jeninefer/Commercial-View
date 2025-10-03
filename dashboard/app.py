"""
Streamlit-based interactive dashboard for Commercial View Platform.
Includes role-based access control and data visualizations.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from typing import Dict, Any, Optional

from config import BRAND_COLORS, ENABLE_VIEW_ONLY_ROLE
from analysis.kpi_calculator import KPICalculator, calculate_portfolio_kpis
from optimization.disbursement_optimizer import DisbursementOptimizer, optimize_disbursements
from ingestion.sample_data_loader import load_sample_data


# Page configuration
st.set_page_config(
    page_title="Commercial View - ABACO",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply ABACO brand colors
CUSTOM_CSS = f"""
<style>
    .main {{
        background-color: {BRAND_COLORS['contrast_white']};
    }}
    .stButton>button {{
        background-color: {BRAND_COLORS['primary_purple']};
        color: {BRAND_COLORS['contrast_white']};
    }}
    .metric-card {{
        background-color: {BRAND_COLORS['neutral_grey_light']};
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid {BRAND_COLORS['primary_purple']};
    }}
    h1, h2, h3 {{
        color: {BRAND_COLORS['primary_dark']};
    }}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


class UserRole:
    """User role definitions."""
    ADMIN = "admin"
    KAM = "kam"
    VIEWER = "viewer"


def check_authentication() -> Optional[Dict[str, str]]:
    """
    Simple authentication check.
    In production, integrate with proper auth system.
    """
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    if st.session_state.user is None:
        st.sidebar.title("🔐 Login")
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        
        if st.sidebar.button("Login"):
            # Simplified auth - in production, use proper authentication
            if username and password:
                # Default: admin for demo, KAM for specific users
                role = UserRole.KAM if username.startswith("kam") else UserRole.ADMIN
                st.session_state.user = {
                    'username': username,
                    'role': role,
                    'kam_id': username if role == UserRole.KAM else None
                }
                st.rerun()
        
        st.info("👋 Please login to access the dashboard")
        return None
    
    return st.session_state.user


def filter_data_by_role(data: pd.DataFrame, user: Dict[str, str]) -> pd.DataFrame:
    """
    Filter data based on user role.
    KAMs can only see their assigned clients.
    """
    if user['role'] == UserRole.ADMIN:
        return data
    
    if user['role'] == UserRole.KAM and 'kam' in data.columns:
        return data[data['kam'] == user['kam_id']]
    
    return data


def render_kpi_cards(kpis: Dict[str, Any]):
    """Render KPI metrics as cards."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Portfolio APR",
            f"{kpis['portfolio_apr']*100:.2f}%",
            delta=None
        )
    
    with col2:
        st.metric(
            "Active Loans",
            f"{kpis['active_loans']:,}",
            delta=None
        )
    
    with col3:
        st.metric(
            "Total Principal",
            f"${kpis['total_principal']:,.0f}",
            delta=None
        )
    
    with col4:
        st.metric(
            "Avg DPD",
            f"{kpis['avg_dpd']:.1f} days",
            delta=None,
            delta_color="inverse"
        )


def render_portfolio_charts(loan_tape: pd.DataFrame):
    """Render portfolio visualization charts."""
    col1, col2 = st.columns(2)
    
    with col1:
        # Sector distribution
        if 'sector' in loan_tape.columns:
            sector_data = loan_tape[loan_tape['status'] == 'active'].groupby('sector')['principal'].sum().reset_index()
            fig = px.pie(
                sector_data,
                values='principal',
                names='sector',
                title='Portfolio Distribution by Sector',
                color_discrete_sequence=px.colors.sequential.Purples
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Status distribution
        if 'status' in loan_tape.columns:
            status_data = loan_tape.groupby('status').size().reset_index(name='count')
            fig = px.bar(
                status_data,
                x='status',
                y='count',
                title='Loans by Status',
                color='status',
                color_discrete_map={
                    'active': BRAND_COLORS['primary_purple'],
                    'paid': BRAND_COLORS['neutral_grey_mid'],
                    'overdue': '#FF6B6B'
                }
            )
            st.plotly_chart(fig, use_container_width=True)


def render_disbursement_optimizer(loan_tape: pd.DataFrame, requests: pd.DataFrame):
    """Render disbursement optimization interface."""
    st.header("💰 Disbursement Optimizer")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Input Parameters")
        available_cash = st.number_input(
            "Available Cash ($)",
            min_value=0.0,
            value=1000000.0,
            step=50000.0,
            format="%.2f"
        )
        
        optimization_method = st.selectbox(
            "Optimization Method",
            ["greedy", "lp"],
            help="Greedy is faster, LP is more optimal"
        )
        
        if st.button("🚀 Generate Recommendations", type="primary"):
            with st.spinner("Optimizing disbursements..."):
                result = optimize_disbursements(
                    requests,
                    loan_tape,
                    available_cash,
                    method=optimization_method
                )
                st.session_state.optimization_result = result
    
    with col2:
        if 'optimization_result' in st.session_state:
            result = st.session_state.optimization_result
            
            st.subheader("📊 Recommendation Summary")
            
            # Summary metrics
            metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
            with metrics_col1:
                st.metric("Loans to Approve", result['num_loans'])
            with metrics_col2:
                st.metric("Total Disbursement", f"${result['total_disbursement']:,.0f}")
            with metrics_col3:
                st.metric("Cash Utilization", f"{result['cash_utilization']*100:.1f}%")
            
            # Recommended loans table
            st.subheader("Recommended Loans")
            if len(result['selected_loans']) > 0:
                display_df = result['selected_loans'][['request_id', 'client_name', 'requested_amount', 'proposed_apr', 'proposed_term']]
                display_df['proposed_apr'] = display_df['proposed_apr'].apply(lambda x: f"{x*100:.2f}%")
                st.dataframe(display_df, use_container_width=True)
                
                # Export options
                csv = result['selected_loans'].to_csv(index=False)
                st.download_button(
                    "📥 Download Recommendations (CSV)",
                    csv,
                    "disbursement_recommendations.csv",
                    "text/csv"
                )
            else:
                st.warning("No loans recommended with current constraints.")


def render_ai_insights():
    """Render AI-generated insights section."""
    st.header("🤖 AI-Powered Insights")
    
    st.info("💡 AI analysis provides multi-perspective insights from different stakeholder viewpoints.")
    
    # Placeholder for AI insights
    with st.expander("📈 Executive Perspective (CEO)"):
        st.write("""
        **Strategic Observations:**
        - Portfolio showing healthy growth trajectory
        - Diversification across sectors reduces systemic risk
        - Consider expanding into higher-margin segments
        
        **Recommendations:**
        - Maintain current growth rate while monitoring quality metrics
        - Explore strategic partnerships in underserved sectors
        """)
    
    with st.expander("💰 Financial Perspective (CFO)"):
        st.write("""
        **Financial Health:**
        - APR margins within target range
        - Cash flow management optimal
        - DPD levels acceptable but monitor closely
        
        **Recommendations:**
        - Implement stricter credit criteria for new clients
        - Consider securitization for portfolio liquidity
        """)
    
    with st.expander("📊 Data Perspective (BI Analyst)"):
        st.write("""
        **Data Insights:**
        - Concentration risk within acceptable limits
        - Seasonal patterns detected in disbursement requests
        - Correlation between sector and default rates
        
        **Recommendations:**
        - Enhance predictive models with additional data points
        - Implement real-time monitoring dashboards
        """)


def main():
    """Main dashboard application."""
    
    # Authentication
    user = check_authentication()
    if user is None:
        return
    
    # Sidebar
    st.sidebar.title("Commercial View")
    st.sidebar.markdown(f"**User:** {user['username']}")
    st.sidebar.markdown(f"**Role:** {user['role'].upper()}")
    
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Navigation
    page = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Disbursement Optimizer", "AI Insights", "Data Management"]
    )
    
    # Load data
    if 'data' not in st.session_state:
        with st.spinner("Loading data..."):
            st.session_state.data = load_sample_data()
    
    data = st.session_state.data
    loan_tape = filter_data_by_role(data['loan_tape'], user)
    
    # Main content
    st.title("💼 Commercial View Dashboard")
    st.markdown(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    
    if page == "Dashboard":
        # KPIs
        st.header("📊 Key Performance Indicators")
        kpis = calculate_portfolio_kpis(loan_tape)
        render_kpi_cards(kpis)
        
        st.markdown("---")
        
        # Charts
        render_portfolio_charts(loan_tape)
        
        # Detailed metrics
        with st.expander("📋 Detailed Metrics"):
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Rotation Speed", f"{kpis['rotation_speed_days']:.0f} days")
                st.metric("Client Concentration", f"{kpis['client_concentration']*100:.1f}%")
            with col2:
                st.metric("Sector Concentration", f"{kpis['sector_concentration']*100:.1f}%")
                st.metric("Overdue Ratio", f"{kpis['overdue_ratio']*100:.1f}%")
    
    elif page == "Disbursement Optimizer":
        if user['role'] == UserRole.KAM and ENABLE_VIEW_ONLY_ROLE:
            st.warning("⚠️ You don't have permission to access the Disbursement Optimizer.")
        else:
            render_disbursement_optimizer(loan_tape, data['disbursement_requests'])
    
    elif page == "AI Insights":
        render_ai_insights()
    
    elif page == "Data Management":
        st.header("📁 Data Management")
        
        tab1, tab2, tab3 = st.tabs(["Loan Tape", "Disbursement Requests", "Clients"])
        
        with tab1:
            st.dataframe(loan_tape, use_container_width=True)
        
        with tab2:
            st.dataframe(data['disbursement_requests'], use_container_width=True)
        
        with tab3:
            clients = filter_data_by_role(data['clients'], user)
            st.dataframe(clients, use_container_width=True)


if __name__ == "__main__":
    main()
