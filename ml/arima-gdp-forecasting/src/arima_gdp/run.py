"""CLI: arima-gdp --csv path/to/data.csv  (or --download to fetch from Kaggle)."""
import argparse
from pathlib import Path

import pandas as pd

from .config import Config
from .data import download_csv, load_us_monthly, prepare, split_and_scale
from .metrics import metrics_table
from .models import fit_all
from .plots import plot_comparison, plot_forecast


def run(csv_path: Path, out_dir: Path, cfg: Config = Config()) -> pd.DataFrame:
    out_dir.mkdir(parents=True, exist_ok=True)
    y, X = prepare(load_us_monthly(csv_path), cfg)
    y_train, y_test, X_train, X_test = split_and_scale(y, X, cfg.test_size)
    print(f"train: {len(y_train)} months, test: {len(y_test)} months")

    predictions, info = fit_all(y_train, y_test, X_train, X_test, cfg)
    print("AutoARIMA selected:", info)

    table = metrics_table(predictions, y_test, y_train).sort_values("MAPE (%)")
    table.round(4).to_csv(out_dir / "metrics.csv")
    pd.DataFrame(predictions).to_csv(out_dir / "forecasts.csv")
    for name, pred in predictions.items():
        plot_forecast(name, y_train, y_test, pred, out_dir / f"forecast_{name.lower().replace(' ', '_')}.png")
    plot_comparison(y_train, y_test, predictions, out_dir / "comparison.png")
    print(table.round(4).to_string())
    return table


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--csv", type=Path, help="CSV file of the US Economic Indicators dataset")
    ap.add_argument("--download", action="store_true", help="download the dataset with kagglehub")
    ap.add_argument("--out", type=Path, default=Path("results"))
    args = ap.parse_args()
    if not args.csv and not args.download:
        ap.error("pass --csv PATH or --download")
    run(args.csv or download_csv(), args.out)


if __name__ == "__main__":
    main()
