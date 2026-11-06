"""Internal validity metrics, choice of k and agreement between algorithms."""
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, calinski_harabasz_score, davies_bouldin_score, silhouette_score


def score(X: np.ndarray, labels: np.ndarray) -> dict:
    sizes = np.bincount(labels)
    return {
        "silhouette": silhouette_score(X, labels),
        "davies_bouldin": davies_bouldin_score(X, labels),
        "calinski_harabasz": calinski_harabasz_score(X, labels),
        "min_cluster_share": sizes.min() / len(labels),
        "max_cluster_share": sizes.max() / len(labels),
    }


def compare(X: np.ndarray, label_sets: dict) -> pd.DataFrame:
    return pd.DataFrame({name: score(X, lab) for name, lab in label_sets.items()}).T.rename_axis("algorithm")


def scan_k(X: np.ndarray, ks=range(2, 9), seed: int = 42) -> pd.DataFrame:
    rows = []
    for k in ks:
        km = KMeans(k, n_init=10, random_state=seed).fit(X)
        rows.append({"k": k, "inertia": km.inertia_, "silhouette": silhouette_score(X, km.labels_)})
    return pd.DataFrame(rows)


def agreement(label_sets: dict) -> pd.DataFrame:
    names = list(label_sets)
    m = pd.DataFrame(index=names, columns=names, dtype=float)
    for a in names:
        for b in names:
            m.loc[a, b] = adjusted_rand_score(label_sets[a], label_sets[b])
    return m
