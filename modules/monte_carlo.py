
import numpy as np
import pandas as pd


def simulate_portfolio_paths(
    portfolio_returns,
    initial_investment=100000,
    days=252,
    simulations=1000,
    periods_per_year=252,
    seed=42
):
    """
    Simulate future portfolio values using a
    Geometric Brownian Motion (GBM) approach.

    Parameters
    ----------
    portfolio_returns : pd.Series
        Historical daily portfolio returns.
    initial_investment : float
        Starting portfolio value.
    days : int
        Number of future trading days.
    simulations : int
        Number of simulated paths.
    periods_per_year : int
        Number of trading periods per year.
    seed : int
        Random seed for reproducibility.
    """

    returns = pd.Series(portfolio_returns).dropna()

    if returns.empty:
        raise ValueError("Portfolio returns are empty.")

    if initial_investment <= 0:
        raise ValueError("Initial investment must be positive.")

    if days <= 0 or simulations <= 0:
        raise ValueError("Days and simulations must be positive.")

    if periods_per_year <= 0:
        raise ValueError("Periods per year must be positive.")

    mean_return = returns.mean()
    volatility = returns.std()

    if not np.isfinite(mean_return) or not np.isfinite(volatility):
        raise ValueError("Invalid historical return statistics.")

    if volatility == 0:
        paths = np.full(
            (days + 1, simulations),
            initial_investment,
            dtype=float
        )
    else:
        rng = np.random.default_rng(seed)

        daily_drift = mean_return - (0.5 * volatility ** 2)

        random_shocks = rng.normal(
            loc=0,
            scale=1,
            size=(days, simulations)
        )

        daily_returns = np.exp(
            daily_drift + volatility * random_shocks
        )

        paths = np.vstack([
            np.full(simulations, initial_investment),
            initial_investment * np.cumprod(daily_returns, axis=0)
        ])

    paths_df = pd.DataFrame(
        paths,
        columns=[
            f"Simulation {i + 1}"
            for i in range(simulations)
        ]
    )

    paths_df.index.name = "Trading Day"

    final_values = paths_df.iloc[-1]

    summary = {
        "Mean Final Value": float(final_values.mean()),
        "Median Final Value": float(final_values.median()),
        "5th Percentile": float(final_values.quantile(0.05)),
        "95th Percentile": float(final_values.quantile(0.95)),
        "Probability of Loss": float(
            (final_values < initial_investment).mean()
        )
    }

    return paths_df, summary


def calculate_simulation_percentiles(paths):
    """
    Calculate percentile bands across simulated paths.
    """

    if not isinstance(paths, pd.DataFrame) or paths.empty:
        raise ValueError("Simulation paths are empty.")

    percentile_df = pd.DataFrame({
        "5th Percentile": paths.quantile(0.05, axis=1),
        "25th Percentile": paths.quantile(0.25, axis=1),
        "Median": paths.quantile(0.50, axis=1),
        "75th Percentile": paths.quantile(0.75, axis=1),
        "95th Percentile": paths.quantile(0.95, axis=1)
    })

    return percentile_df
