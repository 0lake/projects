"""Итерации z -> z^2 + c для множеств Мандельброта и Жюлиа.

Вычисление идёт блоками строк с «уплотнением» активных точек: пиксели, которые уже
ушли на бесконечность, из расчёта исключаются. Для множества Мандельброта точки главной
кардиоиды и большой луковицы периода 2 отбрасываются аналитически, не итерируясь.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .grid import View

ESCAPE_RADIUS = 2.0


@dataclass
class Orbit:
    """Результат итераций для всех пикселей картинки (сверху вниз, слева направо)."""

    inside: np.ndarray        # bool: точка не ушла за max_iter итераций
    n: np.ndarray             # int32: номер итерации выхода (для внутренних max_iter)
    mu: np.ndarray            # float32: гладкое число итераций
    modulus: np.ndarray       # float32: |z| в момент выхода
    angle: np.ndarray         # float32: arg z в момент выхода
    distance: np.ndarray      # float32: оценка расстояния до множества (в пикселях)
    stripe: np.ndarray        # float32: среднее «полосатое» значение (stripe average)
    trap: np.ndarray          # float32: минимум расстояния орбиты до ловушки
    final_mod: np.ndarray     # float32: |z| последней итерации у внутренних точек
    max_iter: int = 0
    view: View | None = field(default=None, repr=False)


def mandelbrot_interior(c: np.ndarray) -> np.ndarray:
    """True для точек главной кардиоиды и луковицы периода 2 (заведомо в множестве)."""
    x, y = c.real, c.imag
    q = (x - 0.25) ** 2 + y ** 2
    cardioid = q * (q + (x - 0.25)) <= 0.25 * y ** 2
    bulb = (x + 1.0) ** 2 + y ** 2 <= 0.0625
    return cardioid | bulb


def _iterate_block(z0: np.ndarray, c: np.ndarray, max_iter: int, bailout: float,
                   julia: bool, stripe_freq: float, trap_point: complex) -> dict[str, np.ndarray]:
    shape = z0.shape
    size = z0.size
    n_out = np.full(size, max_iter, dtype=np.int32)
    mu = np.zeros(size, dtype=np.float32)
    modulus = np.zeros(size, dtype=np.float32)
    angle = np.zeros(size, dtype=np.float32)
    dist = np.zeros(size, dtype=np.float32)
    stripe = np.zeros(size, dtype=np.float32)
    trap = np.full(size, np.inf, dtype=np.float32)
    final_mod = np.zeros(size, dtype=np.float32)
    inside = np.ones(size, dtype=bool)

    z = z0.ravel().astype(np.complex128)
    cc = np.broadcast_to(c, shape).ravel().astype(np.complex128)
    idx = np.arange(size)

    if not julia:
        skip = mandelbrot_interior(cc)
        keep = ~skip
        idx, z, cc = idx[keep], z[keep], cc[keep]
        final_mod[skip] = 0.0

    dz = np.ones_like(z) if julia else np.zeros_like(z)
    s_sum = np.zeros(idx.size)
    t_min = np.full(idx.size, np.inf)
    log_b = np.log(bailout)
    last_z = z.copy()

    for i in range(max_iter):
        if idx.size == 0:
            break
        # производная нужна до обновления z: dz' = 2 z dz (+1 для Мандельброта)
        dz = 2.0 * z * dz + (0.0 if julia else 1.0)
        z = z * z + cc
        a = np.abs(z)
        if i > 0:
            s_sum += 0.5 + 0.5 * np.sin(stripe_freq * np.angle(z))
        t_min = np.minimum(t_min, np.abs(z - trap_point))
        out = a > bailout
        if out.any():
            k = idx[out]
            zz, aa = z[out], a[out]
            n_out[k] = i
            inside[k] = False
            modulus[k] = aa
            angle[k] = np.angle(zz)
            mu[k] = i + 1.0 - np.log(np.log(aa)) / np.log(2.0) + np.log(log_b) / np.log(2.0)
            dist[k] = aa * np.log(aa) / np.maximum(np.abs(dz[out]), 1e-300)
            cnt = max(i, 1)
            prev = s_sum[out] - (0.5 + 0.5 * np.sin(stripe_freq * np.angle(zz)))
            last = (prev / max(cnt - 1, 1)) if cnt > 1 else prev
            cur = s_sum[out] / cnt
            frac = 1.0 + np.log(log_b) / np.log(2.0) - np.log(np.log(aa)) / np.log(2.0)
            frac = np.clip(frac, 0.0, 1.0)
            stripe[k] = frac * cur + (1.0 - frac) * last
            trap[k] = t_min[out]
            keep = ~out
            idx, z, cc, dz = idx[keep], z[keep], cc[keep], dz[keep]
            s_sum, t_min = s_sum[keep], t_min[keep]
        last_z = z
    if idx.size:
        final_mod[idx] = np.abs(last_z) if last_z.size == idx.size else 0.0
        trap[idx] = t_min
    return dict(inside=inside, n=n_out, mu=mu, modulus=modulus, angle=angle,
                distance=dist, stripe=stripe, trap=trap, final_mod=final_mod)


def compute(view: View, *, kind: str = "mandelbrot", c: complex = 0j, max_iter: int = 500,
            bailout: float = 256.0, stripe_freq: float = 5.0, trap_point: complex = 0j,
            block_rows: int = 128) -> Orbit:
    """Считает орбиты для всей картинки.

    kind="mandelbrot": z0 = 0, параметр c берётся из пикселя.
    kind="julia": z0 берётся из пикселя, параметр c задан.
    bailout: радиус «ухода на бесконечность». Для гладкой раскраски нужен большой
    (по умолчанию 256), для классических полос хватает 2. Радиус 2 корректен, см. README.
    """
    if kind not in ("mandelbrot", "julia"):
        raise ValueError("kind должен быть 'mandelbrot' или 'julia'")
    if bailout < ESCAPE_RADIUS:
        raise ValueError("bailout не может быть меньше 2")
    julia = kind == "julia"
    parts: list[dict[str, np.ndarray]] = []
    for start in range(0, view.px_height, block_rows):
        stop = min(start + block_rows, view.px_height)
        grid = view.rows(start, stop)
        if julia:
            parts.append(_iterate_block(grid, np.complex128(c), max_iter, bailout, True,
                                        stripe_freq, trap_point))
        else:
            parts.append(_iterate_block(np.zeros_like(grid), grid, max_iter, bailout, False,
                                        stripe_freq, trap_point))
    cat = {k: np.concatenate([p[k] for p in parts]).reshape(view.px_height, view.px_width)
           for k in parts[0]}
    cat["distance"] = cat["distance"] / np.float32(view.pixel)
    return Orbit(max_iter=max_iter, view=view, **cat)


def escapes(c: complex, max_iter: int = 1000) -> bool:
    """Ушла ли орбита нуля для одного значения c (точная проверка радиусом 2)."""
    z = 0j
    for _ in range(max_iter):
        z = z * z + c
        if abs(z) > ESCAPE_RADIUS:
            return True
    return False
