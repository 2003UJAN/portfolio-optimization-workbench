# modules/data_loader.py

import yfinance as yf
import pandas as pd
import numpy as np


def download_stock_data(
    tickers,
    period="5y",
    interval="1d"
):
    """Download adjusted historical stock prices."""

    if not tickers:
        raise ValueError("Please provide at least one ticker.")

    data = yf.download(
        tickers=tickers,
        period=period,
        interval=interval,
        auto_adjust=True,
        progress=False,
        group_by="column",
        threads=True
    )

    if data.empty:
        raise ValueError("No stock data received from Yahoo Finance.")

    if isinstance(data.columns, pd.MultiIndex):
        if "Close" in data.columns.get_level_values(0):
            prices = data["Close"].copy()
            volumes = data["Volume"].copy()
        else:
            raise ValueError("Unable to identify Close price data.")
    else:
        ticker = tickers[0]
        prices = data[["Close"]].rename(columns={"Close": ticker})
        volumes = data[["Volume"]].rename(columns={"Volume": ticker})

    if isinstance(prices, pd.Series):
        prices = prices.to_frame()

    if isinstance(volumes, pd.Series):
        volumes = volumes.to_frame()

    prices.index = pd.to_datetime(prices.index)
    volumes.index = pd.to_datetime(volumes.index)

    prices = prices.sort_index().apply(
        pd.to_numeric, errors="coerce"
    )

    volumes = volumes.sort_index().apply(
        pd.to_numeric, errors="coerce"
    )

    prices = prices.dropna(axis=1, how="all")

    return {
        "prices": prices,
        "volumes": volumes.reindex(columns=prices.columns),
        "returns": prices.pct_change()
    }


def download_benchmark(
    ticker="^NSEI",
    period="5y",
    interval="1d"
):
    """Download benchmark index data, defaulting to NIFTY 50."""

    data = yf.download(
        ticker,
        period=period,
        interval=interval,
        auto_adjust=True,
        progress=False
    )

    if data.empty:
        raise ValueError("Unable to download benchmark data.")

    if isinstance(data.columns, pd.MultiIndex):
        benchmark = data["Close"].iloc[:, 0]
    else:
        benchmark = data["Close"]

    benchmark = pd.to_numeric(
        benchmark, errors="coerce"
    ).dropna()

    benchmark.name = ticker

    return benchmark


def calculate_returns(prices, frequency="Daily"):
    """Calculate returns at the selected frequency."""

    if frequency == "Daily":
        return prices.pct_change().dropna()

    if frequency == "Weekly":
        return prices.resample("W-FRI").last().pct_change().dropna()

    if frequency == "Monthly":
        return prices.resample("ME").last().pct_change().dropna()

    raise ValueError("Frequency must be Daily, Weekly or Monthly.")


def get_data_summary(prices):
    """Return basic information about downloaded data."""

    if prices is None or prices.empty:
        return {
            "stocks": 0,
            "observations": 0,
            "start_date": None,
            "end_date": None
        }

    return {
        "stocks": prices.shape[1],
        "observations": prices.shape[0],
        "start_date": prices.index.min(),
        "end_date": prices.index.max()
    }