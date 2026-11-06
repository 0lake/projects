"""movies-clustering --csv data/movies_clean.csv --out results [--log] [--k 4]"""
import argparse
import json
from pathlib import Path

import pandas as pd

from .algorithms import run_all
from .config import FEATURES, K, SEED
from .data import flag_median_filled, load, scale
from .evaluate import agreement, compare, scan_k
from .plots import k_selection, pca_grid, profile_heatmap


def run(csv: Path, out: Path, k: int = K, log: bool = False, seed: int = SEED, fig_dir: Path | None = None) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    fig_dir = fig_dir or out
    fig_dir.mkdir(parents=True, exist_ok=True)
    df = load(csv)
    X = scale(df, log=log)
    tag = "log" if log else "raw"

    labels = run_all(X, k, seed)
    table = compare(X, labels)
    table.round(4).to_csv(out / f"metrics_{tag}.csv")
    agreement(labels).round(3).to_csv(out / f"agreement_ari_{tag}.csv")

    scan = scan_k(X, seed=seed)
    scan.round(4).to_csv(out / f"k_scan_{tag}.csv", index=False)

    best = table["silhouette"].idxmax()
    df = df.assign(cluster=labels[best])
    profile = df.groupby("cluster")[FEATURES].mean()
    profile.insert(0, "size", df.groupby("cluster").size())
    profile.round(2).to_csv(out / f"cluster_profile_{tag}.csv")

    pca_grid(X, labels, fig_dir / f"pca_clusters_{tag}.png")
    k_selection(scan, fig_dir / f"k_selection_{tag}.png")
    profile_heatmap(profile[FEATURES], fig_dir / f"profiles_{tag}.png")

    filled = flag_median_filled(df)
    summary = {
        "rows": len(df), "k": k, "log_transform": log, "best_by_silhouette": best,
        "share_rows_with_median_filled_gross_or_metascore": round(float(filled.mean()), 3),
    }
    (out / f"summary_{tag}.json").write_text(json.dumps(summary, indent=2))
    return {"table": table, "scan": scan, "profile": profile, "summary": summary}


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--csv", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=Path("results"))
    ap.add_argument("--figures", type=Path, default=Path("assets/figures"))
    ap.add_argument("--k", type=int, default=K)
    ap.add_argument("--log", action="store_true", help="log1p-transform Votes and Gross before scaling")
    a = ap.parse_args(argv)
    res = run(a.csv, a.out, a.k, a.log, fig_dir=a.figures)
    print(res["table"].round(3).to_string())
    print(res["summary"])


if __name__ == "__main__":
    main()
