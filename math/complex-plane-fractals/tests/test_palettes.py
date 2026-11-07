import numpy as np
import pytest

from complexplane import palettes as P


def test_palette_is_cyclic_and_in_range():
    pal = P.get("sunset")
    t = np.linspace(-3, 3, 1000)
    rgb = pal(t)
    assert rgb.shape == (1000, 3)
    assert rgb.min() >= 0 and rgb.max() <= 1
    assert np.allclose(pal(np.array([0.0])), pal(np.array([1.0])))
    assert np.allclose(pal(np.array([0.37])), pal(np.array([2.37])))


def test_palette_has_no_jump_at_seam():
    pal = P.get("fire")
    a, b = pal(np.array([0.9999])), pal(np.array([0.0001]))
    assert np.abs(a - b).max() < 0.02


def test_all_named_palettes_construct():
    for name in {**P.named(), **P.cosine_palettes()}:
        assert P.get(name).lut.shape[1] == 3


def test_matplotlib_fallback_and_unknown():
    assert P.get("viridis").name == "viridis"
    with pytest.raises(KeyError):
        P.get("no-such-palette-name")


def test_cosine_palette_formula():
    pal = P.Palette.cosine([0.5] * 3, [0.5] * 3, [1.0] * 3, [0.0, 0.33, 0.67], size=1024)
    assert np.allclose(pal(np.array([0.0]))[0], [1.0, 0.5 + 0.5 * np.cos(2 * np.pi * 0.33), 0.5 + 0.5 * np.cos(2 * np.pi * 0.67)], atol=2e-3)


def test_radiance_inside_depth_ignores_frame_edge():
    import numpy as np
    from complexplane.coloring import _inside_depth
    inside = np.ones((60, 90), dtype=bool)
    depth = _inside_depth(inside)
    # множество заполняет весь кадр: границы нет, глубина не должна падать к краям
    assert depth[0, 0] > 0.5 * depth[30, 45]
