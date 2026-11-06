"""Metrics and decision-threshold selection."""

from __future__ import annotations

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)

from churn.config import TARGET_RECALL


def pick_threshold(y_true, proba, target_recall: float = TARGET_RECALL) -> float:
    """Highest threshold that still reaches the target recall.

    The higher the threshold, the fewer customers are flagged, so this keeps
    false alarms as low as possible while meeting the recall requirement.
    """
    _, recall, thresholds = precision_recall_curve(y_true, proba)
    ok = np.where(recall[:-1] >= target_recall)[0]
    if len(ok) == 0:
        return float(thresholds[0])
    return float(thresholds[ok[-1]])


def ranking_metrics(y_true, proba) -> dict[str, float]:
    """Threshold-free quality of the probability ranking."""
    return {
        "roc_auc": float(roc_auc_score(y_true, proba)),
        "pr_auc": float(average_precision_score(y_true, proba)),
    }


def classification_metrics(y_true, proba, threshold: float = 0.5) -> dict[str, float]:
    """Quality of the yes/no decision at a given threshold."""
    proba = np.asarray(proba)
    pred = (proba >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, pred, labels=[0, 1]).ravel()
    return {
        "threshold": float(threshold),
        "recall": float(recall_score(y_true, pred, zero_division=0)),
        "precision": float(precision_score(y_true, pred, zero_division=0)),
        "f1": float(f1_score(y_true, pred, zero_division=0)),
        "accuracy": float(accuracy_score(y_true, pred)),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
        "flagged_share": float(pred.mean()),
    }


def capture_rate(y_true, proba, top_fraction: float = 0.2) -> float:
    """Share of all churners found in the top `top_fraction` of scored customers."""
    y_true = np.asarray(y_true)
    order = np.argsort(-np.asarray(proba), kind="stable")
    k = max(1, int(round(len(y_true) * top_fraction)))
    total = y_true.sum()
    return float(y_true[order][:k].sum() / total) if total else 0.0
