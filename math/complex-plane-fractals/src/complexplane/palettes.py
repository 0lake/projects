"""Палитры: циклические градиенты по опорным цветам, косинусные палитры, обёртки matplotlib."""

from __future__ import annotations

from typing import Callable, Sequence

import numpy as np


def _hex(color: str) -> np.ndarray:
    color = color.lstrip("#")
    return np.array([int(color[i:i + 2], 16) for i in (0, 2, 4)], dtype=float) / 255.0


class Palette:
    """Цвет как функция t. Значения t берутся по модулю 1, палитра циклическая."""

    def __init__(self, lut: np.ndarray, name: str = ""):
        if lut.ndim != 2 or lut.shape[1] != 3:
            raise ValueError("lut должен иметь форму (N, 3)")
        self.lut = np.clip(lut, 0.0, 1.0)
        self.name = name

    def __call__(self, t: np.ndarray) -> np.ndarray:
        t = np.asarray(t, dtype=float)
        pos = (t % 1.0) * len(self.lut)
        i0 = np.floor(pos).astype(int) % len(self.lut)
        i1 = (i0 + 1) % len(self.lut)
        f = (pos - np.floor(pos))[..., None]
        return self.lut[i0] * (1 - f) + self.lut[i1] * f

    @classmethod
    def from_stops(cls, stops: Sequence[str], name: str = "", size: int = 2048,
                   cyclic: bool = True) -> "Palette":
        """Градиент по опорным цветам. cyclic=True замыкает последний цвет на первый."""
        pts = [_hex(s) for s in stops]
        if cyclic:
            pts.append(pts[0])
        pts_arr = np.array(pts)
        xs = np.linspace(0.0, 1.0, len(pts_arr))
        grid = np.linspace(0.0, 1.0, size, endpoint=not cyclic)
        lut = np.stack([np.interp(grid, xs, pts_arr[:, k]) for k in range(3)], axis=1)
        # сглаживаем стыки опорных точек, чтобы не было видимых «изломов»
        kernel = np.hanning(size // 64 * 2 + 1)
        kernel /= kernel.sum()
        pad = len(kernel) // 2
        smooth = np.empty_like(lut)
        for k in range(3):
            wrapped = np.concatenate([lut[-pad:, k], lut[:, k], lut[:pad, k]]) if cyclic \
                else np.concatenate([np.full(pad, lut[0, k]), lut[:, k], np.full(pad, lut[-1, k])])
            smooth[:, k] = np.convolve(wrapped, kernel, mode="valid")
        return cls(smooth, name)

    @classmethod
    def cosine(cls, a, b, c, d, name: str = "", size: int = 2048) -> "Palette":
        """Палитра a + b cos(2 pi (c t + d)) по каналам."""
        t = np.linspace(0.0, 1.0, size, endpoint=False)[:, None]
        a, b, c, d = (np.array(v, dtype=float)[None, :] for v in (a, b, c, d))
        return cls(a + b * np.cos(2 * np.pi * (c * t + d)), name)

    @classmethod
    def matplotlib(cls, cmap: str, cyclic: bool = False, size: int = 2048) -> "Palette":
        """Палитра из matplotlib. cyclic=True зеркалит её туда и обратно, чтобы не было шва."""
        from matplotlib import colormaps

        cm = colormaps[cmap]
        t = np.linspace(0.0, 1.0, size, endpoint=False)
        if cyclic:
            t = 1.0 - np.abs(2.0 * t - 1.0)
        return cls(cm(t)[:, :3], cmap)


def named() -> dict[str, Palette]:
    """Собственные палитры проекта."""
    s = Palette.from_stops
    return {
        "fire": s(["#0b0206", "#4a0d1a", "#b3261e", "#ff7a18", "#ffd166", "#fff4d6", "#ffb347", "#8f1d14"], "fire"),
        "ice": s(["#020b1a", "#0b3a6b", "#1e7fd0", "#7fd3ff", "#f2fbff", "#7fd3ff", "#1e7fd0", "#0b3a6b"], "ice"),
        "aurora": s(["#04111f", "#0b6e5f", "#2ee6a8", "#b8ffd9", "#7a5cff", "#2b1a6b", "#0b6e5f"], "aurora"),
        "sunset": s(["#10051f", "#4b1a6b", "#c13584", "#ff6a5c", "#ffb24d", "#ffe4a1", "#ff8a5c", "#8a2a6b"], "sunset"),
        "neon": s(["#05010f", "#3b0a9c", "#ff2bd6", "#25e8ff", "#d6ff3b", "#ff2bd6", "#5a1fd6"], "neon"),
        "gold": s(["#120b02", "#5c3a06", "#b8860b", "#ffd24d", "#fff6d6", "#e0a526", "#7a4d0a"], "gold"),
        "ocean": s(["#00060f", "#003a63", "#00809a", "#35d0c0", "#e8fff4", "#35d0c0", "#00809a", "#003a63"], "ocean"),
        "candy": s(["#ffd1e8", "#ff7ab8", "#b86bff", "#6b9bff", "#7affd9", "#fff59a", "#ffb07a"], "candy"),
        "ultraviolet": s(["#06010f", "#2a0a63", "#6b2bd6", "#c77dff", "#ffffff", "#c77dff", "#6b2bd6", "#2a0a63"], "ultraviolet"),
        "ember": s(["#050102", "#2b0505", "#7a0f0f", "#e0431f", "#ffc23d", "#e0431f", "#7a0f0f"], "ember"),
        "emerald": s(["#010a06", "#04452b", "#0e9f6e", "#7ae0b0", "#f1fff8", "#7ae0b0", "#0e9f6e", "#04452b"], "emerald"),
        "paper": s(["#fbf6ea", "#e8d9b5", "#b78a4a", "#5a3a1e", "#1c1208", "#5a3a1e", "#b78a4a", "#e8d9b5"], "paper"),
    }


def cosine_palettes() -> dict[str, Palette]:
    """Классические косинусные палитры (по мотивам Иниго Килеса)."""
    c = Palette.cosine
    return {
        "rainbow": c([0.5, 0.5, 0.5], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0], [0.0, 0.33, 0.67], "rainbow"),
        "magenta-teal": c([0.5, 0.5, 0.5], [0.5, 0.5, 0.5], [1.0, 1.0, 0.5], [0.8, 0.9, 0.3], "magenta-teal"),
        "warm-cool": c([0.5, 0.5, 0.5], [0.5, 0.5, 0.5], [1.0, 0.7, 0.4], [0.0, 0.15, 0.2], "warm-cool"),
        "deep-sea": c([0.2, 0.4, 0.6], [0.3, 0.3, 0.4], [1.0, 1.0, 1.0], [0.0, 0.1, 0.25], "deep-sea"),
    }


def get(name: str) -> Palette:
    """Палитра по имени: свои, косинусные или любая из matplotlib."""
    own = {**named(), **cosine_palettes()}
    if name in own:
        return own[name]
    return Palette.matplotlib(name, cyclic=True)


def to_rgb255(rgb: np.ndarray) -> np.ndarray:
    return (np.clip(rgb, 0.0, 1.0) * 255.0 + 0.5).astype(np.uint8)


PaletteFn = Callable[[np.ndarray], np.ndarray]
