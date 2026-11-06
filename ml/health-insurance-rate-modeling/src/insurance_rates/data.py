"""Loading, cleaning and feature preparation."""
import numpy as np
import pandas as pd

from .config import TARGET, USECOLS


def load(path, nrows: int | None = None) -> pd.DataFrame:
    """Rate.csv has about 12.7 million rows; read only the columns that are needed."""
    return pd.read_csv(path, usecols=lambda c: c in USECOLS, nrows=nrows, low_memory=False)


def parse_age(age: pd.Series) -> pd.DataFrame:
    """Age is a string: '0-20', '21' ... '63', '64 and over', 'Family Option'.
    Rows must not be dropped just because Age is not a plain number."""
    a = age.astype(str).str.strip()
    num = pd.to_numeric(a, errors="coerce")
    num = num.mask(a.str.startswith("0-"), 20)
    num = num.mask(a.str.contains("64 and over", case=False), 65)
    family = a.str.contains("family", case=False)
    return pd.DataFrame({"age_num": num.where(~family, np.nan), "family_option": family.astype(int)})


def iqr_filter(df: pd.DataFrame, col: str = TARGET, k: float = 1.5) -> pd.DataFrame:
    q1, q3 = df[col].quantile([0.25, 0.75])
    iqr = q3 - q1
    return df[(df[col] >= q1 - k * iqr) & (df[col] <= q3 + k * iqr)]


def clean(df: pd.DataFrame, iqr: bool = True) -> pd.DataFrame:
    """Drop duplicates and rows without a positive rate, remove extreme rates (the raw file has a
    value near 1 000 000), parse Age, fill the categorical gaps."""
    df = df.drop_duplicates()
    df = df[df[TARGET].notna() & (df[TARGET] > 0)]
    if iqr:
        df = iqr_filter(df)
    df = pd.concat([df.reset_index(drop=True), parse_age(df["Age"]).reset_index(drop=True)], axis=1)
    df["age_num"] = df["age_num"].fillna(df["age_num"].median())
    for col in ("StateCode", "IssuerId", "RatingAreaId", "Tobacco"):
        df[col] = df[col].astype("string").fillna("Unknown")
    return df
