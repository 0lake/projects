import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, mean_absolute_error, mean_squared_error, r2_score

from .config import SEED


def split_by_group(df: pd.DataFrame, group: str = "PlanId", test_size: float = 0.2, seed: int = SEED):
    """Hold out whole plans: the same plan appears for many ages and years, and a random row split
    would put near-identical rows on both sides."""
    from sklearn.model_selection import GroupShuffleSplit
    groups = df[group] if group in df.columns else np.arange(len(df))
    idx_train, idx_test = next(GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=seed)
                               .split(df, groups=groups))
    return df.iloc[idx_train].reset_index(drop=True), df.iloc[idx_test].reset_index(drop=True)


def make_classes(train_rate: pd.Series, test_rate: pd.Series, labels=("Low", "Medium", "High")):
    """Tercile thresholds from the TRAIN rates only."""
    q1, q2 = train_rate.quantile([1 / 3, 2 / 3])
    def cut(s):
        return pd.cut(s, [-np.inf, q1, q2, np.inf], labels=list(labels)).astype(str)
    return cut(train_rate), cut(test_rate), (float(q1), float(q2))


def classification_scores(y_true, y_pred, labels) -> dict:
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "f1_macro": float(f1_score(y_true, y_pred, average="macro")),
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=labels).tolist(),
    }


def regression_scores(y_true, y_pred) -> dict:
    return {"mae": float(mean_absolute_error(y_true, y_pred)),
            "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
            "r2": float(r2_score(y_true, y_pred))}


def feature_importance(model, X: pd.DataFrame, y, n: int = 4000, seed: int = SEED) -> pd.Series:
    sample = X.sample(min(n, len(X)), random_state=seed)
    result = permutation_importance(model, sample, pd.Series(y).loc[sample.index] if hasattr(y, "loc") else y[sample.index],
                                    n_repeats=3, random_state=seed, n_jobs=-1)
    return pd.Series(result.importances_mean, index=X.columns).sort_values(ascending=False)
