import numpy as np

from complexplane.grid import make_view
from complexplane.newton import newton_basins, unit_roots


def test_unit_roots_satisfy_equation():
    for n in (2, 3, 5, 8):
        assert np.allclose(unit_roots(n) ** n, 1)


def test_starting_exactly_at_a_root_is_converged():
    roots = unit_roots(4)
    view = make_view(roots[1], 1e-3, 3, aspect=1.0)    # центральный пиксель совпадает с корнем
    b = newton_basins(view, roots)
    assert b.root[1, 1] == 1 and b.steps[1, 1] == 0


def test_points_near_roots_converge_to_them():
    roots = unit_roots(3)
    view = make_view(0, 4.0, 5, aspect=1.0)
    b = newton_basins(view, roots)
    for k, r in enumerate(roots):
        v = make_view(r, 1e-3, 3, aspect=1.0)
        assert (newton_basins(v, roots).root == k).all()
    assert b.roots.shape == (3,)


def test_three_basins_have_equal_area():
    view = make_view(0, 3.4, 300, aspect=1.0)
    b = newton_basins(view, unit_roots(3), max_iter=80)
    shares = [(b.root == k).mean() for k in range(3)]
    assert max(shares) - min(shares) < 0.02
    assert sum(shares) > 0.98


def test_basins_are_symmetric_about_real_axis():
    view = make_view(0, 3.4, 201, aspect=1.0)
    b = newton_basins(view, unit_roots(3), max_iter=80)
    # корень 0 (z=1) лежит на оси, корни 1 и 2 сопряжены и меняются местами
    flipped = b.root[::-1]
    swap = np.where(flipped == 1, 2, np.where(flipped == 2, 1, flipped))
    assert (b.root == swap).mean() > 0.999


def test_polynomial_with_attracting_cycle_has_unconverged_points():
    roots = np.roots([1, 0, -2, 2])
    # у z^3 - 2z + 2 есть притягивающий цикл {0, 1}: из его бассейна метод не сходится ни к одному корню
    view = make_view(0.5, 1.2, 300, aspect=1.0)
    b = newton_basins(view, roots, max_iter=80)
    assert (b.root == -1).mean() > 0.015
