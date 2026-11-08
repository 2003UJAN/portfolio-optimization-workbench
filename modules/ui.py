
import streamlit as st
import textwrap


def apply_theme():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background:
        radial-gradient(ellipse at 12% 0%, rgba(14,116,144,.16), transparent 34%),
        radial-gradient(ellipse at 95% 5%, rgba(37,99,235,.12), transparent 30%),
        #07111f;
    color: #e7eef8;
}

[data-testid="stHeader"] {
    background: rgba(7,17,31,.88);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1a2b, #0a1524);
    border-right: 1px solid rgba(148,163,184,.16);
}

[data-testid="stSidebar"] * {
    color: #d8e5f3;
}

.block-container {
    padding-top: 2.1rem;
    padding-bottom: 3rem;
    max-width: 1450px;
}

h1, h2, h3 {
    font-family: 'Manrope', sans-serif !important;
    color: #e7eef8;
}

[data-testid="stMetric"] {
    background: linear-gradient(145deg, #14263b, #0d1d2f);
    border: 1px solid rgba(148,163,184,.16);
    border-radius: 15px;
    padding: 16px 18px;
}

[data-testid="stMetricLabel"] {
    color: #91a4bb !important;
}

[data-testid="stMetricValue"] {
    color: #f4f8ff !important;
    font-weight: 700;
}

.stButton > button,
.stDownloadButton > button {
    border: 1px solid rgba(56,189,248,.35);
    border-radius: 10px;
    background: linear-gradient(100deg, #0284c7, #0e7490);
    color: white;
    font-weight: 700;
    min-height: 2.65rem;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    border-color: #7dd3fc;
    color: white;
    transform: translateY(-1px);
}

.hero {
    padding: 25px 28px;
    border: 1px solid rgba(56,189,248,.22);
    border-radius: 18px;
    background: linear-gradient(115deg, #082f49, #0f2339 55%, #14263b);
    margin-bottom: 22px;
}

.eyebrow {
    color: #67e8f9;
    font-size: .76rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .13em;
}

.hero h1 {
    margin: 7px 0;
    font-size: 2rem;
    color: #f4f8ff;
}

.hero p {
    color: #a9bfd3;
    margin: 0;
    font-size: .98rem;
}

hr {
    border-color: rgba(148,163,184,.16);
}
</style>
""", unsafe_allow_html=True)


def page_header(title, subtitle):
    html = f"""
<div class="hero">
    <div class="eyebrow">
        QUANTITATIVE FINANCE • RESEARCH • RISK
    </div>
    <h1>{title}</h1>
    <p>{subtitle}</p>
</div>
"""
    st.markdown(
        textwrap.dedent(html).strip(),
        unsafe_allow_html=True
    )


def require_portfolio():
    prices = st.session_state.get("portfolio_prices")
    returns = st.session_state.get("portfolio_returns")
    weights = st.session_state.get("portfolio_weights")

    if prices is None or returns is None or weights is None:
        st.warning(
            "No portfolio data found. Go to Portfolio Builder, "
            "download market data and configure your portfolio."
        )
        st.stop()

    return prices, returns, weights
