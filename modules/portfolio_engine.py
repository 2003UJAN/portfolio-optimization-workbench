
# modules/portfolio_engine.py

import numpy as np
import pandas as pd


def equal_weights(tickers):
    """Create an equally weighted portfolio."""

    if not tickers:
        raise ValueError("Ticker list cannot be empty.")

    weight = 1.0 / len(tickers)

    return pd.Series(
        weight,
        index=tickers,
        name="Weight"
    )


def validate_weights(weights, tolerance=1e-6):
    """Validate portfolio weights."""

    weights = pd.Series(weights, dtype=float)

    if weights.empty:
        raise ValueError("Portfolio weights are empty.")

    if not np.isfinite(weights).all():
        raise ValueError("Weights must be finite numbers.")

    if (weights < 0).any():
        raise ValueError("Negative weights are not supported.")

    if not np.isclose(weights.sum(), 1, atol=tolerance):
        raise ValueError("Portfolio weights must sum to 1.")

    return weights


def calculate_portfolio_returns(returns, weights):
    """Calculate daily weighted portfolio returns."""

    weights = validate_weights(weights)

    missing = weights.index.difference(returns.columns)

    if len(missing) > 0:
        raise ValueError(
            f"Missing return data for: {list(missing)}"
        )

    aligned_returns = returns.reindex(
        columns=weights.index
    )

    if aligned_returns.isna().any().any():
        raise ValueError(
            "Returns contain missing values. "
            "Clean or align the data before calculation."
        )

    portfolio_returns = aligned_returns.dot(weights)

    portfolio_returns.name = "Portfolio Returns"

    return portfolio_returns


def calculate_portfolio_value(
    portfolio_returns,
    initial_investment=100000
):
    """Calculate historical portfolio value."""

    if initial_investment <= 0:
        raise ValueError("Initial investment must be positive.")

    portfolio_value = (
        (1 + portfolio_returns).cumprod()
        * initial_investment
    )

    portfolio_value.name = "Portfolio Value"

    return portfolio_value


def calculate_covariance_matrix(
    returns,
    annualize=True,
    periods_per_year=252
):
    """Calculate the asset return covariance matrix."""

    covariance = returns.cov()

    if annualize:
        covariance = covariance * periods_per_year

    return covariance


def calculate_portfolio_statistics(
    returns,
    weights,
    risk_free_rate=0.0,
    periods_per_year=252
):
    """Calculate portfolio expected return, volatility and Sharpe ratio."""

    weights = validate_weights(weights)

    aligned_returns = returns.reindex(
        columns=weights.index
    ).dropna()

    if aligned_returns.empty:
        raise ValueError("Insufficient return observations.")

    mean_returns = (
        aligned_returns.mean() * periods_per_year
    )

    covariance = (
        aligned_returns.cov() * periods_per_year
    )

    expected_return = float(
        weights.dot(mean_returns)
    )

    variance = float(
        weights.T.dot(covariance).dot(weights)
    )

    volatility = np.sqrt(max(variance, 0))

    sharpe_ratio = (
        (expected_return - risk_free_rate) / volatility
        if volatility > 0 else np.nan
    )

    return {
        "Expected Annual Return": expected_return,
        "Annualised Volatility": volatility,
        "Sharpe Ratio": sharpe_ratio,
        "Portfolio Variance": variance
    }


def calculate_portfolio_allocation(weights):
    """Convert portfolio weights into an allocation DataFrame."""

    weights = validate_weights(weights)

    allocation = pd.DataFrame({
        "Ticker": weights.index,
        "Weight": weights.values,
        "Allocation (%)": weights.values * 100
    })

    return allocation.sort_values(
        "Weight",
        ascending=False
    ).reset_index(drop=True)
