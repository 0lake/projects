"""Loading, scaling and imputation flags."""
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

from .config import FEATURES, LOG_FEATURES


def load(path) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = [c for c in FEATURES if c not in df.columns]
    if missing:
        raise ValueError(f"missing columns: {missing}")
    return df


def flag_median_filled(df: pd.DataFrame) -> pd.Series:
    """The R cleaning step fills missing MetaScore and Gross with the median. Values equal to
    the median in those columns are therefore mostly imputed, not observed."""
    return (df["Gross"] == df["Gross"].median()) | (df["MetaScore"] == df["MetaScore"].median())


def scale(df: pd.DataFrame, log: bool = False) -> np.ndarray:
    X = df[FEATURES].astype(float).copy()
    if log:
        for col in LOG_FEATURES:
            X[col] = np.log1p(X[col].clip(lower=0))
    return StandardScaler().fit_transform(X)
