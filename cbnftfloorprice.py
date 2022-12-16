import typing as ta
import numpy as np
import pandas as pd
import numpy.typing as npt
from scipy import stats


def create_lookback(data: pd.DataFrame, lookback: int) -> pd.DataFrame:
    """
    For each row, create an array of past log prices for the given lookback period, exclusive of the
    log price for the row. The function assumes that the data belong to the same group (e.g. same
    NFT collection).

    Args:
        data: A pandas DataFrame containing the relevant data, in particular, block_number column is required for ordering and log_price column is required for the price data
        lookback: The lookback period

    Returns:
        The original pandas DataFrame with two additional columns: trade_id and log_prices_lookback.
    """
    data.block_number = data.block_number.astype("int64")
    result = data[
        [
            "chain_id",
            "contract_address",
            "ds",
            "block_number",
            "unix_timestamp",
            "log_price",
        ]
    ].sort_values("block_number")
    lookback_prices = []
    trade_ids = []

    for idx in range(result.shape[0]):
        if idx == 0:
            lookback_prices.append([-42.0])
        else:
            idx_start = max(0, idx - lookback)
            prices = list(result.iloc[idx_start:idx]["log_price"])

            lookback_prices.append(prices)

        trade_ids.append(idx)

    result["log_prices_lookback"] = lookback_prices
    result["trade_id"] = trade_ids

    return result


def compute_new_quantile(
    q_curr: float,
    q_target: float,
    q_obs: float,
    speed: float,
    pct_target_min: float,
    pct_target_max: float,
) -> float:
    """
    Compute an adjusted quantile based on a reference target quantile and the observed quantile.

    Args:
        q_curr: The current effective quantile
        q_target: The target quantile
        q_obs: The observed quantile
        speed: The speed of adjustment
        pct_target_min: The lower bound for the adjusted quantile
        pct_target_max: The upper bound for the adjusted quantile

    Returns:
        The adjusted quantile
    """
    return min(pct_target_max, max(pct_target_min, q_curr + speed * (q_target - q_obs)))


def compute_quantile(array: npt.ArrayLike, quantile: float) -> float:
    """
    Compute the value at a given quantile from an array of numbers.

    Args:
        array: The array of numbers
        quantile: The quantile of interest

    Returns:
        The value corresponding to the given quantile in the array.
    """
    return float(pd.Series(np.array(array)).dropna().quantile(quantile))


def compute_quantile_obs(data: pd.DataFrame, backtest: int) -> pd.DataFrame:
    """
    Compute an observed quantile based on how each row's log price relates to the lookback log
    prices over a backtest window. The function assumes that the data belong to the same group (e.g.
    same NFT collection).

    Args:
        data: A pandas DataFrame containing the relevant data, in particular an ordering column trade_id and a boolean column price_smaller are required
        backtest: The backtest window

    Returns:
        The original pandas DataFrame with an additional column: quantile_obs
    """
    result = data[
        [
            "chain_id",
            "contract_address",
            "ds",
            "block_number",
            "unix_timestamp",
            "log_price",
            "trade_id",
            "log_prices_lookback",
            "price_smaller",
        ]
    ].sort_values("trade_id")

    result["quantile_obs"] = result["price_smaller"].rolling(backtest).mean()

    return result


def remove_outliers(array: npt.NDArray[np.float64]) -> ta.List[float]:
    """
    Remove outliers from an array of floating-point numbers.
    Outliers are determined to be at least 3 median absolute deviation away from the median.

    Args:
        array: The array of floating-point numbers whose outliers we want to remove

    Returns:
        A list of floating-point numbers from array with the exception of the outliers
    """
    array_median = np.median(array)
    array_mad = stats.median_abs_deviation(array)
    lb = array_median - 3 * array_mad
    ub = array_median + 3 * array_mad

    result = [float(elem) for elem in array if elem >= lb and elem <= ub]

    return result
