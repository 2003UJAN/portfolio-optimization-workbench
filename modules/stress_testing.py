
import numpy as np
import pandas as pd


DEFAULT_SCENARIOS = {
    "Market Crash (-20%)": -0.20,
    "Moderate Correction (-10%)": -0.10,
    "Mild Correction (-5%)": -0.05,
    "Bull Market (+10%)": 0.10,
    "Strong Bull Market (+20%)": 0.20
}


def calculate_stress_scenarios(
    weights,
    scenarios=None,
    initial_investment=100000
):
    """
    Calculate portfolio impact under market-wide stress scenarios.

    Every asset receives the same percentage shock.
    """

    weights = pd.Series(weights, dtype=float)

    if weights.empty:
        raise ValueError("Portfolio weights are empty.")

    if not np.isfinite(weights).all():
        raise ValueError("Portfolio weights contain invalid values.")

    if (weights < 0).any():
        raise ValueError("Negative weights are not supported.")

    if not np.isclose(weights.sum(), 1.0, atol=1e-6):
        raise ValueError("Portfolio weights must sum to 1.")

    if initial_investment <= 0:
        raise ValueError("Initial investment must be positive.")

    if scenarios is None:
        scenarios = DEFAULT_SCENARIOS

    results = []

    for scenario_name, shock in scenarios.items():

        portfolio_return = float(shock)

        profit_loss = initial_investment * portfolio_return

        ending_value = initial_investment + profit_loss

        results.append({
            "Scenario": scenario_name,
            "Portfolio Return (%)": portfolio_return * 100,
            "Profit / Loss": profit_loss,
            "Ending Portfolio Value": ending_value
        })

    return pd.DataFrame(results)


def calculate_custom_asset_shock(
    weights,
    asset_shocks,
    initial_investment=100000
):
    """
    Calculate portfolio impact when individual assets
    experience different percentage shocks.
    """

    weights = pd.Series(weights, dtype=float)
    asset_shocks = pd.Series(asset_shocks, dtype=float)

    if weights.empty:
        raise ValueError("Portfolio weights are empty.")

    if not np.isfinite(weights).all() or not np.isfinite(asset_shocks).all():
        raise ValueError("Weights or shocks contain invalid values.")

    if (weights < 0).any():
        raise ValueError("Negative weights are not supported.")

    if not np.isclose(weights.sum(), 1.0, atol=1e-6):
        raise ValueError("Portfolio weights must sum to 1.")

    if initial_investment <= 0:
        raise ValueError("Initial investment must be positive.")

    missing = weights.index.difference(asset_shocks.index)

    if len(missing) > 0:
        raise ValueError(
            f"Missing shocks for assets: {list(missing)}"
        )

    asset_shocks = asset_shocks.reindex(weights.index)

    portfolio_return = float(
        (weights * asset_shocks).sum()
    )

    profit_loss = initial_investment * portfolio_return

    return {
        "Portfolio Return": portfolio_return,
        "Profit / Loss": profit_loss,
        "Ending Portfolio Value": initial_investment + profit_loss
    }


def calculate_historical_stress(
    returns,
    weights,
    window=21
):
    """
    Calculate historical rolling-period portfolio returns.

    This helps identify the worst historical market periods.
    """

    weights = pd.Series(weights, dtype=float)

    if returns.empty:
        raise ValueError("Returns data is empty.")

    missing = weights.index.difference(returns.columns)

    if len(missing) > 0:
        raise ValueError(f"Missing return data for: {list(missing)}")

    if not np.isclose(weights.sum(), 1.0, atol=1e-6):
        raise ValueError("Portfolio weights must sum to 1.")

    if window <= 0:
        raise ValueError("Window must be positive.")

    aligned_returns = returns.reindex(
        columns=weights.index
    ).dropna()

    portfolio_returns = aligned_returns.dot(weights)

    rolling_returns = (
        (1 + portfolio_returns)
        .rolling(window=window)
        .apply(np.prod, raw=True) - 1
    )

    rolling_returns = rolling_returns.dropna()

    result = rolling_returns.sort_values().reset_index()

    result.columns = ["Date", "Portfolio Return"]

    return result


def calculate_volatility_shock(
    weights,
    covariance_matrix,
    volatility_multiplier=2.0
):
    """
    Estimate portfolio volatility under a covariance shock.

    The multiplier scales portfolio volatility, not returns.
    """

    weights = pd.Series(weights, dtype=float)

    covariance_matrix = pd.DataFrame(covariance_matrix)

    if volatility_multiplier <= 0:
        raise ValueError("Volatility multiplier must be positive.")

    covariance_matrix = covariance_matrix.reindex(
        index=weights.index,
        columns=weights.index
    )

    if covariance_matrix.isna().any().any():
        raise ValueError("Covariance matrix does not match portfolio assets.")

    if not np.isclose(weights.sum(), 1.0, atol=1e-6):
        raise ValueError("Portfolio weights must sum to 1.")

    portfolio_variance = float(
        weights.values
        @ covariance_matrix.values
        @ weights.values
    )

    base_volatility = np.sqrt(max(portfolio_variance, 0))

    stressed_volatility = (
        base_volatility * volatility_multiplier
    )

    return {
        "Base Volatility": float(base_volatility),
        "Stressed Volatility": float(stressed_volatility),
        "Volatility Multiplier": float(volatility_multiplier)
    }
