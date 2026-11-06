import json

import joblib
import numpy as np
import pandas as pd
import pytest

from churn.data import clean, load_raw, make_xy, split
from churn.evaluate import capture_rate, classification_metrics, pick_threshold
from churn.models import get_models
from churn.predict import score
from churn.train import run


@pytest.fixture(scope="module")
def trained(tmp_path_factory, data_file):
    out = tmp_path_factory.mktemp("out")
    metrics = run(
        data_path=data_file,
        out_dir=out / "reports",
        model_path=out / "model.joblib",
        tune=False,
        explain=False,
        target_recall=0.8,
    )
    return out, metrics


def test_pick_threshold_reaches_target_recall():
    rng = np.random.default_rng(1)
    y = rng.integers(0, 2, 1000)
    proba = np.clip(y * 0.3 + rng.random(1000) * 0.7, 0, 1)
    threshold = pick_threshold(y, proba, target_recall=0.8)
    assert classification_metrics(y, proba, threshold)["recall"] >= 0.8


def test_capture_rate_is_perfect_for_perfect_scores():
    y = np.array([1, 1, 0, 0, 0, 0, 0, 0, 0, 0])
    assert capture_rate(y, y.astype(float), top_fraction=0.2) == 1.0


def test_every_model_returns_probabilities(raw_df):
    X, y = make_xy(clean(raw_df))
    X_tr, X_te, y_tr, _ = split(X, y)
    for name, pipeline in get_models().items():
        pipeline.fit(X_tr, y_tr)
        proba = pipeline.predict_proba(X_te)
        assert proba.shape == (len(X_te), 2), name
        assert np.isfinite(proba).all(), name


def test_pipeline_survives_unseen_category_and_missing_values(raw_df):
    X, y = make_xy(clean(raw_df))
    pipeline = get_models()["logistic_regression"].fit(X, y)
    odd = X.head(3).copy()
    odd.loc[odd.index[0], "Contract"] = "Brand new contract"
    odd.loc[odd.index[1], "Monthly_Charges"] = np.nan
    assert pipeline.predict_proba(odd).shape == (3, 2)


def test_training_writes_artifacts(trained):
    out, metrics = trained
    assert (out / "model.joblib").exists()
    assert (out / "reports" / "figures" / "model_comparison.png").exists()
    saved = json.loads((out / "reports" / "metrics.json").read_text())
    assert saved["selected_model"] == metrics["selected_model"]
    assert saved["selected_model"] != "dummy"


def test_final_model_reaches_roughly_target_recall(trained):
    _, metrics = trained
    assert metrics["test"]["recall"] > 0.6
    assert metrics["test"]["roc_auc"] > 0.6


def test_predict_scores_and_sorts(trained, raw_df):
    out, _ = trained
    bundle = joblib.load(out / "model.joblib")
    scored = score(raw_df.drop(columns=["Churn Label"]).head(50), bundle)
    assert list(scored.columns) == ["CustomerID", "churn_risk_score", "retention_flag"]
    assert scored["churn_risk_score"].is_monotonic_decreasing
    assert scored["retention_flag"].dtype == bool


def test_predict_rejects_missing_columns(trained, raw_df):
    out, _ = trained
    bundle = joblib.load(out / "model.joblib")
    with pytest.raises(KeyError):
        score(raw_df.drop(columns=["Contract"]), bundle)
