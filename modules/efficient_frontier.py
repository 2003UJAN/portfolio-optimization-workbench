
import numpy as np
import pandas as pd
from scipy.optimize import minimize


def _prepare_frontier_inputs(returns, periods_per_year=252):

    if not isinstance(returns, pd.DataFrame):
        raise TypeError("Returns must be a pandas DataFrame.")

    data = returns.copy()

    data = data.apply(pd.to_numeric, errors="coerce")
    data = data.replace([np.inf, -np.inf], np.nan)
    data = data.dropna(axis=1, how="all").dropna(axis=0, how="any")

    if data.shape[1] < 2:
        raise ValueError("At least two valid assets are required.")

    if len(data) < 30:
        raise ValueError("At least 30 observations are required.")

    mean_returns = data.mean().to_numpy() * periods_per_year
    covariance = data.cov().to_numpy() * periods_per_year

    covariance = (covariance + covariance.T) / 2
    covariance += np.eye(len(mean_returns)) * 1e-10

    return data, mean_returns, covariance


def generate_efficient_frontier(
    returns,
    points=50,
    risk_free_rate=0.0,
    periods_per_year=252
):

    data, mean_returns, covariance = _prepare_frontier_inputs(
        returns, periods_per_year
    )

    n_assets = len(mean_returns)

    bounds = tuple((0.0, 1.0) for _ in range(n_assets))

    base_constraint = {
        "type": "eq",
        "fun": lambda w: np.sum(w) - 1.0
    }

    initial_weights = np.repeat(1 / n_assets, n_assets)

    target_returns = np.linspace(
        mean_returns.min(),
        mean_returns.max(),
        int(points)
    )

    results = []

    def portfolio_variance(w):
        return float(w @ covariance @ w)

    for target in target_returns:

        target_constraint = {
            "type": "eq",
            "fun": lambda w, t=target: np.dot(w, mean_returns) - t
        }

        result = minimize(
            portfolio_variance,
            initial_weights.copy(),
            method="SLSQP",
            bounds=bounds,
            constraints=[base_constraint, target_constraint],
            options={"maxiter": 2000, "ftol": 1e-10}
        )

        if not result.success:
            continue

        w = np.clip(result.x, 0, None)

        if w.sum() <= 0:
            continue

        w = w / w.sum()

        expected_return = float(w @ mean_returns)
        volatility = float(np.sqrt(max(w @ covariance @ w, 0)))

        if volatility <= 0:
            continue

        sharpe = (expected_return - risk_free_rate) / volatility

        results.append({
            "Expected Return": expected_return,
            "Volatility": volatility,
            "Sharpe Ratio": sharpe,
            "Weights": {
                ticker: float(weight)
                for ticker, weight in zip(data.columns, w)
            }
        })

    frontier = pd.DataFrame(
        results,
        columns=[
            "Expected Return",
            "Volatility",
            "Sharpe Ratio",
            "Weights"
        ]
    )

    if frontier.empty:
        raise ValueError(
            "No feasible frontier portfolios generated. "
            "Try a different set of stocks."
        )

    return (
        frontier
        .sort_values("Volatility")
        .reset_index(drop=True)
    )


def calculate_capital_allocation_line(
    frontier,
    risk_free_rate=0.0,
    points=50
):

    if frontier is None or frontier.empty:
        raise ValueError("Frontier is empty.")

    required = ["Expected Return", "Volatility", "Sharpe Ratio"]

    if not all(col in frontier.columns for col in required):
        raise ValueError(
            f"Invalid frontier columns: {list(frontier.columns)}"
        )

    valid = frontier.dropna(subset=required)

    if valid.empty:
        raise ValueError("No valid frontier portfolios.")

    best = valid.loc[valid["Sharpe Ratio"].idxmax()]

    best_return = float(best["Expected Return"])
    best_volatility = float(best["Volatility"])

    if best_volatility <= 0:
        raise ValueError("Invalid tangency portfolio volatility.")

    x = np.linspace(0, best_volatility * 1.5, int(points))

    slope = (best_return - risk_free_rate) / best_volatility

    y = risk_free_rate + slope * x

    return pd.DataFrame({
        "Volatility": x,
        "Expected Return": y
    })


def get_frontier_portfolio(
    frontier,
    objective="Maximum Sharpe"
):

    if frontier is None or frontier.empty:
        return None

    required = [
        "Expected Return",
        "Volatility",
        "Sharpe Ratio",
        "Weights"
    ]

    missing = [c for c in required if c not in frontier.columns]

    if missing:
        raise ValueError(
            f"Frontier is missing {missing}. "
            f"Available columns: {list(frontier.columns)}"
        )

    if objective == "Maximum Sharpe":
        row = frontier.loc[frontier["Sharpe Ratio"].idxmax()]

    elif objective == "Minimum Volatility":
        row = frontier.loc[frontier["Volatility"].idxmin()]

    elif objective == "Maximum Return":
        row = frontier.loc[frontier["Expected Return"].idxmax()]

    else:
        raise ValueError("Unknown portfolio objective.")

    return {
        "Expected Return": float(row["Expected Return"]),
        "Volatility": float(row["Volatility"]),
        "Sharpe Ratio": float(row["Sharpe Ratio"]),
        "Weights": dict(row["Weights"])
    }
