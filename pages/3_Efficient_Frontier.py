
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from modules.ui import apply_theme

from modules.efficient_frontier import (
    generate_efficient_frontier,
    calculate_capital_allocation_line
)

from modules.portfolio_engine import calculate_portfolio_allocation


# PAGE CONFIGURATION

st.set_page_config(
    page_title="Efficient Frontier",
    page_icon="📈",
    layout="wide"
)

apply_theme()

st.title("Efficient Frontier")
st.caption(
    "Markowitz portfolio optimization | Risk-return analysis | Capital Allocation Line"
)

st.divider()


# LOAD PORTFOLIO DATA

returns = st.session_state.get("portfolio_returns")
weights = st.session_state.get("portfolio_weights")

if returns is None or weights is None:
    st.warning("Please download and configure your portfolio in Portfolio Builder.")
    st.stop()

assets = [
    ticker for ticker in weights.index
    if ticker in returns.columns
]

if len(assets) < 2:
    st.warning("At least two valid assets are required.")
    st.stop()


# CONFIGURATION

st.subheader("1. Frontier Configuration")

col1, col2 = st.columns(2)

with col1:
    selected_assets = st.multiselect(
        "Select stocks",
        options=assets,
        default=assets,
        key="ef_assets"
    )

with col2:
    risk_free_rate = st.number_input(
        "Annual Risk-Free Rate (%)",
        min_value=0.0,
        max_value=30.0,
        value=6.0,
        step=0.25,
        key="ef_risk_free"
    ) / 100

points = st.slider(
    "Frontier Resolution",
    min_value=10,
    max_value=100,
    value=40,
    step=5
)

if len(selected_assets) < 2:
    st.warning("Select at least two assets.")
    st.stop()


# GENERATE FRONTIER

if st.button(
    "Generate Efficient Frontier",
    type="primary",
    use_container_width=True
):

    # Clear stale results before generating new ones
    st.session_state.pop("frontier_data", None)
    st.session_state.pop("cal_data", None)
    st.session_state.pop("frontier_assets_used", None)

    try:
        selected_returns = (
            returns[selected_assets]
            .apply(pd.to_numeric, errors="coerce")
            .replace([float("inf"), float("-inf")], float("nan"))
            .dropna()
        )

        with st.spinner("Generating efficient frontier..."):

            frontier = generate_efficient_frontier(
                selected_returns,
                points=points,
                risk_free_rate=risk_free_rate
            )

            cal = calculate_capital_allocation_line(
                frontier,
                risk_free_rate=risk_free_rate,
                points=60
            )

        st.session_state["frontier_data"] = frontier
        st.session_state["cal_data"] = cal
        st.session_state["frontier_assets_used"] = selected_assets.copy()

        st.success(
            f"Successfully generated {len(frontier)} portfolios."
        )

    except Exception as e:
        st.error(f"Frontier generation failed: {e}")


# DISPLAY RESULTS

frontier = st.session_state.get("frontier_data")
cal = st.session_state.get("cal_data")

if frontier is None or frontier.empty:

    st.info("Generate the frontier to view the analysis.")

    st.stop()


# VALIDATE FRONTIER STRUCTURE

required_columns = [
    "Expected Return",
    "Volatility",
    "Sharpe Ratio",
    "Weights"
]

missing_columns = [
    column for column in required_columns
    if column not in frontier.columns
]

if missing_columns:
    st.error(
        f"Frontier data is missing columns: {missing_columns}. "
        "Click Generate Efficient Frontier again."
    )
    st.stop()


# FRONTIER CHART

st.divider()
st.subheader("2. Efficient Frontier Visualization")

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=frontier["Volatility"],
        y=frontier["Expected Return"],
        mode="lines+markers",
        name="Efficient Frontier",
        line=dict(color="#38BDF8", width=3),
        marker=dict(size=7)
    )
)

if cal is not None and not cal.empty:
    fig.add_trace(
        go.Scatter(
            x=cal["Volatility"],
            y=cal["Expected Return"],
            mode="lines",
            name="Capital Allocation Line",
            line=dict(
                color="#2DD4BF",
                width=2,
                dash="dash"
            )
        )
    )

fig.update_layout(
    template="plotly_dark",
    height=520,
    title="Portfolio Risk vs Expected Return",
    xaxis_title="Annualized Volatility",
    yaxis_title="Expected Annual Return",
    xaxis_tickformat=".1%",
    yaxis_tickformat=".1%",
    hovermode="closest"
)

st.plotly_chart(fig, use_container_width=True)


# FRONTIER SUMMARY

st.divider()
st.subheader("3. Frontier Summary")

c1, c2, c3 = st.columns(3)

c1.metric("Portfolios Generated", len(frontier))
c2.metric("Minimum Volatility", f"{frontier['Volatility'].min():.2%}")
c3.metric("Maximum Expected Return", f"{frontier['Expected Return'].max():.2%}")


# OPTIMAL PORTFOLIO SELECTION

st.divider()
st.subheader("4. Select Optimal Portfolio")

objective = st.selectbox(
    "Portfolio Optimization Objective",
    [
        "Maximum Sharpe",
        "Minimum Volatility",
        "Maximum Return"
    ],
    key="ef_objective"
)

try:

    # Select directly from the DataFrame
    if objective == "Maximum Sharpe":
        chosen = frontier.loc[
            frontier["Sharpe Ratio"].idxmax()
        ]

    elif objective == "Minimum Volatility":
        chosen = frontier.loc[
            frontier["Volatility"].idxmin()
        ]

    else:
        chosen = frontier.loc[
            frontier["Expected Return"].idxmax()
        ]

    expected_return = float(chosen["Expected Return"])
    volatility = float(chosen["Volatility"])
    sharpe = float(chosen["Sharpe Ratio"])

    chosen_weights = pd.Series(
        chosen["Weights"],
        dtype=float
    )

    c1, c2, c3 = st.columns(3)

    c1.metric("Expected Annual Return", f"{expected_return:.2%}")
    c2.metric("Annualized Volatility", f"{volatility:.2%}")
    c3.metric("Sharpe Ratio", f"{sharpe:.3f}")

    # ALLOCATION

    st.subheader("5. Optimal Portfolio Allocation")

    allocation = calculate_portfolio_allocation(
        chosen_weights
    )

    col1, col2 = st.columns(2)

    with col1:
        st.dataframe(
            allocation,
            use_container_width=True,
            hide_index=True
        )

    with col2:
        pie = px.pie(
            allocation,
            names="Ticker",
            values="Weight",
            hole=0.55,
            title="Optimal Asset Allocation"
        )

        pie.update_layout(
            template="plotly_dark",
            height=420
        )

        st.plotly_chart(pie, use_container_width=True)

    # APPLY WEIGHTS

    if st.button(
        "Apply Optimized Weights",
        type="primary",
        use_container_width=True
    ):

        st.session_state["portfolio_weights"] = chosen_weights
        st.session_state["selected_assets"] = list(chosen_weights.index)

        st.success("Optimized portfolio weights saved.")

except Exception as e:

    st.error(f"Portfolio selection failed: {e}")


# EXPORT

st.divider()
st.subheader("6. Export Results")

export_data = frontier.copy()

export_data["Weights"] = export_data["Weights"].apply(str)

st.download_button(
    "Download Efficient Frontier CSV",
    data=export_data.to_csv(index=False),
    file_name="efficient_frontier.csv",
    mime="text/csv"
)
