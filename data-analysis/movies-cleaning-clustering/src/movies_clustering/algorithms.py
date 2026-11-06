"""K-Means written by hand plus the scikit-learn algorithms used for comparison."""
import numpy as np
from sklearn.cluster import AgglomerativeClustering, KMeans, MiniBatchKMeans
from sklearn.mixture import GaussianMixture


def custom_kmeans(X: np.ndarray, k: int, max_iter: int = 100, seed: int = 42, n_init: int = 10):
    """Lloyd's algorithm with random initial centroids, repeated n_init times (best inertia wins).
    Returns labels, centroids, inertia, iterations of the best run."""
    best = None
    for run in range(n_init):
        rng = np.random.default_rng(seed + run)
        centroids = X[rng.choice(len(X), k, replace=False)]
        for iteration in range(1, max_iter + 1):
            dist = np.linalg.norm(X[:, None, :] - centroids[None, :, :], axis=2)
            labels = dist.argmin(axis=1)
            new = np.array([X[labels == i].mean(axis=0) if np.any(labels == i) else centroids[i]
                            for i in range(k)])
            if np.allclose(centroids, new):
                break
            centroids = new
        inertia = float(((X - centroids[labels]) ** 2).sum())
        if best is None or inertia < best[2]:
            best = (labels, centroids, inertia, iteration)
    return best


def run_all(X: np.ndarray, k: int = 4, seed: int = 42) -> dict:
    """name -> labels for every algorithm."""
    labels = {}
    labels["Custom K-Means"] = custom_kmeans(X, k, seed=seed)[0]
    labels["K-Means (sklearn)"] = KMeans(k, n_init=10, random_state=seed).fit_predict(X)
    labels["MiniBatch K-Means"] = MiniBatchKMeans(k, batch_size=5000, n_init=10, random_state=seed).fit_predict(X)
    labels["Gaussian Mixture"] = GaussianMixture(k, covariance_type="full", random_state=seed).fit(X).predict(X)
    labels["Ward"] = AgglomerativeClustering(k, linkage="ward").fit_predict(X)
    return labels
