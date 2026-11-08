import streamlit as st

st.set_page_config(
    page_title="Portfolio Optimization",
    page_icon="⚖️",
    layout="wide"
)

st.title("Portfolio Optimization")

import streamlit as st
import pandas as pd
import plotly.express as px

from modules.ui import apply_theme, page_header, require_portfolio

from modules.optimization_engine import optimize_portfolio

from modules.portfolio_engine import (
    calculate_portfolio_statistics,
    calculate_portfolio_allocation
)


st.set_page_config(
    page_title="Portfolio Optimization",
    page_icon="⚖️",
    layout="wide"
)

apply_theme()

page_header(
    "Portfolio Optimization",
    "Optimize portfolio weights using quantitative allocation strategies."
)


_, returns, current_weights = require_portfolio()

assets = [
    x for x in current_weights.index
    if x in returns.columns
]

selected = st.multiselect(
    "Select assets",
    assets,
    default=assets
)

if len(selected) < 2:
    st.warning("Select at least two assets.")
    st.stop()


col1, col2 = st.columns(2)

with col1:

    method = st.selectbox(
        "Optimization objective",
        [
            "Maximum Sharpe",
            "Minimum Variance",
            "Risk Parity"
        ]
    )

with col2:

    risk_free_rate = st.number_input(
        "Annual risk-free rate (%)",
        min_value=0.0,
        max_value=30.0,
        value=6.0,
        step=0.25
    ) / 100


st.caption(
    "Long-only optimization: each asset weight is between 0% and 100%, "
    "and all portfolio weights sum to 100%."
)


if st.button(
    "Run Portfolio Optimization",
    type="primary",
    use_container_width=True
):

    try:

        selected_returns = returns[selected].dropna()

        with st.spinner("Optimizing portfolio..."):

            optimized_weights = optimize_portfolio(
                selected_returns,
                method=method,
                risk_free_rate=risk_free_rate
            )

            optimized_weights = pd.Series(
                optimized_weights,
                dtype=float
            )

            optimized_weights = optimized_weights.reindex(
                selected
            ).fillna(0)

            optimized_weights = (
                optimized_weights / optimized_weights.sum()
            )

            stats = calculate_portfolio_statistics(
                selected_returns,
                optimized_weights,
                risk_free_rate=risk_free_rate
            )

            st.session_state.optimized_weights = optimized_weights
            st.session_state.optimized_stats = stats
            st.session_state.optimized_method = method

        st.success("Portfolio optimization completed.")

    except Exception as e:

        st.error(f"Optimization failed: {e}")


optimized_weights = st.session_state.get(
    "optimized_weights"
)

if optimized_weights is not None:

    st.divider()

    st.subheader("Optimized Portfolio Allocation")

    stats = st.session_state.get(
        "optimized_stats",
        {}
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Expected Annual Return",
        f"{stats.get('Expected Annual Return', 0):.2%}"
    )

    col2.metric(
        "Annualized Volatility",
        f"{stats.get('Annualised Volatility', 0):.2%}"
    )

    col3.metric(
        "Sharpe Ratio",
        f"{stats.get('Sharpe Ratio', 0):.2f}"
    )

    allocation = calculate_portfolio_allocation(
        optimized_weights
    )

    fig = px.bar(
        allocation,
        x="Ticker",
        y="Weight",
        color="Ticker",
        title="Optimized Portfolio Weights"
    )

    fig.update_layout(
        template="plotly_dark",
        height=400,
        showlegend=False,
        yaxis_tickformat=".0%"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.dataframe(
        allocation,
        use_container_width=True,
        hide_index=True
    )

    if st.button(
        "Apply Optimized Weights",
        type="primary"
    ):

        st.session_state.portfolio_weights = (
            optimized_weights
        )

        st.session_state.selected_assets = (
            list(optimized_weights.index)
        )

        st.success(
            "Optimized weights saved as the active portfolio."
        )

else:

    st.info(
        "Run an optimization to view the recommended allocation."
    )
