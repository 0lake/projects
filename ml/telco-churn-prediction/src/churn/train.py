"""Train, compare and save the churn model.

    python -m churn.train --data data/Telco_customer_churn.xlsx

Steps:
1. Stratified train/test split (the test set is touched only for reporting).
2. Cross-validated probabilities for every candidate, selection by PR-AUC.
3. Optional randomized hyperparameter search for the selected model.
4. Decision threshold chosen on out-of-fold predictions to reach the target recall.
5. Final evaluation on the held-out test set, figures, saved model bundle.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold, cross_val_predict

from churn import __version__
from churn.config import (
    CV_FOLDS,
    DATA_PATH,
    FEATURES,
    MODELS_DIR,
    REPORTS_DIR,
    SEED,
    TARGET_RECALL,
)
from churn.data import clean, load_raw, make_xy, split
from churn.evaluate import capture_rate, classification_metrics, pick_threshold, ranking_metrics
from churn.explain import plot_permutation_importance, plot_shap
from churn.models import SEARCH_SPACES, get_models
from churn.plots import plot_confusion, plot_cumulative_gain, plot_model_comparison, plot_pr_curves


def run(
    data_path: Path = DATA_PATH,
    out_dir: Path = REPORTS_DIR,
    model_path: Path = MODELS_DIR / "churn_model.joblib",
    tune: bool = True,
    explain: bool = True,
    target_recall: float = TARGET_RECALL,
    n_iter: int = 15,
) -> dict:
    out_dir = Path(out_dir)
    figures = out_dir / "figures"
    figures.mkdir(parents=True, exist_ok=True)

    df = clean(load_raw(data_path))
    X, y = make_xy(df)
    X_train, X_test, y_train, y_test = split(X, y)
    cv = StratifiedKFold(CV_FOLDS, shuffle=True, random_state=SEED)

    # 1. Compare all candidates with cross-validation on the train set.
    models = get_models()
    rows, test_scores = [], {}
    for name, pipeline in models.items():
        oof = cross_val_predict(pipeline, X_train, y_train, cv=cv, method="predict_proba", n_jobs=-1)[:, 1]
        cv_rank = ranking_metrics(y_train, oof)
        pipeline.fit(X_train, y_train)
        scores = pipeline.predict_proba(X_test)[:, 1]
        test_scores[name] = scores
        at_half = classification_metrics(y_test, scores, 0.5)
        rows.append(
            {
                "model": name,
                "cv_roc_auc": cv_rank["roc_auc"],
                "cv_pr_auc": cv_rank["pr_auc"],
                "test_recall_at_0.5": at_half["recall"],
                "test_precision_at_0.5": at_half["precision"],
                "test_f1_at_0.5": at_half["f1"],
                "test_accuracy_at_0.5": at_half["accuracy"],
            }
        )
        print(f"{name:24s} CV PR-AUC {cv_rank['pr_auc']:.3f}  CV ROC-AUC {cv_rank['roc_auc']:.3f}")
    comparison = pd.DataFrame(rows)

    # 2. Select the best real model by cross-validated PR-AUC.
    candidates = comparison[comparison["model"] != "dummy"]
    best_name = candidates.sort_values("cv_pr_auc", ascending=False).iloc[0]["model"]
    best = models[best_name]
    print(f"\nSelected: {best_name}")

    # 3. Tune the selected model if a search space exists.
    best_params = {}
    if tune and best_name in SEARCH_SPACES:
        search = RandomizedSearchCV(
            best,
            SEARCH_SPACES[best_name],
            n_iter=n_iter,
            scoring="average_precision",
            cv=cv,
            random_state=SEED,
            n_jobs=-1,
        )
        search.fit(X_train, y_train)
        best, best_params = search.best_estimator_, search.best_params_
        print(f"Tuned PR-AUC (CV): {search.best_score_:.3f}  params: {best_params}")

    # 4. Choose the decision threshold on out-of-fold predictions.
    oof = cross_val_predict(best, X_train, y_train, cv=cv, method="predict_proba", n_jobs=-1)[:, 1]
    threshold = pick_threshold(y_train, oof, target_recall)
    best.fit(X_train, y_train)

    # 5. Final evaluation on the untouched test set.
    final_scores = best.predict_proba(X_test)[:, 1]
    final = {
        **classification_metrics(y_test, final_scores, threshold),
        **ranking_metrics(y_test, final_scores),
        "capture_top_20_percent": capture_rate(y_test, final_scores, 0.2),
        "baseline_churn_rate": float(y_test.mean()),
    }
    test_scores["selected_tuned"] = final_scores

    plot_model_comparison(comparison, best_name, figures / "model_comparison.png")
    plot_pr_curves(
        y_test,
        {k: v for k, v in test_scores.items() if k not in {"dummy", "selected_tuned"}},
        figures / "pr_curves.png",
    )
    plot_confusion(final, figures / "confusion_matrix.png")
    plot_cumulative_gain(y_test, final_scores, figures / "cumulative_gain.png")

    importance = None
    shap_done = False
    if explain:
        importance = plot_permutation_importance(best, X_test, y_test, figures / "permutation_importance.png")
        shap_done = plot_shap(best, X_test, figures)

    # Save artifacts.
    comparison.to_csv(out_dir / "model_comparison.csv", index=False)
    metrics = {
        "version": __version__,
        "selected_model": best_name,
        "best_params": {k.replace("model__", ""): v for k, v in best_params.items()},
        "target_recall": target_recall,
        "threshold": threshold,
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
        "test": final,
        "comparison": comparison.round(4).to_dict(orient="records"),
        "top_permutation_features": None if importance is None else importance.head(8).round(4).to_dict(),
        "shap": shap_done,
    }
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2, default=str), encoding="utf-8")

    model_path = Path(model_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "pipeline": best,
            "threshold": threshold,
            "features": FEATURES,
            "model_name": best_name,
            "target_recall": target_recall,
        },
        model_path,
    )

    print(
        f"\nTest @ threshold {threshold:.3f}: recall {final['recall']:.3f}, precision {final['precision']:.3f}, "
        f"F1 {final['f1']:.3f}, PR-AUC {final['pr_auc']:.3f}, ROC-AUC {final['roc_auc']:.3f}"
    )
    print(f"Model saved to {model_path}")
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the churn model.")
    parser.add_argument("--data", type=Path, default=DATA_PATH, help="Path to the dataset (.xlsx or .csv)")
    parser.add_argument("--reports", type=Path, default=REPORTS_DIR, help="Where to write metrics and figures")
    parser.add_argument("--model-out", type=Path, default=MODELS_DIR / "churn_model.joblib")
    parser.add_argument("--target-recall", type=float, default=TARGET_RECALL)
    parser.add_argument("--no-tune", action="store_true", help="Skip hyperparameter search")
    parser.add_argument("--no-explain", action="store_true", help="Skip permutation importance and SHAP")
    args = parser.parse_args()
    run(
        data_path=args.data,
        out_dir=args.reports,
        model_path=args.model_out,
        tune=not args.no_tune,
        explain=not args.no_explain,
        target_recall=args.target_recall,
    )


if __name__ == "__main__":
    main()
