"""Forecast and metric plots."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

STYLE = {
    "ARIMA": "#2ca02c", "SARIMA": "#ff7f0e", "AutoARIMA": "#9467bd",
    "ARIMAX": "#1f77b4", "SARIMAX": "#d62728", "Naive": "#7f7f7f", "Seasonal naive": "#8c564b",
}


def plot_forecast(name, y_train, y_test, y_pred, out: Path):
    sns.set_theme(style="whitegrid", context="notebook")
    fig, ax = plt.subplots(figsize=(11, 4.2))
    ax.plot(y_train.index.to_timestamp(), y_train.values, color="#444", label="Train")
    ax.plot(y_test.index.to_timestamp(), y_test.values, color="#999", lw=2.2, label="Actual")
    ax.plot(y_pred.index.to_timestamp(), y_pred.values, color=STYLE.get(name, "C0"), ls="--", lw=2, label=name)
    ax.set_title(f"US GDP forecast: {name}")
    ax.set_ylabel("GDP, constant prices (growth, %)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out, dpi=140)
    plt.close(fig)


def plot_comparison(y_train, y_test, predictions, out: Path):
    sns.set_theme(style="whitegrid", context="notebook")
    fig, ax = plt.subplots(figsize=(11, 4.8))
    ax.plot(y_test.index.to_timestamp(), y_test.values, color="black", lw=2.4, label="Actual")
    for name, pred in predictions.items():
        ax.plot(pred.index.to_timestamp(), pred.values, color=STYLE.get(name, "C0"), lw=1.6, label=name)
    ax.set_title("Test window: all models vs actual")
    ax.legend(ncol=4, fontsize=8)
    fig.tight_layout()
    fig.savefig(out, dpi=140)
    plt.close(fig)
