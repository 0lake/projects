"""Forecast accuracy metrics."""
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def smape(y_true, y_pred) -> float:
    return 100 * np.mean(2 * np.abs(y_pred - y_true) / (np.abs(y_true) + np.abs(y_pred) + 1e-8))


def mape(y_true, y_pred) -> float:
    return 100 * np.mean(np.abs((y_true - y_pred) / y_true))


def theils_u(y_true, y_pred) -> float:
    """RMSE of the model divided by RMSE of the one-step naive forecast on the test window."""
    naive = np.roll(y_true, 1)
    naive[0] = y_true[0]
    denom = np.sqrt(np.mean((naive - y_true) ** 2))
    return float(np.sqrt(np.mean((y_pred - y_true) ** 2)) / denom) if denom else np.nan


def mase(y_true, y_pred, y_train) -> float:
    """MAE scaled by the in-sample MAE of the one-step naive forecast."""
    scale = np.mean(np.abs(np.diff(y_train)))
    return float(np.mean(np.abs(y_true - y_pred)) / scale) if scale else np.nan


def evaluate(y_true, y_pred, y_train) -> dict:
    y_true, y_pred, y_train = (np.asarray(a, dtype=float) for a in (y_true, y_pred, y_train))
    return {
        "MAE": mean_absolute_error(y_true, y_pred),
        "MAPE (%)": mape(y_true, y_pred),
        "RMSE": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "sMAPE (%)": smape(y_true, y_pred),
        "R2": r2_score(y_true, y_pred),
        "Theil's U": theils_u(y_true, y_pred),
        "MASE": mase(y_true, y_pred, y_train),
    }


def metrics_table(predictions: dict, y_test, y_train) -> pd.DataFrame:
    rows = {name: evaluate(y_test.values, p.values, y_train.values) for name, p in predictions.items()}
    return pd.DataFrame(rows).T.rename_axis("Model")
