"""Model explanations: permutation importance and SHAP."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier  # noqa: E402
from sklearn.inspection import permutation_importance  # noqa: E402
from sklearn.tree import DecisionTreeClassifier  # noqa: E402

from churn.config import SEED  # noqa: E402
from churn.plots import ACCENT, _save, _style  # noqa: E402

TREE_MODELS = (RandomForestClassifier, GradientBoostingClassifier, DecisionTreeClassifier)


def plot_permutation_importance(pipeline, X: pd.DataFrame, y, path: Path, top: int = 12) -> pd.Series:
    """How much PR-AUC drops when one original feature is shuffled."""
    result = permutation_importance(
        pipeline,
        X,
        y,
        scoring="average_precision",
        n_repeats=10,
        random_state=SEED,
        n_jobs=-1,
    )
    importance = pd.Series(result.importances_mean, index=X.columns).sort_values()
    _style()
    fig, ax = plt.subplots(figsize=(8, 5))
    tail = importance.tail(top)
    ax.barh(tail.index, tail.values, color=ACCENT)
    ax.set_xlabel("Drop in PR-AUC when the feature is shuffled")
    ax.set_title("Permutation importance (test)")
    ax.grid(axis="y", visible=False)
    _save(fig, path)
    return importance.sort_values(ascending=False)


def plot_shap(pipeline, X: pd.DataFrame, out_dir: Path, sample: int = 300) -> bool:
    """SHAP beeswarm and a waterfall for the highest-risk customer.

    Only tree models are supported. Returns False when SHAP was skipped.
    """
    model = pipeline.named_steps["model"]
    if not isinstance(model, TREE_MODELS):
        return False

    import shap

    preprocessor = pipeline.named_steps["preprocessor"]
    subset = X.sample(min(sample, len(X)), random_state=SEED)
    names = preprocessor.get_feature_names_out()
    matrix = pd.DataFrame(preprocessor.transform(subset), columns=names, index=subset.index)

    values = shap.TreeExplainer(model)(matrix)
    if values.values.ndim == 3:
        values = values[..., 1]

    out_dir.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(9, 5.5))
    shap.plots.beeswarm(values, max_display=12, show=False)
    plt.title("SHAP: what pushes churn risk up or down", fontweight="bold")
    plt.savefig(out_dir / "shap_beeswarm.png", bbox_inches="tight", dpi=140, facecolor="white")
    plt.close("all")

    riskiest = int(np.argmax(model.predict_proba(matrix)[:, 1]))
    plt.figure()
    shap.plots.waterfall(values[riskiest], max_display=10, show=False)
    plt.savefig(out_dir / "shap_waterfall_high_risk.png", bbox_inches="tight", dpi=140, facecolor="white")
    plt.close("all")
    return True
