"""Loading and preparing the US monthly indicators."""
from pathlib import Path

import pandas as pd
from sklearn.preprocessing import StandardScaler

from .config import KAGGLE_DATASET, Config


def download_csv() -> Path:
    """Download the Kaggle dataset and return the path to its CSV file."""
    import kagglehub  # optional dependency

    folder = Path(kagglehub.dataset_download(KAGGLE_DATASET))
    return sorted(folder.glob("*.csv"))[0]


def load_us_monthly(csv_path: Path) -> pd.DataFrame:
    """Rows for the United States with monthly frequency, sorted by date."""
    df = pd.read_csv(csv_path)
    usa = df[(df["place_name"] == "United States") & (df["frequency"] == "monthly")].copy()
    usa["Date"] = pd.to_datetime(usa["Date"], format="%d-%m-%Y")
    return usa.sort_values("Date")


def prepare(usa: pd.DataFrame, cfg: Config):
    """Build a regular monthly index, interpolate gaps, scale exogenous variables.

    Returns y (target) and X (standardised exogenous) with a monthly PeriodIndex.
    The scaler is fitted on the training part only, so no test statistics leak.
    """
    frame = usa.set_index("Date")[[cfg.target] + cfg.exog].interpolate(method="linear")
    full_index = pd.date_range(frame.index.min(), frame.index.max(), freq="MS")
    frame = frame.reindex(full_index).interpolate(method="linear")

    y = frame[cfg.target].to_period("M")
    X = frame[cfg.exog].to_period("M")
    return y, X


def split_and_scale(y: pd.Series, X: pd.DataFrame, test_size: float):
    """Chronological split; scaler fitted on train only."""
    n_test = int(round(len(y) * test_size))
    y_train, y_test = y.iloc[:-n_test], y.iloc[-n_test:]
    X_train, X_test = X.iloc[:-n_test], X.iloc[-n_test:]
    scaler = StandardScaler().fit(X_train)
    X_train = pd.DataFrame(scaler.transform(X_train), index=X_train.index, columns=X.columns)
    X_test = pd.DataFrame(scaler.transform(X_test), index=X_test.index, columns=X.columns)
    return y_train, y_test, X_train, X_test
