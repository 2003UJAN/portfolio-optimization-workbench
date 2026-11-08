
import streamlit as st
import pandas as pd
import plotly.express as px

from modules.ui import apply_theme, page_header

from modules.portfolio_engine import calculate_portfolio_returns

from modules.risk_engine import (
    calculate_risk_metrics,
    calculate_rolling_volatility
)


st.set_page_config(
    page_title="Risk Analytics",
    page_icon="🛡️",
    layout="wide"
)

apply_theme()

page_header(
    "Risk Analytics",
    "Analyze downside exposure, portfolio volatility and market sensitivity."
)

st.success("Risk Analytics page loaded successfully.")


# PORTFOLIO DATA

returns = st.session_state.get("portfolio_returns")
weights = st.session_state.get("portfolio_weights")

if returns is None or weights is None:
    st.warning("Please configure your portfolio in Portfolio Builder.")
    st.stop()

assets = [
    ticker for ticker in weights.index
    if ticker in returns.columns
]

if len(assets) < 2:
    st.warning("At least two assets are required.")
    st.stop()


# CONFIGURATION

st.subheader("1. Risk Configuration")

selected = st.multiselect(
    "Select portfolio assets",
    assets,
    default=assets
)

confidence = st.selectbox(
    "VaR / CVaR Confidence Level",
    [0.90, 0.95, 0.99],
    index=1
)

if len(selected) < 2:
    st.warning("Select at least two assets.")
    st.stop()


selected_weights = weights.reindex(selected)
selected_weights = selected_weights / selected_weights.sum()

try:

    portfolio_returns = calculate_portfolio_returns(
        returns[selected].dropna(),
        selected_weights
    )

except Exception as e:

    st.error(f"Portfolio return calculation failed: {e}")
    st.stop()


# BENCHMARK

benchmark = st.session_state.get("portfolio_benchmark")

benchmark_returns = None

if benchmark is not None:

    benchmark_returns = (
        benchmark.pct_change()
        .reindex(portfolio_returns.index)
        .dropna()
    )


# RISK CALCULATIONS

try:

    metrics = calculate_risk_metrics(
        portfolio_returns,
        benchmark_returns=benchmark_returns,
        confidence_level=confidence
    )

except Exception as e:

    st.error(f"Risk calculation failed: {e}")
    st.stop()


# RISK DASHBOARD

st.divider()

st.subheader("2. Portfolio Risk Dashboard")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Value at Risk",
    f"{metrics['Value at Risk (VaR)']:.2%}"
)

c2.metric(
    "Conditional VaR",
    f"{metrics['Conditional VaR (CVaR)']:.2%}"
)

c3.metric(
    "Maximum Drawdown",
    f"{metrics['Maximum Drawdown']:.2%}"
)

c4.metric(
    "Annualized Volatility",
    f"{metrics['Annualized Volatility']:.2%}"
)

if "Portfolio Beta" in metrics:

    st.metric(
        "Portfolio Beta",
        f"{metrics['Portfolio Beta']:.2f}"
    )


# RETURN DISTRIBUTION

st.divider()

st.subheader("3. Return Distribution and VaR")

fig = px.histogram(
    portfolio_returns,
    nbins=50,
    title="Distribution of Daily Portfolio Returns"
)

fig.add_vline(
    x=-metrics["Value at Risk (VaR)"],
    line_dash="dash",
    line_color="#fb7185",
    annotation_text="VaR"
)

fig.update_layout(
    template="plotly_dark",
    height=420
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ROLLING VOLATILITY

st.divider()

st.subheader("4. Rolling Volatility")

rolling_volatility = calculate_rolling_volatility(
    portfolio_returns,
    window=30
)

volatility_fig = px.line(
    rolling_volatility,
    title="30-Day Rolling Annualized Volatility"
)

volatility_fig.update_layout(
    template="plotly_dark",
    height=400,
    yaxis_tickformat=".0%"
)

st.plotly_chart(
    volatility_fig,
    use_container_width=True
)


# DRAWDOWN

st.divider()

st.subheader("5. Drawdown Analysis")

wealth = (1 + portfolio_returns).cumprod()

drawdown = wealth / wealth.cummax() - 1

drawdown_fig = px.area(
    drawdown,
    title="Portfolio Drawdown Over Time"
)

drawdown_fig.update_traces(
    line_color="#fb7185",
    fillcolor="rgba(251,113,133,.18)"
)

drawdown_fig.update_layout(
    template="plotly_dark",
    height=400,
    yaxis_tickformat=".0%"
)

st.plotly_chart(
    drawdown_fig,
    use_container_width=True
)


# EXPORT

st.divider()

st.download_button(
    "Download Risk Metrics",
    pd.DataFrame([metrics]).to_csv(index=False),
    "portfolio_risk_metrics.csv",
    "text/csv"
)
