import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.decomposition import PCA

PALETTE = ["#6366F1", "#F59E0B", "#10B981", "#EC4899", "#06B6D4", "#EF4444"]


def pca_grid(X, label_sets: dict, out):
    sns.set_theme(style="whitegrid", context="notebook")
    Z = PCA(n_components=2, random_state=0).fit_transform(X)
    n = len(label_sets)
    cols = 3
    rows = int(np.ceil(n / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 4.2 * rows), squeeze=False)
    for ax, (name, lab) in zip(axes.ravel(), label_sets.items()):
        for c in np.unique(lab):
            m = lab == c
            ax.scatter(Z[m, 0], Z[m, 1], s=4, alpha=0.5, color=PALETTE[c % len(PALETTE)], label=f"{c}")
        ax.set_title(name)
        ax.set_xlabel("PC1"); ax.set_ylabel("PC2")
    for ax in axes.ravel()[n:]:
        ax.axis("off")
    fig.tight_layout(); fig.savefig(out, dpi=140); plt.close(fig)


def k_selection(df, out):
    sns.set_theme(style="whitegrid", context="notebook")
    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4))
    a.plot(df["k"], df["inertia"], marker="o", color=PALETTE[0]); a.set_title("Elbow: inertia")
    b.plot(df["k"], df["silhouette"], marker="o", color=PALETTE[1]); b.set_title("Silhouette")
    for ax in (a, b):
        ax.set_xlabel("k")
    fig.tight_layout(); fig.savefig(out, dpi=140); plt.close(fig)


def profile_heatmap(profile, out):
    sns.set_theme(style="white", context="notebook")
    z = (profile - profile.mean()) / profile.std(ddof=0)
    fig, ax = plt.subplots(figsize=(8, 3.6))
    sns.heatmap(z, annot=profile.round(1), fmt="", cmap="vlag", center=0, cbar_kws={"label": "z-score of cluster mean"}, ax=ax)
    ax.set_title("Cluster profiles (values: means in original units)")
    fig.tight_layout(); fig.savefig(out, dpi=140); plt.close(fig)
