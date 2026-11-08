
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from modules.ui import apply_theme, page_header

from modules.portfolio_engine import calculate_portfolio_returns

from modules.performance_engine import (
    calculate_performance_metrics,
    calculate_equity_curve
)


st.set_page_config(
    page_title="Performance Analytics",
    page_icon="🏁",
    layout="wide"
)

apply_theme()

page_header(
    "Performance Analytics",
    "Analyze portfolio growth, risk-adjusted returns and benchmark-relative performance."
)

st.success("Performance Analytics page loaded successfully.")


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

st.subheader("1. Performance Configuration")

selected = st.multiselect(
    "Select portfolio holdings",
    assets,
    default=assets
)

risk_free_rate = st.number_input(
    "Annual Risk-Free Rate (%)",
    min_value=0.0,
    max_value=30.0,
    value=6.0,
    step=0.25
) / 100

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


# BENCHMARK DATA

benchmark_prices = st.session_state.get(
    "portfolio_benchmark"
)

benchmark_returns = None

if benchmark_prices is not None:

    benchmark_returns = benchmark_prices.pct_change().dropna()


# PERFORMANCE METRICS

try:

    metrics = calculate_performance_metrics(
        portfolio_returns,
        benchmark_returns=benchmark_returns,
        risk_free_rate=risk_free_rate
    )

except Exception as e:

    st.error(f"Performance calculation failed: {e}")
    st.stop()


# SCORECARD

st.divider()

st.subheader("2. Performance Scorecard")

metric_names = [
    "CAGR",
    "Annualized Volatility",
    "Sharpe Ratio",
    "Sortino Ratio",
    "Maximum Drawdown"
]

columns = st.columns(5)

for column, name in zip(columns, metric_names):

    value = metrics.get(name, float("nan"))

    if name in [
        "CAGR",
        "Annualized Volatility",
        "Maximum Drawdown"
    ]:

        column.metric(
            name,
            f"{value:.2%}"
        )

    else:

        column.metric(
            name,
            f"{value:.2f}"
        )


# BENCHMARK METRICS

if "Information Ratio" in metrics:

    st.subheader("3. Benchmark-Relative Metrics")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Information Ratio",
        f"{metrics['Information Ratio']:.2f}"
    )

    c2.metric(
        "Tracking Error",
        f"{metrics['Tracking Error']:.2%}"
    )

    c3.metric(
        "Benchmark CAGR",
        f"{metrics['Benchmark CAGR']:.2%}"
    )


# EQUITY CURVE

st.divider()

st.subheader("4. Portfolio Growth")

equity = calculate_equity_curve(
    portfolio_returns,
    initial_investment=1.0
)

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=equity.index,
        y=equity,
        mode="lines",
        name="Portfolio",
        line=dict(
            color="#38bdf8",
            width=3
        )
    )
)


if benchmark_returns is not None:

    aligned = pd.concat(
        [
            portfolio_returns.rename("Portfolio"),
            benchmark_returns.rename("Benchmark")
        ],
        axis=1,
        join="inner"
    ).dropna()

    if not aligned.empty:

        benchmark_growth = (
            1 + aligned["Benchmark"]
        ).cumprod()

        fig.add_trace(
            go.Scatter(
                x=benchmark_growth.index,
                y=benchmark_growth,
                mode="lines",
                name="Benchmark",
                line=dict(
                    color="#2dd4bf",
                    width=2
                )
            )
        )


fig.update_layout(
    template="plotly_dark",
    height=480,
    title="Growth of ₹1 Invested",
    yaxis_title="Portfolio Growth"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# DRAWDOWN

st.divider()

st.subheader("5. Drawdown Analysis")

wealth = (1 + portfolio_returns).cumprod()

drawdown = (
    wealth / wealth.cummax()
) - 1

drawdown_fig = px.area(
    drawdown,
    title="Portfolio Drawdown Over Time"
)

drawdown_fig.update_traces(
    line_color="#fb7185",
    fillcolor="rgba(251,113,133,.16)"
)

drawdown_fig.update_layout(
    template="plotly_dark",
    height=380,
    yaxis_tickformat=".0%"
)

st.plotly_chart(
    drawdown_fig,
    use_container_width=True
)


# MONTHLY RETURN HEATMAP

st.divider()

st.subheader("6. Monthly Returns Heatmap")

monthly_returns = (
    (1 + portfolio_returns)
    .resample("ME")
    .prod() - 1
)

if not monthly_returns.empty:

    monthly_df = monthly_returns.to_frame("Return")

    monthly_df["Year"] = monthly_df.index.year

    monthly_df["Month"] = (
        monthly_df.index.strftime("%b")
    )

    pivot = monthly_df.pivot(
        index="Year",
        columns="Month",
        values="Return"
    )

    month_order = [
        "Jan", "Feb", "Mar", "Apr",
        "May", "Jun", "Jul", "Aug",
        "Sep", "Oct", "Nov", "Dec"
    ]

    pivot = pivot.reindex(
        columns=[
            month for month in month_order
            if month in pivot.columns
        ]
    )

    heatmap = px.imshow(
        pivot,
        text_auto=".1%",
        aspect="auto",
        color_continuous_scale="RdYlGn",
        title="Monthly Portfolio Returns"
    )

    heatmap.update_layout(
        template="plotly_dark",
        height=350
    )

    st.plotly_chart(
        heatmap,
        use_container_width=True
    )


# EXPORT

st.divider()

st.download_button(
    "Download Performance Metrics",
    pd.DataFrame([metrics]).to_csv(index=False),
    "portfolio_performance_metrics.csv",
    "text/csv"
)
