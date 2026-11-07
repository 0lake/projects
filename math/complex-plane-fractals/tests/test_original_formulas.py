"""Почему исходные формулы пришлось заменить.

Эти тесты фиксируют дефекты первой версии решения. Если они вдруг начнут падать, значит,
изменилось поведение NumPy или кто-то «починил» исходные формулы, и README нужно обновить.
"""

import numpy as np

from complexplane.conformal import in_source


def original_a(z):
    z1 = (z - 1j) / (z + 1j)
    return np.sqrt((1 / z1) ** 2) * 1j


def original_b(z):
    return np.arccosh(np.sqrt(z ** 2 + 1) * 1j)


def sample(n=4000):
    rng = np.random.default_rng(2)
    z = rng.uniform(-5, 5, n) + 1j * rng.uniform(1e-2, 5, n)
    return z[in_source(z)]


def test_original_variant_a_is_two_to_one():
    # корень из квадрата стирает знак: главное значение sqrt(w^2) равно +-w,
    # поэтому z и другая точка области имеют один и тот же образ
    z = sample()
    m = (z + 1j) / (z - 1j)
    partner = 1j * (1 - m) / (-m - 1)            # прообраз точки -m
    assert (partner.imag > 0).all()
    assert np.max(np.abs(original_a(z) - original_a(partner))) < 1e-9
    assert np.min(np.abs(z - partner)) > 1e-3     # это разные точки


def test_original_variant_b_jumps_across_ray_above_i():
    # главная ветвь sqrt(z^2 + 1) имеет разрез на луче {it, t > 1}, он лежит внутри области
    eps = 1e-9
    for t in (1.5, 2.0, 3.0):
        jump = abs(original_b(eps + 1j * t) - original_b(-eps + 1j * t))
        assert abs(jump - np.pi) < 1e-6


def test_original_variant_b_inverse_does_not_invert():
    z = sample()
    w = original_b(z)
    back = np.sqrt(np.cosh(w) ** 2 - 1) * 1j
    assert not np.allclose(back, z, atol=1e-6)
