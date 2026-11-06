"""Figures for the report. All functions save a PNG and close the figure."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.metrics import precision_recall_curve  # noqa: E402

ACCENT = "#0F766E"
MUTED = "#94A3B8"
WARN = "#EA580C"


def _style() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 140,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.25,
            "axes.titleweight": "bold",
            "axes.titlesize": 13,
            "font.size": 11,
        }
    )


def _save(fig, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_model_comparison(table: pd.DataFrame, best: str, path: Path) -> None:
    """Cross-validated PR-AUC per model (bigger is better)."""
    _style()
    data = table.sort_values("cv_pr_auc")
    colors = [ACCENT if m == best else MUTED for m in data["model"]]
    fig, ax = plt.subplots(figsize=(8, 4.2))
    bars = ax.barh(data["model"], data["cv_pr_auc"], color=colors)
    for bar, value in zip(bars, data["cv_pr_auc"]):
        ax.text(value + 0.005, bar.get_y() + bar.get_height() / 2, f"{value:.3f}", va="center")
    ax.set_xlim(0, max(0.8, data["cv_pr_auc"].max() + 0.08))
    ax.set_xlabel("PR-AUC (5-fold cross-validation on train)")
    ax.set_title("Model comparison")
    ax.grid(axis="y", visible=False)
    _save(fig, path)


def plot_pr_curves(y_true, scores: dict[str, np.ndarray], path: Path) -> None:
    """Precision-recall curves on the held-out test set."""
    _style()
    fig, ax = plt.subplots(figsize=(7, 5))
    for name, proba in scores.items():
        precision, recall, _ = precision_recall_curve(y_true, proba)
        ax.plot(recall, precision, label=name, linewidth=2)
    ax.axhline(np.mean(y_true), color=MUTED, linestyle="--", label="random")
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.set_title("Precision-recall curves (test)")
    ax.legend(frameon=False)
    _save(fig, path)


def plot_confusion(metrics: dict, path: Path) -> None:
    """Confusion matrix at the operating threshold."""
    _style()
    matrix = np.array([[metrics["tn"], metrics["fp"]], [metrics["fn"], metrics["tp"]]])
    fig, ax = plt.subplots(figsize=(5.2, 4.4))
    ax.imshow(matrix, cmap="GnBu")
    ax.grid(False)
    labels = ["Stayed", "Left"]
    ax.set_xticks([0, 1], labels=[f"Predicted: {l}" for l in labels])
    ax.set_yticks([0, 1], labels=[f"Actual: {l}" for l in labels])
    for i in range(2):
        for j in range(2):
            ax.text(j, i, f"{matrix[i, j]}", ha="center", va="center", fontsize=18, fontweight="bold",
                    color="white" if matrix[i, j] > matrix.max() * 0.6 else "#0F172A")
    ax.set_title(f"Confusion matrix (threshold {metrics['threshold']:.2f})")
    _save(fig, path)


def plot_cumulative_gain(y_true, proba, path: Path) -> None:
    """Share of churners found when contacting the top-scored customers first."""
    _style()
    y_true = np.asarray(y_true)
    order = np.argsort(-np.asarray(proba), kind="stable")
    gain = np.cumsum(y_true[order]) / y_true.sum()
    share = np.arange(1, len(y_true) + 1) / len(y_true)
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(share, gain, color=ACCENT, linewidth=2.5, label="model")
    ax.plot([0, 1], [0, 1], color=MUTED, linestyle="--", label="random")
    k = int(round(len(y_true) * 0.2))
    ax.scatter([0.2], [gain[k - 1]], color=WARN, zorder=3)
    ax.annotate(f"top 20% of customers\nfind {gain[k - 1]:.0%} of churners",
                (0.2, gain[k - 1]), xytext=(0.32, gain[k - 1] - 0.18), arrowprops={"arrowstyle": "->"})
    ax.set_xlabel("Share of customers contacted (highest risk first)")
    ax.set_ylabel("Share of churners found")
    ax.set_title("Cumulative gain (test)")
    ax.legend(frameon=False, loc="lower right")
    _save(fig, path)
