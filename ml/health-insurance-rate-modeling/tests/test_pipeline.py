import numpy as np
import pandas as pd
import pytest
from sklearn.ensemble import RandomForestClassifier

from insurance_rates.config import FEATURES, FORBIDDEN
from insurance_rates.data import clean, iqr_filter, load, parse_age
from insurance_rates.evaluate import make_classes, split_by_group
from insurance_rates.run import run


def test_parse_age_keeps_special_tiers():
    out = parse_age(pd.Series(["0-20", "21", "64 and over", "Family Option"]))
    assert out["age_num"].tolist()[:3] == [20, 21, 65]
    assert np.isnan(out["age_num"].iloc[3]) and out["family_option"].tolist() == [0, 0, 0, 1]


def test_clean_removes_extreme_outlier_and_keeps_rows(rates_df):
    cleaned = clean(rates_df)
    assert cleaned["IndividualRate"].max() < 5000
    assert len(cleaned) > 0.9 * len(rates_df)
    assert cleaned["age_num"].notna().all()


def test_features_do_not_contain_target_or_its_copy():
    assert not set(FEATURES) & set(FORBIDDEN)


def test_group_split_keeps_plans_apart(rates_df):
    train, test = split_by_group(clean(rates_df))
    assert set(train["PlanId"]).isdisjoint(set(test["PlanId"]))


def test_class_thresholds_come_from_train_only():
    train = pd.Series(np.arange(100.0))
    test = pd.Series([0.0, 50.0, 99.0, 500.0])
    y_tr, y_te, (q1, q2) = make_classes(train, test)
    assert q1 == pytest.approx(33, abs=1) and q2 == pytest.approx(66, abs=1)
    assert y_te.tolist() == ["Low", "Medium", "High", "High"]


def test_end_to_end_beats_baseline(rates_csv, tmp_path):
    s = run(rates_csv, tmp_path / "r", sample=10_000, fig_dir=tmp_path / "f")
    clf, reg = s["classification"], s["regression"]
    assert clf["Random forest"]["f1_macro"] > clf["Baseline (most frequent)"]["f1_macro"] + 0.2
    assert reg["Random forest"]["r2"] > 0.5 > reg["Baseline (mean)"]["r2"] + 0.4 or reg["Random forest"]["r2"] > 0.5
    assert (tmp_path / "f" / "confusion_matrix_main.png").exists()


def test_leaky_setup_looks_perfect_which_is_the_original_mistake(rates_df):
    """Putting IndividualRate into the features of a rate-category classifier gives ~100% accuracy."""
    df = clean(rates_df)
    train, test = split_by_group(df)
    y_tr, y_te, _ = make_classes(train["IndividualRate"], test["IndividualRate"])
    rf = RandomForestClassifier(50, random_state=0).fit(train[["IndividualRate"]], y_tr)
    assert (rf.predict(test[["IndividualRate"]]) == y_te).mean() > 0.99
