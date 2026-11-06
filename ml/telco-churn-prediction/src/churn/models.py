"""Model zoo and hyperparameter search spaces."""

from __future__ import annotations

from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier

from churn.config import SEED
from churn.features import build_preprocessor


def _pipeline(estimator) -> Pipeline:
    return Pipeline([("preprocessor", build_preprocessor()), ("model", estimator)])


def get_models(seed: int = SEED) -> dict[str, Pipeline]:
    """All candidates. Every real model uses class balancing."""
    return {
        "dummy": _pipeline(DummyClassifier(strategy="prior")),
        "logistic_regression": _pipeline(
            LogisticRegression(max_iter=2000, class_weight="balanced", random_state=seed)
        ),
        "decision_tree": _pipeline(
            DecisionTreeClassifier(
                max_depth=5,
                min_samples_split=50,
                class_weight="balanced",
                random_state=seed,
            )
        ),
        "random_forest": _pipeline(
            RandomForestClassifier(
                n_estimators=400,
                max_depth=8,
                min_samples_leaf=5,
                class_weight="balanced_subsample",
                n_jobs=1,
                random_state=seed,
            )
        ),
        "hist_gradient_boosting": _pipeline(
            HistGradientBoostingClassifier(
                max_depth=3,
                learning_rate=0.05,
                max_iter=300,
                class_weight="balanced",
                random_state=seed,
            )
        ),
    }


SEARCH_SPACES: dict[str, dict[str, list]] = {
    "random_forest": {
        "model__n_estimators": [300, 500, 800],
        "model__max_depth": [5, 8, 12, None],
        "model__min_samples_leaf": [2, 5, 10, 20],
        "model__max_features": ["sqrt", 0.5, None],
    },
    "hist_gradient_boosting": {
        "model__max_depth": [2, 3, 4, None],
        "model__learning_rate": [0.03, 0.05, 0.1],
        "model__max_iter": [150, 300, 500],
        "model__min_samples_leaf": [20, 40, 80],
        "model__l2_regularization": [0.0, 1.0, 10.0],
    },
}
