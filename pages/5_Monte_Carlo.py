
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from modules.ui import apply_theme, page_header

from modules.portfolio_engine import calculate_portfolio_returns

from modules.monte_carlo import (
    simulate_portfolio_paths,
    calculate_simulation_percentiles
)


st.set_page_config(
    page_title="Monte Carlo Simulation",
    page_icon="🎲",
    layout="wide"
)

apply_theme()

page_header(
    "Monte Carlo Simulation",
    "Simulate possible future portfolio values under different market outcomes."
)

st.success("Monte Carlo page loaded successfully.")


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


# SIMULATION SETTINGS

st.subheader("1. Simulation Configuration")

selected = st.multiselect(
    "Select portfolio assets",
    assets,
    default=assets
)

c1, c2, c3 = st.columns(3)

with c1:

    initial_investment = st.number_input(
        "Initial Investment (₹)",
        min_value=1000,
        value=100000,
        step=10000
    )

with c2:

    horizon = st.selectbox(
        "Investment Horizon (Trading Days)",
        [63, 126, 252, 504, 756],
        index=2
    )

with c3:

    simulations = st.select_slider(
        "Number of Simulations",
        options=[100, 250, 500, 1000, 2000, 5000],
        value=1000
    )

seed = st.number_input(
    "Random Seed",
    min_value=0,
    value=42
)

if len(selected) < 2:
    st.warning("Select at least two assets.")
    st.stop()


# RUN SIMULATION

if st.button(
    "Run Monte Carlo Simulation",
    type="primary",
    use_container_width=True
):

    try:

        selected_weights = weights.reindex(selected)
        selected_weights = selected_weights / selected_weights.sum()

        portfolio_returns = calculate_portfolio_returns(
            returns[selected].dropna(),
            selected_weights
        )

        with st.spinner("Running Monte Carlo simulations..."):

            paths, summary = simulate_portfolio_paths(
                portfolio_returns,
                initial_investment=initial_investment,
                days=horizon,
                simulations=simulations,
                seed=int(seed)
            )

        st.session_state.mc_paths = paths
        st.session_state.mc_summary = summary

        st.success("Monte Carlo simulation completed.")

    except Exception as e:

        st.error(f"Simulation failed: {e}")


# DISPLAY RESULTS

paths = st.session_state.get("mc_paths")
summary = st.session_state.get("mc_summary")

if paths is not None and summary is not None:

    st.divider()

    st.subheader("2. Simulation Results")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Mean Final Value",
        f"₹{summary['Mean Final Value']:,.0f}"
    )

    c2.metric(
        "Median Final Value",
        f"₹{summary['Median Final Value']:,.0f}"
    )

    c3.metric(
        "5th Percentile",
        f"₹{summary['5th Percentile']:,.0f}"
    )

    c4.metric(
        "Probability of Loss",
        f"{summary['Probability of Loss']:.1%}"
    )


    # SIMULATED PATHS

    st.divider()

    st.subheader("3. Simulated Portfolio Paths")

    fig = go.Figure()

    sample_columns = list(
        paths.columns[:min(35, len(paths.columns))]
    )

    for column in sample_columns:

        fig.add_trace(
            go.Scatter(
                x=paths.index,
                y=paths[column],
                mode="lines",
                line=dict(
                    width=1,
                    color="rgba(56,189,248,.20)"
                ),
                showlegend=False
            )
        )


    percentiles = calculate_simulation_percentiles(
        paths
    )

    fig.add_trace(
        go.Scatter(
            x=percentiles.index,
            y=percentiles["95th Percentile"],
            mode="lines",
            line=dict(width=0),
            showlegend=False
        )
    )

    fig.add_trace(
        go.Scatter(
            x=percentiles.index,
            y=percentiles["5th Percentile"],
            mode="lines",
            line=dict(width=0),
            fill="tonexty",
            fillcolor="rgba(45,212,191,.13)",
            name="5th–95th Percentile Range"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=percentiles.index,
            y=percentiles["Median"],
            mode="lines",
            line=dict(
                color="#2dd4bf",
                width=3
            ),
            name="Median Path"
        )
    )

    fig.update_layout(
        template="plotly_dark",
        height=500,
        title="Monte Carlo Portfolio Value Simulation",
        xaxis_title="Trading Days",
        yaxis_title="Portfolio Value (₹)"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # FINAL VALUE DISTRIBUTION

    st.divider()

    st.subheader("4. Final Portfolio Value Distribution")

    final_values = paths.iloc[-1]

    distribution = px.histogram(
        final_values,
        nbins=50,
        title="Distribution of Simulated Final Values"
    )

    distribution.update_layout(
        template="plotly_dark",
        height=380
    )

    st.plotly_chart(
        distribution,
        use_container_width=True
    )


    st.caption(
        "GBM-style simulation assumes constant drift and volatility. "
        "It does not model jumps, changing volatility, liquidity or regime shifts."
    )

    st.download_button(
        "Download Simulation Summary",
        pd.DataFrame([summary]).to_csv(index=False),
        "monte_carlo_summary.csv",
        "text/csv"
    )

else:

    st.info(
        "Configure the simulation and click Run Monte Carlo Simulation."
    )
