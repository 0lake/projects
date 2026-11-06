"""Loading, cleaning and splitting the Telco churn dataset."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from churn.config import (
    CATEGORICAL_FEATURES,
    FEATURES,
    NUMERIC_FEATURES,
    SEED,
    TARGET_COLUMN,
    TEST_SIZE,
)


def load_raw(path: str | Path) -> pd.DataFrame:
    """Read the dataset from .xlsx/.xls or .csv."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Data file not found: {path}. See data/README.md for download instructions."
        )
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    return pd.read_csv(path)


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """'Tenure Months' -> 'Tenure_Months'."""
    out = df.copy()
    out.columns = [str(c).strip().replace(" ", "_") for c in out.columns]
    return out


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize names and coerce types.

    Blank Total_Charges belong to customers with zero tenure who have not been
    billed yet, so they are set to 0. Other missing values are imputed inside
    the model pipeline, which keeps the logic identical at training and
    prediction time.
    """
    out = normalize_columns(df)

    for col in NUMERIC_FEATURES:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    if "Total_Charges" in out.columns:
        out["Total_Charges"] = out["Total_Charges"].fillna(0)

    for col in CATEGORICAL_FEATURES:
        if col in out.columns:
            out[col] = out[col].astype(object).replace(r"^\s*$", np.nan, regex=True)

    return out


def make_xy(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Features and binary target (1 = customer left)."""
    missing = [c for c in FEATURES + [TARGET_COLUMN] if c not in df.columns]
    if missing:
        raise KeyError(f"Missing columns: {missing}")
    X = df[FEATURES].copy()
    y = (df[TARGET_COLUMN] == "Yes").astype(int)
    return X, y


def split(
    X: pd.DataFrame, y: pd.Series
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Stratified train/test split with a fixed seed."""
    return train_test_split(X, y, test_size=TEST_SIZE, stratify=y, random_state=SEED)
