
import numpy as np
import pandas as pd


def calculate_cagr(returns, periods_per_year=252):
    """Calculate annualized Compound Annual Growth Rate."""

    returns = pd.Series(returns).dropna()

    if returns.empty:
        return 0.0

    wealth = (1 + returns).prod()

    if wealth <= 0:
        return -1.0

    years = len(returns) / periods_per_year

    if years <= 0:
        return 0.0

    return float(wealth ** (1 / years) - 1)


def calculate_volatility(returns, periods_per_year=252):
    """Calculate annualized portfolio volatility."""

    returns = pd.Series(returns).dropna()

    if len(returns) < 2:
        return 0.0

    return float(returns.std() * np.sqrt(periods_per_year))


def calculate_sharpe_ratio(
    returns,
    risk_free_rate=0.0,
    periods_per_year=252
):
    """Calculate annualized Sharpe Ratio."""

    returns = pd.Series(returns).dropna()

    if len(returns) < 2:
        return 0.0

    periodic_rf = risk_free_rate / periods_per_year
    excess_returns = returns - periodic_rf

    volatility = returns.std()

    if volatility == 0 or np.isnan(volatility):
        return 0.0

    sharpe = (
        excess_returns.mean()
        / volatility
        * np.sqrt(periods_per_year)
    )

    return float(sharpe)


def calculate_sortino_ratio(
    returns,
    risk_free_rate=0.0,
    periods_per_year=252
):
    """Calculate annualized Sortino Ratio."""

    returns = pd.Series(returns).dropna()

    if len(returns) < 2:
        return 0.0

    periodic_rf = risk_free_rate / periods_per_year

    excess_returns = returns - periodic_rf

    downside_returns = np.minimum(
        excess_returns,
        0
    )

    downside_deviation = np.sqrt(
        np.mean(downside_returns ** 2)
    )

    if downside_deviation == 0:
        return 0.0

    sortino = (
        excess_returns.mean()
        / downside_deviation
        * np.sqrt(periods_per_year)
    )

    return float(sortino)


def calculate_tracking_error(
    portfolio_returns,
    benchmark_returns,
    periods_per_year=252
):
    """Calculate annualized tracking error."""

    aligned = pd.concat(
        [
            pd.Series(portfolio_returns, name="Portfolio"),
            pd.Series(benchmark_returns, name="Benchmark")
        ],
        axis=1,
        join="inner"
    ).dropna()

    if len(aligned) < 2:
        return 0.0

    active_returns = (
        aligned["Portfolio"] - aligned["Benchmark"]
    )

    return float(
        active_returns.std() * np.sqrt(periods_per_year)
    )


def calculate_information_ratio(
    portfolio_returns,
    benchmark_returns,
    periods_per_year=252
):
    """Calculate annualized Information Ratio."""

    aligned = pd.concat(
        [
            pd.Series(portfolio_returns, name="Portfolio"),
            pd.Series(benchmark_returns, name="Benchmark")
        ],
        axis=1,
        join="inner"
    ).dropna()

    if len(aligned) < 2:
        return 0.0

    active_returns = (
        aligned["Portfolio"] - aligned["Benchmark"]
    )

    tracking_error = (
        active_returns.std() * np.sqrt(periods_per_year)
    )

    if tracking_error == 0 or np.isnan(tracking_error):
        return 0.0

    annualized_active_return = (
        active_returns.mean() * periods_per_year
    )

    return float(
        annualized_active_return / tracking_error
    )


def calculate_max_drawdown(returns):
    """Calculate maximum peak-to-trough portfolio decline."""

    returns = pd.Series(returns).dropna()

    if returns.empty:
        return 0.0

    wealth_index = (1 + returns).cumprod()

    running_peak = wealth_index.cummax()

    drawdown = (
        wealth_index / running_peak
    ) - 1

    return float(drawdown.min())


def calculate_performance_metrics(
    portfolio_returns,
    benchmark_returns=None,
    risk_free_rate=0.0,
    periods_per_year=252
):
    """Calculate the main portfolio performance metrics."""

    portfolio_returns = pd.Series(
        portfolio_returns
    ).dropna()

    if portfolio_returns.empty:
        raise ValueError("Portfolio returns are empty.")

    metrics = {
        "CAGR": calculate_cagr(
            portfolio_returns,
            periods_per_year
        ),
        "Annualized Volatility": calculate_volatility(
            portfolio_returns,
            periods_per_year
        ),
        "Sharpe Ratio": calculate_sharpe_ratio(
            portfolio_returns,
            risk_free_rate,
            periods_per_year
        ),
        "Sortino Ratio": calculate_sortino_ratio(
            portfolio_returns,
            risk_free_rate,
            periods_per_year
        ),
        "Maximum Drawdown": calculate_max_drawdown(
            portfolio_returns
        )
    }

    if benchmark_returns is not None:

        aligned = pd.concat(
            [
                portfolio_returns.rename("Portfolio"),
                pd.Series(benchmark_returns).rename("Benchmark")
            ],
            axis=1,
            join="inner"
        ).dropna()

        if not aligned.empty:
            metrics["Information Ratio"] = (
                calculate_information_ratio(
                    aligned["Portfolio"],
                    aligned["Benchmark"],
                    periods_per_year
                )
            )

            metrics["Tracking Error"] = (
                calculate_tracking_error(
                    aligned["Portfolio"],
                    aligned["Benchmark"],
                    periods_per_year
                )
            )

            metrics["Benchmark CAGR"] = calculate_cagr(
                aligned["Benchmark"],
                periods_per_year
            )

    return metrics


def calculate_equity_curve(
    returns,
    initial_investment=100000
):
    """Calculate portfolio equity curve."""

    returns = pd.Series(returns).dropna()

    if returns.empty:
        return pd.Series(dtype=float)

    equity_curve = initial_investment * (
        1 + returns
    ).cumprod()

    equity_curve.name = "Portfolio Value"

    return equity_curve


def compare_portfolio_with_benchmark(
    portfolio_returns,
    benchmark_returns,
    initial_investment=100000
):
    """Compare cumulative portfolio and benchmark values."""

    aligned = pd.concat(
        [
            pd.Series(portfolio_returns, name="Portfolio"),
            pd.Series(benchmark_returns, name="Benchmark")
        ],
        axis=1,
        join="inner"
    ).dropna()

    if aligned.empty:
        raise ValueError(
            "Portfolio and benchmark have no overlapping return dates."
        )

    comparison = pd.DataFrame(index=aligned.index)

    comparison["Portfolio Value"] = (
        initial_investment
        * (1 + aligned["Portfolio"]).cumprod()
    )

    comparison["Benchmark Value"] = (
        initial_investment
        * (1 + aligned["Benchmark"]).cumprod()
    )

    return comparison
