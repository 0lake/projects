import numpy as np
import pandas as pd
import pytest

from churn.config import FEATURES
from churn.data import clean, load_raw, make_xy, split


def test_clean_normalizes_column_names(raw_df):
    cleaned = clean(raw_df)
    assert "Tenure_Months" in cleaned.columns
    assert "Churn_Label" in cleaned.columns


def test_blank_total_charges_become_zero(raw_df):
    cleaned = clean(raw_df)
    assert pd.api.types.is_numeric_dtype(cleaned["Total_Charges"])
    assert cleaned["Total_Charges"].isna().sum() == 0
    zero_tenure = cleaned["Tenure_Months"] == 0
    assert (cleaned.loc[zero_tenure, "Total_Charges"] == 0).all()


def test_make_xy_returns_binary_target_and_expected_features(raw_df):
    X, y = make_xy(clean(raw_df))
    assert list(X.columns) == FEATURES
    assert set(y.unique()) <= {0, 1}
    assert y.sum() == (raw_df["Churn Label"] == "Yes").sum()


def test_make_xy_reports_missing_columns(raw_df):
    broken = clean(raw_df).drop(columns=["Contract"])
    with pytest.raises(KeyError):
        make_xy(broken)


def test_split_is_stratified_and_reproducible(raw_df):
    X, y = make_xy(clean(raw_df))
    X_tr, X_te, y_tr, y_te = split(X, y)
    assert len(X_tr) + len(X_te) == len(X)
    assert abs(y_tr.mean() - y_te.mean()) < 0.02
    _, X_te_again, _, _ = split(X, y)
    assert X_te.index.equals(X_te_again.index)


def test_load_raw_missing_file_has_helpful_message(tmp_path):
    with pytest.raises(FileNotFoundError, match="data/README.md"):
        load_raw(tmp_path / "nope.xlsx")


def test_blank_categories_are_treated_as_missing():
    df = pd.DataFrame({"Contract": ["", "  ", "Two year"]})
    cleaned = clean(df)
    assert cleaned["Contract"].isna().sum() == 2
    assert not np.any(cleaned["Contract"].dropna() == "")
