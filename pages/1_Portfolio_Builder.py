
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from modules.data_loader import (
    download_stock_data,
    download_benchmark
)

from modules.portfolio_engine import (
    equal_weights,
    validate_weights,
    calculate_portfolio_allocation
)


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Portfolio Builder",
    page_icon="📊",
    layout="wide"
)


# --------------------------------------------------
# PAGE STYLING
# --------------------------------------------------

st.markdown("""
<style>
    .main-title {
        font-size: 32px;
        font-weight: 700;
        color: #38BDF8;
    }

    .subtitle {
        color: #94A3B8;
        font-size: 15px;
    }

    div[data-testid="stMetric"] {
        background-color: #17253A;
        padding: 15px;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------

st.markdown(
    '<p class="main-title">Portfolio Builder</p>',
    unsafe_allow_html=True
)

st.markdown(
    '<p class="subtitle">Build and configure a multi-asset '
    'equity portfolio using historical market data.</p>',
    unsafe_allow_html=True
)

st.divider()


# --------------------------------------------------
# DEFAULT SETTINGS
# --------------------------------------------------

DEFAULT_TICKERS = [
    "RELIANCE.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "INFY.NS",
    "TCS.NS",
    "SBIN.NS",
    "LT.NS",
    "BHARTIARTL.NS",
    "ITC.NS",
    "AXISBANK.NS"
]

if "portfolio_prices" not in st.session_state:
    st.session_state.portfolio_prices = None

if "portfolio_returns" not in st.session_state:
    st.session_state.portfolio_returns = None

if "portfolio_volumes" not in st.session_state:
    st.session_state.portfolio_volumes = None

if "portfolio_benchmark" not in st.session_state:
    st.session_state.portfolio_benchmark = None

if "portfolio_weights" not in st.session_state:
    st.session_state.portfolio_weights = None

if "portfolio_tickers" not in st.session_state:
    st.session_state.portfolio_tickers = []

if "selected_assets" not in st.session_state:
    st.session_state.selected_assets = []

if "portfolio_optimization_method" not in st.session_state:
    st.session_state.portfolio_optimization_method = "Equal Weight"


# --------------------------------------------------
# SECTION 1: MARKET DATA CONFIGURATION
# --------------------------------------------------

st.subheader("1. Market Data Configuration")

col1, col2 = st.columns(2)

with col1:

    ticker_input = st.text_area(
        "Enter stock ticker symbols",
        value=", ".join(DEFAULT_TICKERS),
        height=110,
        help="Use Yahoo Finance ticker symbols. "
             "For Indian stocks, use .NS for NSE."
    )

with col2:

    period = st.selectbox(
        "Historical data period",
        ["1y", "2y", "3y", "5y", "10y"],
        index=3
    )

    benchmark_ticker = st.selectbox(
        "Benchmark index",
        ["^NSEI", "^BSESN"],
        index=0,
        format_func=lambda x: {
            "^NSEI": "NIFTY 50",
            "^BSESN": "BSE SENSEX"
        }.get(x, x)
    )

    st.caption(
        "Data source: Yahoo Finance | "
        "Frequency: Daily"
    )


download_button = st.button(
    "Download Market Data",
    type="primary",
    use_container_width=True
)


# --------------------------------------------------
# SECTION 2: DOWNLOAD MARKET DATA
# --------------------------------------------------

if download_button:

    tickers = list(dict.fromkeys([
        ticker.strip().upper()
        for ticker in ticker_input.split(",")
        if ticker.strip()
    ]))

    if len(tickers) < 2:

        st.error("Please enter at least two valid stock tickers.")

    else:

        with st.spinner("Downloading historical market data..."):

            try:

                stock_data = download_stock_data(
                    tickers=tickers,
                    period=period
                )

                if not isinstance(stock_data, dict):
                    raise ValueError(
                        "Unexpected data format returned by data loader."
                    )

                prices = stock_data.get("prices")
                volumes = stock_data.get("volumes")
                returns = stock_data.get("returns")

                if prices is None or returns is None:
                    raise ValueError(
                        "Stock price or return data is unavailable."
                    )

                if prices.empty or returns.empty:
                    raise ValueError(
                        "No historical market data was downloaded."
                    )

                available_tickers = list(prices.columns)

                if len(available_tickers) < 2:
                    raise ValueError(
                        "At least two stocks must have valid price data."
                    )

                benchmark = download_benchmark(
                    ticker=benchmark_ticker,
                    period=period
                )

                st.session_state.portfolio_prices = prices
                st.session_state.portfolio_returns = returns
                st.session_state.portfolio_volumes = volumes
                st.session_state.portfolio_benchmark = benchmark

                st.session_state.portfolio_benchmark_ticker = (
                    benchmark_ticker
                )

                st.session_state.portfolio_tickers = available_tickers
                st.session_state.selected_assets = available_tickers

                st.session_state.portfolio_period = period

                st.session_state.portfolio_weights = (
                    equal_weights(available_tickers)
                )

                st.session_state.portfolio_optimization_method = (
                    "Equal Weight"
                )

                st.success(
                    f"Successfully downloaded data for "
                    f"{len(available_tickers)} stocks."
                )

            except Exception as e:

                st.error(f"Market data download failed: {e}")


# --------------------------------------------------
# SECTION 3: CHECK DATA AVAILABILITY
# --------------------------------------------------

prices = st.session_state.portfolio_prices
returns = st.session_state.portfolio_returns
volumes = st.session_state.portfolio_volumes

if prices is None or returns is None:

    st.info(
        "Download market data to start building your portfolio."
    )

    st.markdown("### Default Stock Universe")

    st.write(
        "The application supports Indian equities listed on NSE "
        "using Yahoo Finance ticker symbols."
    )

    st.dataframe(
        pd.DataFrame({
            "Ticker": DEFAULT_TICKERS,
            "Exchange": ["NSE"] * len(DEFAULT_TICKERS)
        }),
        use_container_width=True,
        hide_index=True
    )

    st.stop()


# --------------------------------------------------
# SECTION 4: MARKET DATA OVERVIEW
# --------------------------------------------------

st.divider()

st.subheader("2. Market Data Overview")

metric1, metric2, metric3, metric4 = st.columns(4)

with metric1:
    st.metric(
        "Available Stocks",
        len(prices.columns)
    )

with metric2:
    st.metric(
        "Historical Observations",
        len(prices)
    )

with metric3:
    st.metric(
        "Data Period",
        st.session_state.get("portfolio_period", "N/A")
    )

with metric4:
    st.metric(
        "Benchmark",
        st.session_state.get(
            "portfolio_benchmark_ticker",
            "^NSEI"
        )
    )


# --------------------------------------------------
# SECTION 5: PRICE HISTORY
# --------------------------------------------------

st.subheader("Historical Stock Prices")

price_chart = px.line(
    prices,
    x=prices.index,
    y=prices.columns,
    title="Historical Stock Price Movement",
    labels={
        "x": "Date",
        "value": "Adjusted Price",
        "variable": "Stock"
    }
)

price_chart.update_layout(
    template="plotly_dark",
    height=450,
    hovermode="x unified"
)

st.plotly_chart(
    price_chart,
    use_container_width=True
)


# --------------------------------------------------
# SECTION 6: ASSET SELECTION
# --------------------------------------------------

st.divider()

st.subheader("3. Portfolio Asset Selection")

available_tickers = list(prices.columns)

default_selected = [
    ticker
    for ticker in st.session_state.selected_assets
    if ticker in available_tickers
]

if not default_selected:
    default_selected = available_tickers

selected_assets = st.multiselect(
    "Select stocks for your portfolio",
    options=available_tickers,
    default=default_selected
)

if not selected_assets:

    st.warning("Select at least two stocks to build a portfolio.")
    st.stop()

if len(selected_assets) < 2:

    st.warning(
        "Select at least two stocks for meaningful portfolio analysis."
    )
    st.stop()


# --------------------------------------------------
# SECTION 7: PORTFOLIO WEIGHT ALLOCATION
# --------------------------------------------------

st.divider()

st.subheader("4. Portfolio Weight Allocation")

allocation_method = st.radio(
    "Choose allocation methodology",
    ["Equal Weight", "Custom Weight"],
    horizontal=True
)

if allocation_method == "Equal Weight":

    weights = equal_weights(selected_assets)

    st.info(
        f"Each of the {len(selected_assets)} selected stocks "
        f"will receive an equal allocation of "
        f"{100 / len(selected_assets):.2f}%."
    )

else:

    st.write(
        "Enter the percentage allocation for each selected stock."
    )

    previous_weights = st.session_state.portfolio_weights

    default_values = {}

    for ticker in selected_assets:

        if (
            previous_weights is not None
            and ticker in previous_weights.index
        ):
            default_values[ticker] = float(
                previous_weights[ticker] * 100
            )

        else:
            default_values[ticker] = 100 / len(selected_assets)

    allocation_df = pd.DataFrame({
        "Ticker": selected_assets,
        "Weight (%)": [
            default_values[ticker]
            for ticker in selected_assets
        ]
    })

    edited_allocation = st.data_editor(
        allocation_df,
        use_container_width=True,
        hide_index=True,
        disabled=["Ticker"],
        column_config={
            "Weight (%)": st.column_config.NumberColumn(
                "Weight (%)",
                min_value=0.0,
                max_value=100.0,
                step=1.0,
                format="%.2f%%"
            )
        },
        key="custom_allocation_editor"
    )

    weights = pd.Series(
        edited_allocation["Weight (%)"].values / 100,
        index=edited_allocation["Ticker"].values,
        dtype=float
    )

    total_weight = weights.sum()

    st.metric(
        "Total Allocation",
        f"{total_weight * 100:.2f}%"
    )

    if not np.isclose(total_weight, 1.0, atol=1e-6):

        st.warning(
            "Your portfolio allocation must total exactly 100%. "
            "Adjust the weights before saving."
        )

        st.stop()


# --------------------------------------------------
# SECTION 8: VALIDATE AND SAVE PORTFOLIO
# --------------------------------------------------

try:

    weights = validate_weights(weights)

except Exception as e:

    st.error(f"Invalid portfolio allocation: {e}")
    st.stop()


allocation = calculate_portfolio_allocation(weights)

allocation["Allocation (%)"] = (
    allocation["Weight"] * 100
)

st.session_state.portfolio_weights = weights
st.session_state.selected_assets = selected_assets

st.session_state.portfolio_optimization_method = allocation_method


# --------------------------------------------------
# SECTION 9: PORTFOLIO ALLOCATION VISUALIZATION
# --------------------------------------------------

st.divider()

st.subheader("5. Portfolio Allocation")

col1, col2 = st.columns([1.2, 1])

with col1:

    allocation_chart = px.pie(
        allocation,
        names="Ticker",
        values="Weight",
        hole=0.55,
        title="Portfolio Asset Distribution"
    )

    allocation_chart.update_layout(
        template="plotly_dark",
        height=400
    )

    st.plotly_chart(
        allocation_chart,
        use_container_width=True
    )


with col2:

    st.markdown("#### Allocation Details")

    display_allocation = allocation[
        ["Ticker", "Weight", "Allocation (%)"]
    ].copy()

    display_allocation["Weight"] = (
        display_allocation["Weight"].map(
            lambda x: f"{x:.4f}"
        )
    )

    display_allocation["Allocation (%)"] = (
        display_allocation["Allocation (%)"].map(
            lambda x: f"{x:.2f}%"
        )
    )

    st.dataframe(
        display_allocation,
        use_container_width=True,
        hide_index=True
    )

    st.metric(
        "Number of Portfolio Holdings",
        len(selected_assets)
    )


# --------------------------------------------------
# SECTION 10: PORTFOLIO RETURN ANALYSIS
# --------------------------------------------------

st.divider()

st.subheader("6. Portfolio Return Overview")

selected_returns = returns[selected_assets].dropna()

portfolio_returns = selected_returns.dot(weights)

portfolio_returns.name = "Portfolio Returns"

if portfolio_returns.empty:

    st.warning("Unable to calculate portfolio returns.")

else:

    annual_return = (
        (1 + portfolio_returns.mean()) ** 252 - 1
    ) * 100

    annual_volatility = (
        portfolio_returns.std() * np.sqrt(252) * 100
    )

    total_return = (
        (1 + portfolio_returns).prod() - 1
    ) * 100

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Annualized Arithmetic Return",
            f"{annual_return:.2f}%"
        )

    with c2:
        st.metric(
            "Annualized Volatility",
            f"{annual_volatility:.2f}%"
        )

    with c3:
        st.metric(
            "Historical Cumulative Return",
            f"{total_return:.2f}%"
        )


# --------------------------------------------------
# SECTION 11: PORTFOLIO DATA DOWNLOAD
# --------------------------------------------------

st.divider()

st.subheader("7. Export Portfolio Data")

col1, col2 = st.columns(2)

with col1:

    csv_allocation = allocation.to_csv(index=False)

    st.download_button(
        "Download Portfolio Allocation",
        data=csv_allocation,
        file_name="portfolio_allocation.csv",
        mime="text/csv",
        use_container_width=True
    )

with col2:

    csv_returns = portfolio_returns.to_frame().to_csv()

    st.download_button(
        "Download Portfolio Returns",
        data=csv_returns,
        file_name="portfolio_returns.csv",
        mime="text/csv",
        use_container_width=True
    )


# --------------------------------------------------
# FINAL STATUS
# --------------------------------------------------

st.divider()

st.success(
    "Portfolio configuration saved successfully. "
    "You can now proceed to Portfolio Optimization, "
    "Efficient Frontier and Risk Analytics."
)
