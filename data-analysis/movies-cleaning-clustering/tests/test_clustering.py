import numpy as np
import pandas as pd
import pytest
from sklearn.cluster import KMeans

from movies_clustering.algorithms import custom_kmeans, run_all
from movies_clustering.config import FEATURES
from movies_clustering.data import flag_median_filled, load, scale
from movies_clustering.evaluate import agreement, score
from movies_clustering.run import run


@pytest.fixture(scope="module")
def blobs():
    rng = np.random.default_rng(0)
    centers = np.array([[0, 0], [8, 8], [0, 8], [8, 0]], dtype=float)
    return np.vstack([c + rng.normal(scale=0.6, size=(150, 2)) for c in centers])


@pytest.fixture()
def movies_csv(tmp_path):
    rng = np.random.default_rng(1)
    n = 400
    df = pd.DataFrame({
        "Movie.Rating": rng.normal(6.7, 0.8, n).round(1),
        "Votes": rng.integers(10_000, 200_000, n),
        "MetaScore": rng.integers(25, 95, n),
        "Gross": rng.integers(0, 70_000_000, n).astype(float),
        "Run.Time.in.minutes": rng.integers(70, 160, n),
    })
    path = tmp_path / "m.csv"
    df.to_csv(path, index=False)
    return path


def test_custom_kmeans_matches_sklearn_on_clear_blobs(blobs):
    labels, centroids, inertia, iters = custom_kmeans(blobs, 4)
    ref = KMeans(4, n_init=10, random_state=0).fit(blobs)
    assert inertia == pytest.approx(ref.inertia_, rel=1e-3)
    assert sorted(np.bincount(labels)) == [150, 150, 150, 150]
    assert iters < 100


def test_all_algorithms_find_the_blobs(blobs):
    sets = run_all(blobs, 4)
    assert len(sets) == 5
    ari = agreement(sets)
    assert (ari.values > 0.95).all()
    assert score(blobs, sets["Ward"])["silhouette"] > 0.6


def test_scaling(movies_csv):
    df = load(movies_csv)
    for log in (False, True):
        X = scale(df, log=log)
        assert X.shape == (400, len(FEATURES)) and abs(X.mean()) < 1e-9


def test_load_rejects_missing_columns(movies_csv, tmp_path):
    bad = load(movies_csv).drop(columns=["Votes"])
    path = tmp_path / "bad.csv"
    bad.to_csv(path, index=False)
    with pytest.raises(ValueError):
        load(path)


def test_median_filled_flag():
    df = pd.DataFrame({"Gross": [1.0, 5.0, 5.0, 9.0, 5.0], "MetaScore": [1, 2, 3, 4, 7]})
    # Gross median is 5.0, MetaScore median is 3
    assert flag_median_filled(df).tolist() == [False, True, True, False, True]


def test_end_to_end(movies_csv, tmp_path):
    res = run(movies_csv, tmp_path / "r", k=3, fig_dir=tmp_path / "f")
    assert res["table"].shape[0] == 5
    assert (tmp_path / "f" / "pca_clusters_raw.png").exists()
    assert res["profile"]["size"].sum() == 400
