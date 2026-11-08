
# modules/optimization_engine.py

import numpy as np
import pandas as pd

from scipy.optimize import minimize


# --------------------------------------------------
# DATA PREPARATION
# --------------------------------------------------

def _prepare_inputs(returns):
    """Prepare annualised expected returns and covariance."""

    if returns is None or returns.empty:
        raise ValueError("Return data is empty.")

    clean_returns = (
        returns
        .apply(pd.to_numeric, errors="coerce")
        .dropna(axis=1, how="all")
        .dropna(axis=0, how="any")
    )

    if clean_returns.shape[1] < 2:
        raise ValueError(
            "At least two assets with valid returns are required."
        )

    if len(clean_returns) < 30:
        raise ValueError(
            "At least 30 complete return observations are required."
        )

    tickers = clean_returns.columns

    mean_returns = clean_returns.mean().values * 252

    covariance = clean_returns.cov().values * 252

    # Ensure numerical symmetry
    covariance = (covariance + covariance.T) / 2

    # Small diagonal regularisation for numerical stability
    covariance += np.eye(len(tickers)) * 1e-10

    if not np.isfinite(mean_returns).all():
        raise ValueError("Invalid expected returns.")

    if not np.isfinite(covariance).all():
        raise ValueError("Invalid covariance matrix.")

    return tickers, mean_returns, covariance


def _constraints():
    """Fully invested portfolio constraint."""

    return [
        {
            "type": "eq",
            "fun": lambda weights: np.sum(weights) - 1
        }
    ]


def _bounds(n_assets):
    """Long-only portfolio constraints."""

    return tuple((0.0, 1.0) for _ in range(n_assets))


def _run_optimizer(objective, initial_weights, n_assets):
    """Run the constrained numerical optimizer."""

    result = minimize(
        objective,
        initial_weights,
        method="SLSQP",
        bounds=_bounds(n_assets),
        constraints=_constraints(),
        options={
            "maxiter": 3000,
            "ftol": 1e-12
        }
    )

    if not result.success:
        raise RuntimeError(
            f"Portfolio optimization failed: {result.message}"
        )

    weights = np.clip(result.x, 0, 1)

    if weights.sum() <= 0:
        raise RuntimeError("Optimizer returned invalid weights.")

    return weights / weights.sum()


# --------------------------------------------------
# MINIMUM VARIANCE PORTFOLIO
# --------------------------------------------------

def optimize_minimum_variance(returns):
    """
    Minimize annualised portfolio variance.

    Objective:
        Minimize w'Σw

    Constraints:
        Sum of weights = 1
        0 <= weight <= 1
    """

    tickers, _, covariance = _prepare_inputs(returns)

    n_assets = len(tickers)

    initial_weights = np.ones(n_assets) / n_assets

    def objective(weights):
        return float(
            weights.T @ covariance @ weights
        )

    optimal_weights = _run_optimizer(
        objective,
        initial_weights,
        n_assets
    )

    return pd.Series(
        optimal_weights,
        index=tickers,
        name="Minimum Variance"
    )


# --------------------------------------------------
# MAXIMUM SHARPE RATIO PORTFOLIO
# --------------------------------------------------

def optimize_maximum_sharpe(
    returns,
    risk_free_rate=0.0
):
    """
    Maximize annualised Sharpe ratio.

    Objective:
        Maximize (Expected Return - Risk Free Rate)
        / Portfolio Volatility
    """

    tickers, mean_returns, covariance = _prepare_inputs(
        returns
    )

    n_assets = len(tickers)

    initial_weights = np.ones(n_assets) / n_assets

    def objective(weights):

        expected_return = float(
            weights @ mean_returns
        )

        variance = float(
            weights.T @ covariance @ weights
        )

        volatility = np.sqrt(max(variance, 1e-12))

        sharpe = (
            expected_return - risk_free_rate
        ) / volatility

        return -sharpe

    optimal_weights = _run_optimizer(
        objective,
        initial_weights,
        n_assets
    )

    return pd.Series(
        optimal_weights,
        index=tickers,
        name="Maximum Sharpe"
    )


# --------------------------------------------------
# RISK PARITY PORTFOLIO
# --------------------------------------------------

def optimize_risk_parity(returns):
    """
    Minimize deviations from equal fractional risk contributions.

    This is an approximate long-only risk parity implementation.
    """

    tickers, _, covariance = _prepare_inputs(returns)

    n_assets = len(tickers)

    initial_weights = np.ones(n_assets) / n_assets

    def objective(weights):

        portfolio_variance = float(
            weights.T @ covariance @ weights
        )

        if portfolio_variance <= 1e-12:
            return 1e10

        marginal_risk = covariance @ weights

        risk_contributions = (
            weights * marginal_risk
        ) / portfolio_variance

        target_contribution = 1.0 / n_assets

        return float(
            np.sum(
                (risk_contributions - target_contribution) ** 2
            )
        )

    optimal_weights = _run_optimizer(
        objective,
        initial_weights,
        n_assets
    )

    return pd.Series(
        optimal_weights,
        index=tickers,
        name="Risk Parity"
    )


# --------------------------------------------------
# GENERAL OPTIMIZATION INTERFACE
# --------------------------------------------------

def optimize_portfolio(
    returns,
    method="Maximum Sharpe",
    risk_free_rate=0.0
):
    """
    Main portfolio optimization function.

    Supported methods:
        - Minimum Variance
        - Maximum Sharpe
        - Risk Parity
    """

    if method == "Minimum Variance":

        return optimize_minimum_variance(
            returns
        )

    elif method == "Maximum Sharpe":

        return optimize_maximum_sharpe(
            returns,
            risk_free_rate
        )

    elif method == "Risk Parity":

        return optimize_risk_parity(
            returns
        )

    else:

        raise ValueError(
            "Unsupported optimization method. "
            "Choose Minimum Variance, Maximum Sharpe "
            "or Risk Parity."
        )
