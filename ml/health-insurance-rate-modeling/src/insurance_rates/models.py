"""Pipelines for classification and regression."""
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, VotingClassifier
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .config import CAT_FEATURES, NUM_FEATURES, SEED


def preprocessor(cat=CAT_FEATURES, num=NUM_FEATURES) -> ColumnTransformer:
    return ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore", min_frequency=20), list(cat)),
        ("num", StandardScaler(), list(num)),
    ])


def classifiers(cat=CAT_FEATURES, num=NUM_FEATURES, n_trees: int = 60) -> dict:
    lr = LogisticRegression(max_iter=300, class_weight="balanced")
    rf = RandomForestClassifier(n_estimators=n_trees, max_depth=18, min_samples_leaf=3, n_jobs=-1,
                                class_weight="balanced", random_state=SEED)
    models = {
        "Baseline (most frequent)": DummyClassifier(strategy="most_frequent"),
        "Logistic regression": lr,
        "Random forest": rf,
        "Voting (LR + RF, soft)": VotingClassifier([("lr", lr), ("rf", rf)], voting="soft"),
    }
    return {name: Pipeline([("prep", preprocessor(cat, num)), ("model", m)]) for name, m in models.items()}


def regressors(cat=CAT_FEATURES, num=NUM_FEATURES, n_trees: int = 60) -> dict:
    models = {
        "Baseline (mean)": DummyRegressor(),
        "Ridge": Ridge(alpha=1.0),
        "Random forest": RandomForestRegressor(n_estimators=n_trees, max_depth=18, min_samples_leaf=3,
                                               n_jobs=-1, random_state=SEED),
    }
    return {name: Pipeline([("prep", preprocessor(cat, num)), ("model", m)]) for name, m in models.items()}
