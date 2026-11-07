"""Бассейны Ньютона: к какому корню сходится метод Ньютона из каждой точки плоскости."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .grid import View


@dataclass
class Basins:
    root: np.ndarray        # int8: номер корня, -1 если сходимости нет
    steps: np.ndarray       # int32: число шагов до сходимости
    closeness: np.ndarray   # float32: гладкая поправка в долях шага, 0..1
    roots: np.ndarray


def unit_roots(n: int) -> np.ndarray:
    """Корни уравнения z^n = 1."""
    return np.exp(2j * np.pi * np.arange(n) / n)


def newton_basins(view: View, roots: np.ndarray | None = None, max_iter: int = 60,
                  tol: float = 1e-8, block_rows: int = 128) -> Basins:
    """Метод Ньютона для многочлена с заданными корнями.

    f(z) = prod (z - r_k), поэтому f/f' = 1 / sum 1/(z - r_k) и шаг считается без
    раскрытия многочлена: так нет переполнений и потери точности для больших |z|.
    """
    roots = unit_roots(3) if roots is None else np.asarray(roots, dtype=complex)
    out_root = np.full((view.px_height, view.px_width), -1, dtype=np.int8)
    out_steps = np.full((view.px_height, view.px_width), max_iter, dtype=np.int32)
    out_close = np.zeros((view.px_height, view.px_width), dtype=np.float32)
    for start in range(0, view.px_height, block_rows):
        stop = min(start + block_rows, view.px_height)
        z = view.rows(start, stop).copy()
        shape = z.shape
        zf = z.ravel()
        idx = np.arange(zf.size)
        r_blk = np.full(zf.size, -1, dtype=np.int8)
        s_blk = np.full(zf.size, max_iter, dtype=np.int32)
        c_blk = np.zeros(zf.size, dtype=np.float32)
        # точка, совпадающая с корнем, уже сошлась (шаг Ньютона там делил бы на ноль)
        d0 = np.abs(zf[:, None] - roots[None, :])
        at_root = d0.min(axis=1) < tol
        if at_root.any():
            r_blk[at_root] = d0.argmin(axis=1)[at_root]
            s_blk[at_root] = 0
            c_blk[at_root] = 1.0
            idx, zf = idx[~at_root], zf[~at_root]
        for i in range(max_iter):
            if idx.size == 0:
                break
            with np.errstate(divide="ignore", invalid="ignore"):
                inv_sum = np.sum(1.0 / (zf[:, None] - roots[None, :]), axis=1)
                zf = zf - 1.0 / inv_sum
            d = np.abs(zf[:, None] - roots[None, :])
            near = d.argmin(axis=1)
            dmin = d[np.arange(d.shape[0]), near]
            done = dmin < tol
            if done.any():
                k = idx[done]
                r_blk[k] = near[done]
                s_blk[k] = i
                c_blk[k] = np.clip(np.log(tol / np.maximum(dmin[done], 1e-300)) / np.log(tol) * -1.0, 0.0, 1.0)
                keep = ~done
                idx, zf = idx[keep], zf[keep]
        out_root[start:stop] = r_blk.reshape(shape)
        out_steps[start:stop] = s_blk.reshape(shape)
        out_close[start:stop] = c_blk.reshape(shape)
    return Basins(out_root, out_steps, out_close, roots)
