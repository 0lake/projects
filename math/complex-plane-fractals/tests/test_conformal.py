import numpy as np
import pytest

from complexplane.conformal import (exterior_half_plane, half_strip, in_source, joukowski,
                                    joukowski_inverse)

RNG = np.random.default_rng(3)


def sample_source(n: int = 60000) -> np.ndarray:
    z = RNG.uniform(-8, 8, n) + 1j * RNG.uniform(1e-3, 8, n)
    return z[in_source(z)]


@pytest.fixture(scope="module", params=["a", "b"])
def cmap(request):
    return exterior_half_plane() if request.param == "a" else half_strip()


def test_image_lies_in_target(cmap):
    w = cmap(sample_source())
    assert np.isfinite(w).all()
    assert cmap.target_inside(w).all()


def test_inverse_recovers_point(cmap):
    z = sample_source()
    assert np.max(np.abs(cmap.inverse(cmap(z)) - z)) < 1e-9


def test_forward_recovers_target_point(cmap):
    # точки цели берём образами, чтобы быть уверенными, что они в области
    z = sample_source(20000)
    w = cmap(z)
    assert np.max(np.abs(cmap(cmap.inverse(w)) - w)) < 1e-9


def test_map_is_injective_on_sample(cmap):
    z = sample_source(5000)
    w = cmap(z)
    key = np.round(w.real * 1e8) + 1j * np.round(w.imag * 1e8)
    assert len(np.unique(key)) == len(key)


def test_real_axis_goes_to_boundary_rays():
    m = exterior_half_plane()
    x = np.concatenate([np.linspace(-9, -0.05, 200), np.linspace(0.05, 9, 200)])
    w = m(x + 1e-9j)
    assert np.allclose(w.imag, 0, atol=1e-6)
    assert (np.abs(w.real) > 1 - 1e-6).all()
    # знак сохраняется: левая полуось уходит влево, правая вправо
    assert (w.real[x < 0] < 0).all() and (w.real[x > 0] > 0).all()


def test_slit_sides_go_to_unit_semicircle():
    m = exterior_half_plane()
    t = np.linspace(0.02, 0.98, 100)
    left, right = m(-1e-9 + 1j * t), m(1e-9 + 1j * t)
    for w in (left, right):
        assert np.allclose(np.abs(w), 1, atol=1e-6)
        assert (w.imag > 0).all()
    assert (left.real < 0).all() and (right.real > 0).all()


def test_half_strip_boundary():
    m = half_strip()
    t = np.linspace(0.02, 0.98, 100)
    left, right = m(-1e-9 + 1j * t), m(1e-9 + 1j * t)
    for w in (left, right):
        assert np.allclose(w.real, 0, atol=1e-6)
        assert ((w.imag > -1e-6) & (w.imag < np.pi + 1e-6)).all()
    x = np.linspace(0.05, 9, 100)
    assert np.allclose(m(x + 1e-9j).imag, 0, atol=1e-6)          # правая ось в нижнюю сторону
    assert np.allclose(m(-x + 1e-9j).imag, np.pi, atol=1e-6)      # левая ось в верхнюю сторону


def test_arccosh_form_of_variant_b():
    m = half_strip()
    z = sample_source(5000)
    zeta = m.forward(z, upto=3)
    assert np.allclose(np.cosh(m(z)), zeta, atol=1e-9)


def test_joukowski_pair():
    zeta = RNG.uniform(-4, 4, 5000) + 1j * RNG.uniform(1e-3, 4, 5000)
    w = joukowski_inverse(zeta)
    assert (np.abs(w) >= 1 - 1e-12).all() and (w.imag > 0).all()
    assert np.allclose(joukowski(w), zeta, atol=1e-9)


def test_conformality_derivative_is_finite_and_nonzero():
    m = exterior_half_plane()
    z = sample_source(2000)
    h = 1e-6
    d = (m(z + h) - m(z - h)) / (2 * h)
    assert (np.abs(d) > 0).all() and np.isfinite(d).all()
    # конформность: образ малого круга остаётся кругом, отношение осей близко к 1
    e = 1e-5
    a = m(z + e) - m(z)
    b = m(z + 1j * e) - m(z)
    assert np.allclose(np.abs(a), np.abs(b), rtol=1e-2)
