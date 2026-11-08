
import streamlit as st

from modules.ui import apply_theme


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Quantitative Portfolio Workbench",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_theme()


# ==================================================
# HERO BANNER
# ==================================================

hero_html = """
<div class="hero">
<div class="eyebrow">QUANTITATIVE FINANCE • RESEARCH • RISK</div>
<h1>Portfolio Optimization &amp; Risk Management Workbench</h1>
<p>A quantitative research environment for portfolio construction,
mean-variance optimization, efficient-frontier analysis,
simulation, stress testing and benchmark-relative performance.</p>
</div>
"""

st.markdown(hero_html, unsafe_allow_html=True)


# ==================================================
# RESEARCH WORKSPACE
# ==================================================

st.markdown("## Research Workspace")

st.caption(
    "Explore the quantitative modules using the navigation panel."
)

st.divider()


# ==================================================
# DASHBOARD MODULES
# ==================================================

cards = [
    (
        "01",
        "Portfolio Builder",
        "📊",
        "Load market data, select assets and define portfolio weights."
    ),
    (
        "02",
        "Portfolio Optimization",
        "⚖️",
        "Compare minimum variance, maximum Sharpe and risk parity."
    ),
    (
        "03",
        "Efficient Frontier",
        "📈",
        "Explore the risk-return trade-off and capital allocation line."
    ),
    (
        "04",
        "Risk Analytics",
        "🛡️",
        "Measure VaR, CVaR, drawdown, beta and volatility."
    ),
    (
        "05",
        "Monte Carlo",
        "🎲",
        "Simulate potential future portfolio value paths."
    ),
    (
        "06",
        "Stress Testing",
        "⚡",
        "Evaluate hypothetical market shocks and historical losses."
    ),
    (
        "07",
        "Performance Analytics",
        "🏁",
        "Analyze portfolio growth and benchmark-relative performance."
    )
]


for i in range(0, len(cards), 2):

    col1, col2 = st.columns(2)

    number, title, emoji, description = cards[i]

    with col1:

        with st.container(border=True):

            st.caption(f"MODULE {number}")

            st.markdown(f"### {emoji} {title}")

            st.write(description)

    if i + 1 < len(cards):

        number, title, emoji, description = cards[i + 1]

        with col2:

            with st.container(border=True):

                st.caption(f"MODULE {number}")

                st.markdown(f"### {emoji} {title}")

                st.write(description)


# ==================================================
# QUANTITATIVE FRAMEWORK
# ==================================================

st.divider()

st.markdown("## Quantitative Framework")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Asset Universe", "Multi-Asset")
c2.metric("Optimization", "Mean-Variance")
c3.metric("Risk Framework", "VaR / CVaR")
c4.metric("Simulation", "Monte Carlo")


# ==================================================
# GETTING STARTED
# ==================================================

st.divider()

st.markdown("## Getting Started")

st.info(
    """
    **Step 1:** Open Portfolio Builder.

    **Step 2:** Download historical stock market data.

    **Step 3:** Select at least two stocks.

    **Step 4:** Configure equal or custom portfolio weights.

    **Step 5:** Explore optimization, risk and performance analytics.
    """
)


# ==================================================
# FOOTER
# ==================================================

st.divider()

st.caption(
    "QUANTITATIVE PORTFOLIO OPTIMIZATION & RISK MANAGEMENT WORKBENCH"
)

st.caption(
    "Built using Python | Streamlit | NumPy | Pandas | SciPy | Plotly"
)

st.caption(
    "For educational and quantitative research purposes only. "
    "Not investment advice."
)
