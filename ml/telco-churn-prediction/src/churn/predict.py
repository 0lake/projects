"""Score new customers with a trained model.

    python -m churn.predict --input new_customers.xlsx --output scored.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd

from churn.config import FEATURES, MODELS_DIR
from churn.data import clean, load_raw, normalize_columns


def score(df: pd.DataFrame, bundle: dict) -> pd.DataFrame:
    """Return a churn risk score and a retention flag for every customer.

    The flag uses the threshold chosen during training, so it reaches the
    target recall rather than the default 0.5 cut-off. The score ranks
    customers by risk; because training used class balancing it is not a
    calibrated probability.
    """
    cleaned = clean(df)
    missing = [c for c in FEATURES if c not in cleaned.columns]
    if missing:
        raise KeyError(f"Missing columns: {missing}")

    proba = bundle["pipeline"].predict_proba(cleaned[FEATURES])[:, 1]
    out = pd.DataFrame(index=cleaned.index)
    for id_col in ("CustomerID", "Customer_ID"):
        if id_col in normalize_columns(df).columns:
            out[id_col] = normalize_columns(df)[id_col]
    out["churn_risk_score"] = proba.round(4)
    out["retention_flag"] = proba >= bundle["threshold"]
    return out.sort_values("churn_risk_score", ascending=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Score customers for churn risk.")
    parser.add_argument("--input", type=Path, required=True, help="Customers file (.xlsx or .csv)")
    parser.add_argument("--output", type=Path, default=Path("scored_customers.csv"))
    parser.add_argument("--model", type=Path, default=MODELS_DIR / "churn_model.joblib")
    args = parser.parse_args()

    if not args.model.exists():
        raise SystemExit(f"Model not found: {args.model}. Run `python -m churn.train` first.")

    bundle = joblib.load(args.model)
    scored = score(load_raw(args.input), bundle)
    scored.to_csv(args.output, index=False)
    flagged = int(scored["retention_flag"].sum())
    print(f"Scored {len(scored)} customers, {flagged} flagged for retention. Saved to {args.output}")


if __name__ == "__main__":
    main()
