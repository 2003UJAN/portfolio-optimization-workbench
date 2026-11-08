
import numpy as np
import pandas as pd
from scipy.stats import norm


def calculate_var(
    returns,
    confidence_level=0.95,
    method="Historical"
):
    """
    Calculate Value at Risk (VaR).

    Returns VaR as a positive loss percentage.
    """

    returns = pd.Series(returns).dropna()

    if returns.empty:
        raise ValueError("Returns data is empty.")

    if not 0 < confidence_level < 1:
        raise ValueError("Confidence level must be between 0 and 1.")

    if method == "Historical":
        var = -returns.quantile(1 - confidence_level)

    elif method == "Parametric":
        mean = returns.mean()
        std = returns.std()

        if std == 0 or np.isnan(std):
            return 0.0

        z_score = norm.ppf(1 - confidence_level)
        var = -(mean + z_score * std)

    else:
        raise ValueError(
            "Method must be 'Historical' or 'Parametric'."
        )

    return float(max(var, 0))


def calculate_cvar(returns, confidence_level=0.95):
    """
    Calculate Conditional Value at Risk (CVaR).
    Also known as Expected Shortfall.
    """

    returns = pd.Series(returns).dropna()

    if returns.empty:
        raise ValueError("Returns data is empty.")

    if not 0 < confidence_level < 1:
        raise ValueError("Confidence level must be between 0 and 1.")

    var = calculate_var(
        returns,
        confidence_level,
        method="Historical"
    )

    tail_returns = returns[returns <= -var]

    if tail_returns.empty:
        return float(var)

    return float(max(-tail_returns.mean(), 0))


def calculate_beta(portfolio_returns, benchmark_returns):
    """
    Calculate portfolio beta relative to a benchmark.
    """

    portfolio_returns = pd.Series(portfolio_returns)
    benchmark_returns = pd.Series(benchmark_returns)

    aligned = pd.concat(
        [portfolio_returns, benchmark_returns],
        axis=1,
        join="inner"
    ).dropna()

    if len(aligned) < 2:
        return np.nan

    portfolio = aligned.iloc[:, 0]
    benchmark = aligned.iloc[:, 1]

    benchmark_variance = benchmark.var()

    if benchmark_variance == 0 or np.isnan(benchmark_variance):
        return np.nan

    beta = portfolio.cov(benchmark) / benchmark_variance

    return float(beta)


def calculate_max_drawdown(returns):
    """
    Calculate maximum drawdown from a return series.
    """

    returns = pd.Series(returns).dropna()

    if returns.empty:
        return 0.0

    wealth_index = (1 + returns).cumprod()
    running_peak = wealth_index.cummax()

    drawdown = (wealth_index / running_peak) - 1

    return float(drawdown.min())


def calculate_rolling_volatility(
    returns,
    window=30,
    periods_per_year=252
):
    """
    Calculate annualized rolling volatility.
    """

    returns = pd.Series(returns)

    rolling_volatility = (
        returns.rolling(window=window).std()
        * np.sqrt(periods_per_year)
    )

    rolling_volatility.name = "Rolling Volatility"

    return rolling_volatility


def calculate_downside_deviation(
    returns,
    target_return=0.0,
    periods_per_year=252
):
    """
    Calculate annualized downside deviation.
    """

    returns = pd.Series(returns).dropna()

    if returns.empty:
        return 0.0

    downside_returns = np.minimum(
        returns - target_return,
        0
    )

    downside_deviation = np.sqrt(
        np.mean(downside_returns ** 2)
    ) * np.sqrt(periods_per_year)

    return float(downside_deviation)


def calculate_risk_metrics(
    portfolio_returns,
    benchmark_returns=None,
    confidence_level=0.95
):
    """
    Calculate the main portfolio risk metrics.
    """

    portfolio_returns = pd.Series(
        portfolio_returns
    ).dropna()

    if portfolio_returns.empty:
        raise ValueError("Portfolio returns are empty.")

    var_95 = calculate_var(
        portfolio_returns,
        confidence_level=confidence_level,
        method="Historical"
    )

    cvar_95 = calculate_cvar(
        portfolio_returns,
        confidence_level=confidence_level
    )

    max_drawdown = calculate_max_drawdown(
        portfolio_returns
    )

    annualized_volatility = (
        portfolio_returns.std() * np.sqrt(252)
    )

    downside_deviation = calculate_downside_deviation(
        portfolio_returns
    )

    metrics = {
        "Value at Risk (VaR)": var_95,
        "Conditional VaR (CVaR)": cvar_95,
        "Maximum Drawdown": max_drawdown,
        "Annualized Volatility": float(annualized_volatility),
        "Downside Deviation": downside_deviation
    }

    if benchmark_returns is not None:
        beta = calculate_beta(
            portfolio_returns,
            benchmark_returns
        )

        metrics["Portfolio Beta"] = beta

    return metrics
