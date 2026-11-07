import numpy as np
import pytest

from complexplane.engine import ESCAPE_RADIUS, compute, escapes, mandelbrot_interior
from complexplane.grid import View, make_view


def single(c: complex, max_iter: int = 400, kind: str = "mandelbrot", julia_c: complex = 0j):
    view = View(center=c, width=1e-6, px_width=1, px_height=1)
    return compute(view, kind=kind, c=julia_c, max_iter=max_iter, bailout=2.0)


@pytest.mark.parametrize("c", [0j, -1 + 0j, 0.25 + 0j, -2 + 0j, -0.12 + 0.74j, 1j * 0.0 - 0.5])
def test_known_members_do_not_escape(c):
    assert single(c).inside[0, 0]


@pytest.mark.parametrize("c", [0.26 + 0j, 1 + 0j, 0.5 + 0.6j, -2.01 + 0j, 2 + 2j, 1j * 1.2 + 0.4])
def test_known_non_members_escape(c):
    assert not single(c).inside[0, 0]


def test_cardioid_shortcut_matches_iteration():
    view = make_view(-0.3, 1.6, 160, aspect=1.5)
    grid = view.grid()
    shortcut = mandelbrot_interior(grid)
    for c in grid[shortcut][:300]:
        assert not escapes(c, max_iter=600)


def test_escape_iteration_is_monotone_in_max_iter():
    view = make_view(-0.75, 0.3, 120, aspect=1.0)
    few = compute(view, max_iter=30, bailout=2.0)
    many = compute(view, max_iter=300, bailout=2.0)
    # то, что не ушло за 300 итераций, не ушло и за 30
    assert (few.inside | ~many.inside).all()
    # у точек, ушедших в обоих запусках, номер выхода одинаков
    both = ~few.inside & ~many.inside
    assert (few.n[both] == many.n[both]).all()


def test_smooth_iteration_lies_within_its_band():
    # при радиусе B из |z| в (B, B^2) следует n <= mu <= n + 1
    view = make_view(-0.8, 1.0, 200, aspect=1.0)
    o = compute(view, max_iter=400, bailout=256.0)
    out = ~o.inside
    assert (o.mu[out] >= o.n[out] - 1e-3).all()
    assert (o.mu[out] <= o.n[out] + 1.0 + 1e-3).all()


def test_smooth_iteration_is_smooth_away_from_the_set():
    view = make_view(0.9 + 0.9j, 0.2, 100, aspect=1.0)
    o = compute(view, max_iter=200, bailout=256.0)
    assert (~o.inside).all()
    assert np.abs(np.diff(o.mu, axis=1)).max() < 0.5
    assert np.abs(np.diff(o.mu, axis=0)).max() < 0.5


def test_julia_with_c_zero_is_unit_disk():
    view = make_view(0, 3.0, 200, aspect=1.0)
    o = compute(view, kind="julia", c=0j, max_iter=200, bailout=2.0)
    r = np.abs(view.grid())
    assert (o.inside[r < 0.95]).all()
    assert (~o.inside[r > 1.05]).all()


def test_julia_for_c_outside_mandelbrot_is_totally_disconnected_but_bounded():
    # c = 1 лежит вне множества Мандельброта: заполненное множество Жюлиа «пыль», очень мало внутренних точек
    view = make_view(0, 3.0, 300, aspect=1.0)
    o = compute(view, kind="julia", c=1 + 0j, max_iter=300, bailout=2.0)
    assert o.inside.mean() < 0.01


def test_invalid_arguments():
    view = make_view(0, 1, 10)
    with pytest.raises(ValueError):
        compute(view, kind="bad")
    with pytest.raises(ValueError):
        compute(view, bailout=1.5)


def test_escape_radius_constant():
    assert ESCAPE_RADIUS == 2.0
