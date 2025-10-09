"""
Visualization Module for Commercial-View

Creates interactive and static charts for portfolio analytics,
delinquency distribution, and financial trends.
"""

import logging
from typing import Optional, Dict, Any
from pathlib import Path
import pandas as pd
import numpy as np

# Plotting libraries
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    px = None
    go = None

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None

logger = logging.getLogger(__name__)

# Constants
DEFAULT_FIGURE_SIZE = (10, 6)
DEFAULT_COLOR_SCHEME = 'viridis'
ERROR_MESSAGE_EMPTY_DF = "Cannot plot: empty {}"
ERROR_MESSAGE_NO_LIBRARY = "No plotting library available"


def _ensure_output_dir(output_path: str) -> None:
    """Ensure output directory exists."""
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)


def _validate_dataframe_and_column(
    df: pd.DataFrame,
    column: str,
    df_name: str = "DataFrame"
) -> bool:
    """
    Validate DataFrame and column existence.
    
    Args:
        df: DataFrame to validate
        column: Column name to check
        df_name: Name of DataFrame for error messages
        
    Returns:
        True if valid, False otherwise
    """
    if df is None or df.empty:
        logger.warning(ERROR_MESSAGE_EMPTY_DF.format(df_name))
        return False
    
    if column not in df.columns:
        logger.warning(f"Column '{column}' not found in {df_name}")
        return False
    
    return True


def _validate_dataframe_and_columns(
    df: pd.DataFrame,
    columns: list,
    df_name: str = "DataFrame"
) -> bool:
    """
    Validate DataFrame and multiple columns existence.
    
    Args:
        df: DataFrame to validate
        columns: List of column names to check
        df_name: Name of DataFrame for error messages
        
    Returns:
        True if valid, False otherwise
    """
    if df is None or df.empty:
        logger.warning(ERROR_MESSAGE_EMPTY_DF.format(df_name))
        return False
    
    missing_cols = [col for col in columns if col not in df.columns]
    if missing_cols:
        logger.warning(f"Required columns not found in {df_name}: {missing_cols}")
        return False
    
    return True


def _create_plotly_bar_chart(
    dist: pd.DataFrame,
    output_path: Optional[str]
) -> Any:
    """Create Plotly bar chart for delinquency distribution."""
    fig = px.bar(
        dist,
        x='Bucket',
        y='Loans',
        title="Loan Delinquency Distribution",
        labels={'Loans': 'Number of Loans'},
        color='Loans',
        color_continuous_scale='Reds'
    )
    
    fig.update_layout(
        xaxis_title="Delinquency Bucket",
        yaxis_title="Number of Loans",
        showlegend=False,
        height=500
    )

    if output_path:
        _ensure_output_dir(output_path)
        fig.write_html(output_path)
        logger.info(f"✅ Chart saved to {output_path}")

    return fig


def _create_matplotlib_bar_chart(
    dist: pd.DataFrame,
    output_path: Optional[str]
) -> Any:
    """Create Matplotlib bar chart for delinquency distribution."""
    fig, ax = plt.subplots(figsize=DEFAULT_FIGURE_SIZE)
    
    bars = ax.bar(dist['Bucket'], dist['Loans'], color='crimson', alpha=0.7)
    ax.set_xlabel('Delinquency Bucket')
    ax.set_ylabel('Number of Loans')
    ax.set_title('Loan Delinquency Distribution')
    ax.tick_params(axis='x', rotation=45)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.,
            height,
            f'{int(height)}',
            ha='center',
            va='bottom'
        )
    
    plt.tight_layout()

    if output_path:
        _ensure_output_dir(output_path)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        logger.info(f"✅ Chart saved to {output_path}")

    return fig


def plot_delinquency_distribution(
    loan_df: pd.DataFrame,
    bucket_column: str = 'delinquency_bucket',
    output_path: Optional[str] = None,
    interactive: bool = True
) -> Optional[Any]:
    """
    Create bar chart of delinquency bucket distribution.
    
    Args:
        loan_df: DataFrame with loan data
        bucket_column: Column containing delinquency buckets
        output_path: Optional path to save chart
        interactive: If True, use Plotly; else use Matplotlib
        
    Returns:
        Figure object or None
    """
    if not _validate_dataframe_and_column(loan_df, bucket_column, "loan DataFrame"):
        return None

    try:
        # Calculate distribution
        dist = loan_df[bucket_column].value_counts().reset_index()
        dist.columns = ['Bucket', 'Loans']
        dist = dist.sort_values('Loans', ascending=False)

        if interactive and PLOTLY_AVAILABLE:
            return _create_plotly_bar_chart(dist, output_path)
        
        if MATPLOTLIB_AVAILABLE:
            return _create_matplotlib_bar_chart(dist, output_path)
        
        logger.error(ERROR_MESSAGE_NO_LIBRARY)
        return None

    except Exception as e:
        logger.error(f"Error generating delinquency distribution plot: {e}")
        return None


def _create_plotly_line_chart(
    df: pd.DataFrame,
    date_column: str,
    value_column: str,
    output_path: Optional[str]
) -> Any:
    """Create Plotly line chart for portfolio trend."""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df[date_column],
        y=df[value_column],
        mode='lines+markers',
        name='Portfolio Outstanding',
        line={'color': '#1f77b4', 'width': 2},
        marker={'size': 6}
    ))
    
    fig.update_layout(
        title="Portfolio Outstanding Over Time",
        xaxis_title="Date",
        yaxis_title="Outstanding Principal",
        hovermode='x unified',
        height=500
    )

    if output_path:
        _ensure_output_dir(output_path)
        fig.write_html(output_path)
        logger.info(f"✅ Chart saved to {output_path}")

    return fig


def _create_matplotlib_line_chart(
    df: pd.DataFrame,
    date_column: str,
    value_column: str,
    output_path: Optional[str]
) -> Any:
    """Create Matplotlib line chart for portfolio trend."""
    fig, ax = plt.subplots(figsize=DEFAULT_FIGURE_SIZE)
    
    ax.plot(
        df[date_column],
        df[value_column],
        marker='o',
        linewidth=2,
        markersize=6,
        color='#1f77b4'
    )
    
    ax.set_xlabel('Date')
    ax.set_ylabel('Outstanding Principal')
    ax.set_title('Portfolio Outstanding Over Time')
    ax.grid(True, alpha=0.3)
    
    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    plt.xticks(rotation=45)
    
    plt.tight_layout()

    if output_path:
        _ensure_output_dir(output_path)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        logger.info(f"✅ Chart saved to {output_path}")

    return fig


def plot_portfolio_trend(
    financials_df: pd.DataFrame,
    date_column: str = 'date',
    value_column: str = 'portfolio_outstanding',
    output_path: Optional[str] = None,
    interactive: bool = True
) -> Optional[Any]:
    """
    Plot portfolio outstanding trend over time.
    
    Args:
        financials_df: DataFrame with time series data
        date_column: Column containing dates
        value_column: Column with values to plot
        output_path: Optional path to save chart
        interactive: If True, use Plotly; else use Matplotlib
        
    Returns:
        Figure object or None
    """
    if not _validate_dataframe_and_columns(
        financials_df,
        [date_column, value_column],
        "financials DataFrame"
    ):
        return None

    try:
        # Prepare data
        df = financials_df.copy()
        df[date_column] = pd.to_datetime(df[date_column])
        df = df.sort_values(date_column)

        if interactive and PLOTLY_AVAILABLE:
            return _create_plotly_line_chart(df, date_column, value_column, output_path)
        
        if MATPLOTLIB_AVAILABLE:
            return _create_matplotlib_line_chart(df, date_column, value_column, output_path)
        
        logger.error(ERROR_MESSAGE_NO_LIBRARY)
        return None

    except Exception as e:
        logger.error(f"Error generating portfolio trend plot: {e}")
        return None


def plot_risk_heatmap(
    loan_df: pd.DataFrame,
    risk_column: str = 'risk_score',
    bucket_column: str = 'delinquency_bucket',
    output_path: Optional[str] = None
) -> Optional[Any]:
    """
    Create heatmap of risk distribution across delinquency buckets.
    
    Args:
        loan_df: DataFrame with loan data
        risk_column: Column with risk scores
        bucket_column: Column with delinquency buckets
        output_path: Optional path to save chart
        
    Returns:
        Figure object or None
    """
    if not PLOTLY_AVAILABLE:
        logger.warning("Plotly not available for heatmap")
        return None

    if not _validate_dataframe_and_column(loan_df, bucket_column, "loan DataFrame"):
        return None

    try:
        # Create pivot table
        pivot = loan_df.pivot_table(
            values=risk_column,
            index=bucket_column,
            aggfunc='mean'
        ).reset_index()

        fig = px.imshow(
            [pivot[risk_column].values],
            labels={'x': "Risk Score", 'y': "Bucket", 'color': "Average Risk"},
            x=pivot[bucket_column].values,
            color_continuous_scale='RdYlGn_r',
            title="Risk Distribution by Delinquency Bucket"
        )

        if output_path:
            _ensure_output_dir(output_path)
            fig.write_html(output_path)
            logger.info(f"✅ Heatmap saved to {output_path}")

        return fig

    except Exception as e:
        logger.error(f"Error generating risk heatmap: {e}")
        return None


def create_dashboard_summary(
    kpis: Dict[str, Any],
    output_path: Optional[str] = None
) -> Optional[Any]:
    """
    Create summary dashboard with key metrics.
    
    Args:
        kpis: Dictionary with KPI values
        output_path: Optional path to save chart
        
    Returns:
        Figure object or None
    """
    if not PLOTLY_AVAILABLE:
        logger.warning("Plotly not available for dashboard")
        return None

    try:
        from plotly.subplots import make_subplots

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Portfolio Outstanding', 'Active Clients', 'NPL Rate', 'Weighted APR'),
            specs=[[{'type': 'indicator'}, {'type': 'indicator'}],
                   [{'type': 'indicator'}, {'type': 'indicator'}]]
        )

        # Add indicators
        fig.add_trace(go.Indicator(
            mode="number+delta",
            value=kpis.get('total_portfolio_outstanding', 0),
            title={'text': "Portfolio Outstanding"},
            domain={'x': [0, 1], 'y': [0, 1]}
        ), row=1, col=1)

        fig.add_trace(go.Indicator(
            mode="number",
            value=kpis.get('number_of_loans', 0),
            title={'text': "Active Loans"},
        ), row=1, col=2)

        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=kpis.get('npl_ratio', 0),
            title={'text': "NPL Ratio (%)"},
            gauge={'axis': {'range': [None, 10]},
                   'bar': {'color': "darkred"},
                   'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 5}}
        ), row=2, col=1)

        fig.add_trace(go.Indicator(
            mode="number",
            value=kpis.get('average_interest_rate', 0),
            title={'text': "Avg Interest Rate (%)"},
        ), row=2, col=2)

        fig.update_layout(height=600, title_text="Portfolio Dashboard")

        if output_path:
            _ensure_output_dir(output_path)
            fig.write_html(output_path)
            logger.info(f"✅ Dashboard saved to {output_path}")

        return fig

    except Exception as e:
        logger.error(f"Error creating dashboard: {e}")
        return None
