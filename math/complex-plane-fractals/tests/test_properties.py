"""Свойства множества Мандельброта из задания проверяются численно."""

import numpy as np
import pytest

from complexplane.engine import compute, escapes
from complexplane.grid import make_view

RNG = np.random.default_rng(7)


def orbit(c: complex, n: int, cap: float = 1e6) -> np.ndarray:
    """Первые n членов орбиты нуля; после выхода за cap останавливаемся, чтобы не получить inf."""
    z, out = 0j, []
    for _ in range(n):
        z = z * z + c
        out.append(z)
        if abs(z) > cap:
            break
    return np.array(out)


def test_property_1_orbits_of_conjugate_are_conjugate():
    for _ in range(200):
        c = complex(RNG.uniform(-2, 1), RNG.uniform(-1.2, 1.2))
        a, b = orbit(c, 25), orbit(np.conj(c), 25)
        assert len(a) == len(b)
        assert np.allclose(a.conj(), b, rtol=1e-12, atol=1e-12)


def test_property_1_set_is_symmetric_about_real_axis():
    view = make_view(-0.6, 3.0, 300, aspect=1.5)
    # окно симметрично относительно вещественной оси, значит сетка тоже
    o = compute(view, max_iter=300, bailout=2.0)
    assert (o.inside == o.inside[::-1]).all()


def test_property_2_points_with_modulus_above_two_escape():
    for _ in range(300):
        r = RNG.uniform(2.0001, 6.0)
        c = r * np.exp(1j * RNG.uniform(0, 2 * np.pi))
        assert escapes(c, max_iter=50)


def test_property_2_lower_bound_of_orbit():
    # |z_n| >= |c| (|c| - 1)^(n - 1) при |c| > 2, как в доказательстве
    for _ in range(100):
        r = RNG.uniform(2.01, 3.0)
        c = r * np.exp(1j * RNG.uniform(0, 2 * np.pi))
        z = orbit(c, 5)
        n = np.arange(1, 6)
        assert (np.abs(z) >= abs(c) * (abs(c) - 1) ** (n - 1) * (1 - 1e-12)).all()


def test_whole_set_lies_in_disk_of_radius_two():
    view = make_view(0, 6.0, 240, aspect=1.0)
    o = compute(view, max_iter=200, bailout=2.0)
    r = np.abs(view.grid())
    assert not o.inside[r > 2.0 + view.pixel].any()


def test_boundary_point_minus_two_is_in_set():
    assert not escapes(-2 + 0j, max_iter=2000)


@pytest.mark.parametrize("c", [-0.75 + 0.1j, 0.3 + 0.5j, -1.3 + 0j])
def test_once_modulus_exceeds_two_orbit_escapes(c):
    # лемма: если |z_n| > 2 и |c| <= 2, то орбита уходит на бесконечность
    z = 0j
    for _ in range(1000):
        z = z * z + c
        if abs(z) > 2:
            for _ in range(60):
                z = z * z + c
                if abs(z) > 1e100:
                    break
            assert abs(z) > 1e10
            return
