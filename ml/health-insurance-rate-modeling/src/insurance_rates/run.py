"""insurance-rates --csv data/Rate.csv --out results [--sample 300000]"""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from .config import CAT_FEATURES, CLASSES, FEATURES, FORBIDDEN, NUM_FEATURES, SEED, TARGET
from .data import clean, load
from .evaluate import (classification_scores, feature_importance, make_classes, regression_scores,
                       split_by_group)
from .models import classifiers, regressors


def run(csv: Path, out: Path, sample: int = 300_000, nrows: int | None = None, with_tobacco_rate: bool = False,
        fig_dir: Path | None = None) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    fig_dir = fig_dir or out
    fig_dir.mkdir(parents=True, exist_ok=True)

    df = clean(load(csv, nrows))
    if len(df) > sample:
        df = df.sample(sample, random_state=SEED)
    train, test = split_by_group(df)

    cat, num = list(CAT_FEATURES), list(NUM_FEATURES)
    if with_tobacco_rate:   # reproduces the near-leaky regression of the original lab
        num = num + ["IndividualTobaccoRate"]
        train = train.assign(IndividualTobaccoRate=train["IndividualTobaccoRate"].fillna(train["IndividualTobaccoRate"].median()))
        test = test.assign(IndividualTobaccoRate=test["IndividualTobaccoRate"].fillna(train["IndividualTobaccoRate"].median()))
    used = cat + num
    assert not set(used) & (set(FORBIDDEN) - ({"IndividualTobaccoRate"} if with_tobacco_rate else set()))

    # classification
    y_tr, y_te, thresholds = make_classes(train[TARGET], test[TARGET], CLASSES)
    clf_results = {}
    for name, model in classifiers(cat, num).items():
        model.fit(train[used], y_tr)
        clf_results[name] = classification_scores(y_te, model.predict(test[used]), CLASSES)
    best_clf = max((n for n in clf_results if not n.startswith("Baseline")), key=lambda n: clf_results[n]["f1_macro"])

    # regression
    reg_results, fitted = {}, {}
    for name, model in regressors(cat, num).items():
        model.fit(train[used], train[TARGET])
        fitted[name] = model
        reg_results[name] = regression_scores(test[TARGET], model.predict(test[used]))

    summary = {
        "rows_after_cleaning": int(len(df)), "train_rows": int(len(train)), "test_rows": int(len(test)),
        "features": used, "tercile_thresholds": thresholds, "best_classifier": best_clf,
        "classification": clf_results, "regression": reg_results,
    }
    tag = "with_tobacco_rate" if with_tobacco_rate else "main"
    (out / f"metrics_{tag}.json").write_text(json.dumps(summary, indent=2))

    # figures
    sns.set_theme(style="whitegrid", context="notebook")
    cm = np.array(clf_results[best_clf]["confusion_matrix"])
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.heatmap(cm / cm.sum(axis=1, keepdims=True), annot=cm, fmt="d", cmap="Blues", xticklabels=CLASSES,
                yticklabels=CLASSES, cbar=False, ax=ax)
    ax.set_xlabel("Predicted"); ax.set_ylabel("Actual"); ax.set_title(f"{best_clf}: confusion matrix")
    fig.tight_layout(); fig.savefig(fig_dir / f"confusion_matrix_{tag}.png", dpi=140); plt.close(fig)

    imp = feature_importance(fitted["Random forest"], test[used], test[TARGET])
    fig, ax = plt.subplots(figsize=(6, 3.6))
    imp.iloc[::-1].plot.barh(ax=ax, color="#4F46E5")
    ax.set_title("Permutation importance (RF regressor, drop in R²)")
    fig.tight_layout(); fig.savefig(fig_dir / f"feature_importance_{tag}.png", dpi=140); plt.close(fig)
    return summary


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--csv", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=Path("results"))
    ap.add_argument("--figures", type=Path, default=Path("assets/figures"))
    ap.add_argument("--sample", type=int, default=300_000, help="rows used for modelling")
    ap.add_argument("--nrows", type=int, default=None, help="read only the first N rows of the CSV")
    ap.add_argument("--with-tobacco-rate", action="store_true",
                    help="add IndividualTobaccoRate as a feature (near copy of the target, for comparison only)")
    a = ap.parse_args(argv)
    s = run(a.csv, a.out, a.sample, a.nrows, a.with_tobacco_rate, a.figures)
    print(json.dumps({k: v for k, v in s.items() if k in ("classification", "regression", "best_classifier")}, indent=2))


if __name__ == "__main__":
    main()
