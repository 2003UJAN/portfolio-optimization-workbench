# Quantitative Portfolio Optimization & Risk Management Workbench

An interactive quantitative finance platform for portfolio construction, mathematical optimization, asset allocation, risk modelling, stochastic simulation, and investment performance analytics.

## Overview

The **Quantitative Portfolio Optimization & Risk Management Workbench** is a Python-based research platform designed to explore Modern Portfolio Theory and quantitative portfolio management techniques.

The application integrates historical market data, statistical analysis, numerical optimization algorithms, and stochastic modelling to construct diversified portfolios and evaluate their risk-return characteristics.

Built using Python and Streamlit, the platform provides interactive dashboards for portfolio optimization, efficient frontier analysis, risk measurement, Monte Carlo simulation, stress testing, and benchmark-relative performance evaluation.

## Key Features

### 1. Portfolio Builder
- Download historical stock price and trading volume data using Yahoo Finance.
- Select multiple financial assets for portfolio construction.
- Implement equal-weighted and custom-weighted asset allocations.
- Visualize portfolio composition and historical asset prices.

### 2. Portfolio Optimization
Implement mathematical optimization techniques:

- **Minimum Variance Portfolio:** Minimize portfolio variance subject to allocation constraints.
- **Maximum Sharpe Ratio Portfolio:** Optimize risk-adjusted returns.
- **Risk Parity Portfolio:** Allocate capital based on asset-level risk contributions.

### 3. Efficient Frontier Analysis
- Generate the Markowitz Efficient Frontier.
- Analyze expected portfolio returns against annualized volatility.
- Identify minimum-volatility and maximum-Sharpe portfolios.
- Calculate the Capital Allocation Line (CAL).
- Visualize optimal risk-return combinations.

### 4. Portfolio Risk Analytics
Evaluate portfolio risk through:

- Historical Value at Risk (VaR).
- Parametric Value at Risk.
- Conditional Value at Risk (CVaR) / Expected Shortfall.
- Portfolio Beta using benchmark returns.
- Maximum Drawdown.
- Rolling Annualized Volatility.
- Downside Deviation.

### 5. Monte Carlo Simulation
- Simulate potential future portfolio-value trajectories using Geometric Brownian Motion.
- Generate multiple stochastic investment scenarios.
- Analyze median, 5th-percentile and 95th-percentile outcomes.
- Estimate the probability of ending below the initial investment.
- Visualize simulated paths and percentile confidence bands.

### 6. Portfolio Stress Testing
- Evaluate hypothetical market crashes and corrections.
- Simulate bullish and bearish market scenarios.
- Apply custom asset-level price shocks.
- Analyze historical rolling-period portfolio performance.
- Assess the impact of increased portfolio volatility.

### 7. Performance Analytics
Evaluate portfolio performance using:

- Compound Annual Growth Rate (CAGR).
- Total Portfolio Return.
- Annualized Volatility.
- Sharpe Ratio.
- Sortino Ratio.
- Information Ratio.
- Tracking Error.
- Maximum Drawdown.
- Monthly Return Analysis.

Compare portfolio performance against the NIFTY 50 benchmark.

## Quantitative Finance Concepts

The platform incorporates the following quantitative finance methodologies:

| Category | Concepts |
|---|---|
| Portfolio Theory | Modern Portfolio Theory, Markowitz Optimization |
| Optimization | Mean-Variance Optimization, Minimum Variance, Maximum Sharpe |
| Asset Allocation | Equal Weighting, Custom Weighting, Risk Parity |
| Risk Management | VaR, CVaR, Beta, Drawdown, Downside Deviation |
| Stochastic Modelling | Geometric Brownian Motion, Monte Carlo Simulation |
| Market Risk | Scenario Analysis, Stress Testing |
| Performance Evaluation | CAGR, Sharpe, Sortino, Information Ratio, Tracking Error |

## Technology Stack

| Component | Technologies |
|---|---|
| Programming Language | Python |
| Data Manipulation | Pandas, NumPy |
| Market Data | Yahoo Finance (yfinance) |
| Numerical Optimization | SciPy, CVXPY |
| Statistical Analysis | SciPy, Statsmodels |
| Machine Learning Utilities | Scikit-learn |
| Visualization | Plotly |
| Web Application | Streamlit |
| Version Control | Git, GitHub |
| Deployment | Streamlit Community Cloud |

## Project Architecture

```text
portfolio-optimization-workbench/
│
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml
│
├── modules/
│   ├── __init__.py
│   ├── data_loader.py
│   ├── portfolio_engine.py
│   ├── optimization_engine.py
│   ├── efficient_frontier.py
│   ├── risk_engine.py
│   ├── monte_carlo.py
│   ├── stress_testing.py
│   └── performance_engine.py
│
├── pages/
│   ├── 1_Portfolio_Builder.py
│   ├── 2_Portfolio_Optimization.py
│   ├── 3_Efficient_Frontier.py
│   ├── 4_Risk_Analytics.py
│   ├── 5_Monte_Carlo.py
│   ├── 6_Stress_Testing.py
│   └── 7_Performance_Analytics.py
│
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/2003UJAN/portfolio-optimization-workbench.git
cd portfolio-optimization-workbench
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python -m streamlit run app.py
```

The application will open locally in your browser.

## Usage Workflow

1. Open the Portfolio Builder.
2. Select stock tickers and download historical market data.
3. Construct a portfolio using equal or custom asset weights.
4. Navigate to Portfolio Optimization to calculate optimal allocations.
5. Explore risk-return combinations using the Efficient Frontier.
6. Evaluate portfolio risk through VaR, CVaR, Beta and drawdown.
7. Run Monte Carlo simulations to study potential portfolio-value distributions.
8. Conduct hypothetical market stress tests.
9. Evaluate historical portfolio performance against the NIFTY 50 benchmark.

## Mathematical Framework

The platform uses several foundational quantitative finance equations.

**Portfolio Expected Return**

$$
E(R_p)=\sum_{i=1}^{N}w_iE(R_i)
$$

**Portfolio Variance**

$$
\sigma_p^2=w^T\Sigma w
$$

**Sharpe Ratio**

$$
S_p=\frac{R_p-R_f}{\sigma_p}
$$

**Value at Risk**

$$
VaR_{\alpha}=-Q_{1-\alpha}(R_p)
$$

**Conditional Value at Risk**

$$
CVaR_{\alpha}=-E[R_p\mid R_p\leq Q_{1-\alpha}(R_p)]
$$

Where:

- $w_i$ represents the weight of asset $i$.
- $Sigma$ represents the asset return covariance matrix.
- $R_p$ represents portfolio return.
- $R_f$ represents the risk-free rate.
- $sigma_p$ represents portfolio volatility.
- $Q$ represents the return quantile.

## Research Assumptions and Limitations

- Portfolio optimization uses historical sample mean returns and covariance estimates.
- The current optimization framework supports long-only portfolios with individual asset weights between 0% and 100%.
- Risk parity uses approximate equalization of asset risk contributions.
- Monte Carlo simulations use a simplified Geometric Brownian Motion framework with constant estimated drift and volatility.
- Stress scenarios are hypothetical and do not represent calibrated predictions of actual market events.
- Benchmark comparisons use downloaded historical index data.
- The current performance dashboard applies a static portfolio allocation to historical returns; it does not yet model dynamic rebalancing or transaction costs.
- Historical data may contain survivorship bias and does not guarantee future performance.

This project is intended for educational, quantitative research and portfolio analytics purposes. It does not constitute investment advice.

## Future Enhancements

- Dynamic portfolio rebalancing and transaction-cost modelling.
- Black-Litterman portfolio optimization.
- Ledoit-Wolf covariance shrinkage.
- Fama-French factor-based portfolio analysis.
- Advanced CVaR optimization.
- GARCH-based volatility forecasting.
- Historical crisis scenario calibration.
- Sector and asset-class allocation constraints.
- Interactive portfolio reporting and AI-assisted investment insights.

## Author

**Ujan Pradhan**

B.Tech in Computer Science | Quantitative Finance & Financial Analytics

**Areas of Interest:** Quantitative Research, Portfolio Optimization, Financial Risk Modelling, Algorithmic Trading and Applied Machine Learning.