import numpy as np
import pandas as pd
import pytest

from arima_gdp.config import EXOG, TARGET, Config
from arima_gdp.data import load_us_monthly, prepare, split_and_scale
from arima_gdp.metrics import evaluate, mase, smape, theils_u
from arima_gdp.run import run


@pytest.fixture(scope="session")
def csv_path(tmp_path_factory):
    rng = np.random.default_rng(0)
    dates = pd.date_range("1991-01-01", periods=240, freq="MS")
    X = rng.normal(size=(240, len(EXOG))).cumsum(axis=0) * 0.1
    y = 2 + X[:, 0] + rng.normal(scale=0.2, size=240)
    df = pd.DataFrame(X, columns=EXOG)
    df[TARGET] = y
    df["Date"] = dates.strftime("%d-%m-%Y")
    df["place_name"] = "United States"
    df["frequency"] = "monthly"
    other = df.copy()
    other["place_name"] = "Canada"
    path = tmp_path_factory.mktemp("d") / "data.csv"
    pd.concat([df, other]).to_csv(path, index=False)
    return path


def test_filters_us_monthly(csv_path):
    assert set(load_us_monthly(csv_path)["place_name"]) == {"United States"}


def test_split_is_chronological_and_scaled_on_train(csv_path):
    y, X = prepare(load_us_monthly(csv_path), Config())
    y_tr, y_te, X_tr, X_te = split_and_scale(y, X, 0.2)
    assert y_tr.index.max() < y_te.index.min()
    assert len(y_te) == 48
    assert np.allclose(X_tr.mean(), 0, atol=1e-9)


def test_metrics_basics():
    y = np.array([1.0, 2.0, 3.0, 4.0])
    assert evaluate(y, y, y)["MAE"] == 0
    assert smape(y, y) == pytest.approx(0, abs=1e-6)
    assert theils_u(y, y) == 0
    assert mase(y, y + 1, np.array([0.0, 1.0, 2.0])) == pytest.approx(1.0)


def test_end_to_end(csv_path, tmp_path):
    table = run(csv_path, tmp_path)
    assert set(table.index) == {"Naive", "Seasonal naive", "ARIMA", "SARIMA", "AutoARIMA", "ARIMAX", "SARIMAX"}
    assert (tmp_path / "metrics.csv").exists() and (tmp_path / "comparison.png").exists()
    assert table.loc["ARIMAX", "RMSE"] < table.loc["Naive", "RMSE"]
