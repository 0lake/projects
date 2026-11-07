"""Сборка картинок: вычисление, раскраска, сглаживание, сохранение."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

import numpy as np
from PIL import Image

from . import coloring
from .engine import Orbit, compute
from .grid import View, make_view
from .palettes import to_rgb255

Colorer = Callable[[Orbit], np.ndarray]


def render(view: View, colorer: Colorer, *, kind: str = "mandelbrot", c: complex = 0j,
           max_iter: int = 500, bailout: float = 256.0, supersample: int = 2,
           trap_point: complex = 0j, stripe_freq: float = 5.0) -> np.ndarray:
    """Возвращает RGB float (H, W, 3). Считает в supersample раз крупнее и усредняет."""
    big = view.scaled(supersample)
    orbit = compute(big, kind=kind, c=c, max_iter=max_iter, bailout=bailout,
                    trap_point=trap_point, stripe_freq=stripe_freq)
    return coloring.downsample(colorer(orbit), supersample)


def save(rgb: np.ndarray, path: str | Path, quality: int = 92) -> Path:
    """Сохраняет RGB float как PNG или JPEG по расширению."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.fromarray(to_rgb255(rgb))
    if path.suffix.lower() in (".jpg", ".jpeg"):
        img.save(path, quality=quality, optimize=True, subsampling=0)
    else:
        img.save(path, optimize=True)
    return path


def mosaic(tiles: list[np.ndarray], cols: int, gap: int = 6, background: float = 0.05) -> np.ndarray:
    """Склеивает плитки одинакового размера в сетку."""
    h, w, _ = tiles[0].shape
    rows = (len(tiles) + cols - 1) // cols
    out = np.full((rows * h + (rows - 1) * gap, cols * w + (cols - 1) * gap, 3), background)
    for i, t in enumerate(tiles):
        r, cc = divmod(i, cols)
        out[r * (h + gap): r * (h + gap) + h, cc * (w + gap): cc * (w + gap) + w] = t
    return out


__all__ = ["render", "save", "mosaic", "make_view"]
