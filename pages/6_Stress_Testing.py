
import streamlit as st
import pandas as pd
import plotly.express as px

from modules.ui import apply_theme, page_header

from modules.stress_testing import (
    calculate_stress_scenarios,
    calculate_custom_asset_shock,
    calculate_historical_stress,
    calculate_volatility_shock
)

from modules.portfolio_engine import calculate_covariance_matrix


st.set_page_config(
    page_title="Stress Testing",
    page_icon="⚡",
    layout="wide"
)

apply_theme()

page_header(
    "Stress Testing",
    "Evaluate portfolio resilience under adverse market conditions and hypothetical shocks."
)

st.success("Stress Testing page loaded successfully.")


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

st.subheader("1. Stress Test Configuration")

selected = st.multiselect(
    "Select portfolio holdings",
    assets,
    default=assets
)

if len(selected) < 2:
    st.warning("Select at least two assets.")
    st.stop()

selected_weights = weights.reindex(selected)
selected_weights = selected_weights / selected_weights.sum()

initial_investment = st.number_input(
    "Portfolio Value (₹)",
    min_value=1000,
    value=1000000,
    step=50000
)


# MARKET-WIDE SCENARIOS

st.divider()

st.subheader("2. Market-Wide Stress Scenarios")

try:

    scenarios = calculate_stress_scenarios(
        selected_weights,
        initial_investment=initial_investment
    )

    st.dataframe(
        scenarios,
        use_container_width=True,
        hide_index=True
    )

    fig = px.bar(
        scenarios,
        x="Scenario",
        y="Profit / Loss",
        color="Profit / Loss",
        color_continuous_scale=[
            "#fb7185",
            "#64748b",
            "#2dd4bf"
        ],
        title="Portfolio Profit / Loss Under Market Shocks"
    )

    fig.update_layout(
        template="plotly_dark",
        height=400
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

except Exception as e:

    st.error(f"Market-wide stress test failed: {e}")


# CUSTOM ASSET SHOCK

st.divider()

st.subheader("3. Asset-Specific Stress Scenarios")

st.caption(
    "Specify a hypothetical percentage return shock for each asset."
)

shock_columns = st.columns(
    min(3, len(selected))
)

asset_shocks = {}

for i, ticker in enumerate(selected):

    with shock_columns[i % len(shock_columns)]:

        asset_shocks[ticker] = st.number_input(
            f"{ticker} Shock (%)",
            min_value=-100.0,
            max_value=200.0,
            value=-10.0,
            step=1.0,
            key=f"shock_{ticker}"
        ) / 100


try:

    custom = calculate_custom_asset_shock(
        selected_weights,
        asset_shocks,
        initial_investment=initial_investment
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Portfolio Return",
        f"{custom['Portfolio Return']:.2%}"
    )

    c2.metric(
        "Profit / Loss",
        f"₹{custom['Profit / Loss']:,.0f}"
    )

    c3.metric(
        "Stressed Portfolio Value",
        f"₹{custom['Ending Portfolio Value']:,.0f}"
    )

except Exception as e:

    st.error(f"Custom stress test failed: {e}")


# HISTORICAL STRESS

st.divider()

st.subheader("4. Historical Rolling Stress")

window = st.selectbox(
    "Stress Window (Trading Days)",
    [5, 10, 21, 42, 63],
    index=2
)

try:

    historical = calculate_historical_stress(
        returns[selected],
        selected_weights,
        window=window
    )

    if not historical.empty:

        worst = historical.iloc[0]

        st.metric(
            f"Worst Historical {window}-Day Return",
            f"{worst['Portfolio Return']:.2%}"
        )

        hist_fig = px.bar(
            historical.head(15),
            x="Date",
            y="Portfolio Return",
            title=f"15 Worst Rolling {window}-Day Returns"
        )

        hist_fig.update_layout(
            template="plotly_dark",
            height=380,
            yaxis_tickformat=".0%"
        )

        st.plotly_chart(
            hist_fig,
            use_container_width=True
        )

except Exception as e:

    st.error(f"Historical stress calculation failed: {e}")


# VOLATILITY SHOCK

st.divider()

st.subheader("5. Volatility Shock Analysis")

multiplier = st.slider(
    "Volatility Multiplier",
    1.0,
    4.0,
    2.0,
    0.25
)

try:

    covariance = calculate_covariance_matrix(
        returns[selected].dropna(),
        annualize=True
    )

    result = calculate_volatility_shock(
        selected_weights,
        covariance,
        volatility_multiplier=multiplier
    )

    c1, c2 = st.columns(2)

    c1.metric(
        "Base Annualized Volatility",
        f"{result['Base Volatility']:.2%}"
    )

    c2.metric(
        "Stressed Annualized Volatility",
        f"{result['Stressed Volatility']:.2%}"
    )

except Exception as e:

    st.error(f"Volatility shock calculation failed: {e}")

