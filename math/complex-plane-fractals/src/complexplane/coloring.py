"""Алгоритмы раскраски: что именно красить и как превратить число в цвет."""

from __future__ import annotations

import numpy as np
from matplotlib import colormaps

from .engine import Orbit
from .palettes import Palette

BLACK = np.zeros(3)


def _paint(orbit: Orbit, colors: np.ndarray, interior: np.ndarray | None = None) -> np.ndarray:
    out = colors.copy()
    out[orbit.inside] = BLACK if interior is None else interior[orbit.inside]
    return out


def classic(orbit: Orbit, cmap: str = "afmhot") -> np.ndarray:
    """Классика: цвет по целому числу итераций на логарифмической шкале (полосы)."""
    cm = colormaps[cmap]
    v = np.log(orbit.n + 1.0)
    v = (v - v[~orbit.inside].min()) / max(np.ptp(v[~orbit.inside]), 1e-9) if (~orbit.inside).any() else v
    return _paint(orbit, cm(np.clip(v, 0, 1))[..., :3])


def smooth(orbit: Orbit, palette: Palette, cycles: float = 0.045, offset: float = 0.0,
           log_scale: bool = True) -> np.ndarray:
    """Непрерывная раскраска по нормированному числу итераций: без полос."""
    mu = orbit.mu.astype(float)
    t = np.log(np.maximum(mu, 1.0) + 1.0) * (cycles * 22.0) if log_scale else mu * cycles
    return _paint(orbit, palette(t + offset))


def histogram(orbit: Orbit, palette: Palette, cycles: float = 1.0) -> np.ndarray:
    """Выравнивание гистограммы: цвета распределены по площади равномерно."""
    out = ~orbit.inside
    colors = np.zeros(orbit.mu.shape + (3,))
    if out.any():
        vals = orbit.mu[out].astype(float)
        order = np.sort(vals)
        rank = np.searchsorted(order, vals) / max(len(order) - 1, 1)
        colors[out] = palette(rank * cycles)
    return _paint(orbit, colors)


def potential_bands(orbit: Orbit, cmap: str = "twilight", frequency: float = 0.05) -> np.ndarray:
    """Раскраска логарифмическим потенциалом с волнами: синус от log log |z| - n log 2."""
    cm = colormaps[cmap]
    v = np.log(np.maximum(np.log(np.maximum(orbit.modulus, 1.0001)), 1e-9)) - orbit.n * np.log(2.0)
    t = 0.5 + 0.5 * np.sin(v / frequency * 0.25)
    inner = np.broadcast_to(cm(0.5)[:3], orbit.mu.shape + (3,))
    return _paint(orbit, cm(t)[..., :3], np.asarray(inner))


def distance(orbit: Orbit, palette: Palette, glow: float = 0.28, scale: float = 1.0) -> np.ndarray:
    """Оценка расстояния до границы: тонкие нити границы становятся видимыми."""
    d = np.clip(orbit.distance.astype(float) * scale, 0.0, None)
    t = np.clip(d ** glow / 6.0, 0.0, 1.0)
    colors = palette(t * 0.5)
    colors = colors * (0.15 + 0.85 * t[..., None])
    return _paint(orbit, colors)


def stripes(orbit: Orbit, palette: Palette, cycles: float = 1.0) -> np.ndarray:
    """Stripe average: окраска по среднему значению sin от угла орбиты."""
    return _paint(orbit, palette(orbit.stripe.astype(float) * cycles))


def orbit_trap(orbit: Orbit, palette: Palette, strength: float = 2.2) -> np.ndarray:
    """Ловушка орбит: цвет задаёт минимальное расстояние орбиты до заданной точки."""
    t = np.clip(orbit.trap.astype(float), 0, 4)
    t = 1.0 - np.exp(-strength * t)
    return _paint(orbit, palette(t))


def binary_decomposition(orbit: Orbit, light: str = "#f3efe6", dark: str = "#14101e") -> np.ndarray:
    """Бинарное разложение: знак Im z в момент выхода, шахматный рисунок эквипотенциалей."""
    lo = np.array([int(dark[i:i + 2], 16) for i in (1, 3, 5)]) / 255.0
    hi = np.array([int(light[i:i + 2], 16) for i in (1, 3, 5)]) / 255.0
    pick = (orbit.angle > 0) ^ (orbit.n % 2 == 0)
    colors = np.where(pick[..., None], hi, lo)
    return _paint(orbit, colors, np.broadcast_to(lo, colors.shape))


def external_angle(orbit: Orbit, palette: Palette, shades: bool = True) -> np.ndarray:
    """Оттенок по аргументу z в момент выхода (внешний угол), яркость по уровню."""
    t = (orbit.angle.astype(float) / (2 * np.pi)) % 1.0
    colors = palette(t)
    if shades:
        level = 0.55 + 0.45 * np.cos(orbit.mu.astype(float) * 1.6)
        colors = colors * level[..., None]
    return _paint(orbit, colors)


def interior_decay(orbit: Orbit, palette: Palette, interior_palette: Palette,
                   cycles: float = 0.045) -> np.ndarray:
    """Раскрашивает и внешность (гладко), и внутренность по модулю орбиты на последней итерации."""
    outer = smooth(orbit, palette, cycles)
    t = np.clip(orbit.final_mod.astype(float), 0, 2) / 2.0
    inner = interior_palette(t * 0.5 + 0.1)
    out = outer.copy()
    out[orbit.inside] = inner[orbit.inside] * (0.45 + 0.55 * t[orbit.inside, None])
    return out


def _blur(a: np.ndarray, passes: int = 2) -> np.ndarray:
    k = np.array([1, 4, 6, 4, 1], dtype=float) / 16.0
    out = a
    for _ in range(passes):
        for axis in (0, 1):
            pad = [(0, 0), (0, 0)]
            pad[axis] = (2, 2)
            p = np.pad(out, pad, mode="edge")
            out = sum(k[i] * np.take(p, range(i, i + out.shape[axis]), axis=axis) for i in range(5))
    return out


def shade(rgb: np.ndarray, orbit: Orbit, strength: float = 0.55, azimuth: float = 135.0,
          elevation: float = 38.0, height_scale: float = 6.0) -> np.ndarray:
    """Рельефное освещение: поверхность задана гладким числом итераций, свет сбоку."""
    h = np.log(np.maximum(orbit.mu.astype(float), 1.0) + 1.0) * height_scale
    h[orbit.inside] = np.nanmax(h[~orbit.inside]) if (~orbit.inside).any() else 0.0
    h = _blur(h, 1)
    gy, gx = np.gradient(h)
    nx, ny, nz = -gx, gy, np.ones_like(h)
    norm = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2)
    az, el = np.radians(azimuth), np.radians(elevation)
    lx, ly, lz = np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)
    lam = np.clip((nx * lx + ny * ly + nz * lz) / norm, 0.0, 1.0)
    lam = lam / max(np.sin(el), 1e-6)
    lit = (1.0 - strength) + strength * np.clip(lam, 0.0, 1.4)
    out = rgb * lit[..., None]
    out[orbit.inside] = rgb[orbit.inside]
    return np.clip(out, 0.0, 1.0)


def downsample(rgb: np.ndarray, factor: int) -> np.ndarray:
    """Усреднение блоков factor x factor (сглаживание краёв)."""
    if factor == 1:
        return rgb
    h, w, c = rgb.shape
    h2, w2 = h // factor * factor, w // factor * factor
    return rgb[:h2, :w2].reshape(h2 // factor, factor, w2 // factor, factor, c).mean(axis=(1, 3))


def _inside_depth(inside: np.ndarray, factor: int = 6, max_steps: int = 400) -> np.ndarray:
    """Расстояние до границы внутри множества в пикселях: счётчик шагов эрозии маски в малом масштабе
    (шаги чередуют крест и квадрат, это даёт почти евклидову метрику), затем размытие."""
    h, w = inside.shape
    h2, w2 = h // factor, w // factor
    m = inside[: h2 * factor, : w2 * factor].reshape(h2, factor, w2, factor).mean(axis=(1, 3)) > 0.5
    dist = np.zeros(m.shape)
    cur = m.copy()
    for step in range(max_steps):
        if not cur.any():
            break
        dist += cur
        p = np.pad(cur, 1, mode="edge")   # край кадра не считается границей множества
        er = cur & p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:]
        if step % 2:
            er &= p[:-2, :-2] & p[:-2, 2:] & p[2:, :-2] & p[2:, 2:]
        cur = er
    dist = _blur(dist, 2) * factor
    big = np.repeat(np.repeat(dist, factor, axis=0), factor, axis=1)
    big = np.pad(big, ((0, h - big.shape[0]), (0, w - big.shape[1])), mode="edge")
    return _blur(big, 2)


def radiance(orbit: Orbit, palette: Palette, interior_palette: Palette, *, cycles: float = 0.11,
             rim: tuple[float, float, float] = (1.0, 0.93, 0.78), rim_width: float = 5.0,
             halo: float = 0.55, relief: float = 0.5, ring_step: float = 0.0145) -> np.ndarray:
    """Витрина: гладкая внешность с рельефом, светящаяся кромка по оценке расстояния,
    ореол вокруг множества и внутренность в виде светящихся изолиний вместо чёрной заливки."""
    out = shade(smooth(orbit, palette, cycles), orbit, strength=relief)
    pix = max(orbit.view.pixel, 1e-12)
    d = np.where(orbit.inside, 0.0, orbit.distance.astype(float)) / pix
    ext = ~orbit.inside
    rim_c = np.asarray(rim)
    core = np.exp(-d / rim_width)
    wide = np.exp(-d / (rim_width * 14.0))
    glow = (core[..., None] * rim_c * 0.9 + wide[..., None] * palette(np.zeros(d.shape) + 0.35) * halo)
    out = np.where(ext[..., None], 1.0 - (1.0 - out) * (1.0 - np.clip(glow, 0, 1)), out)
    width = orbit.view.width
    depth = _inside_depth(orbit.inside) * orbit.view.pixel / width   # расстояние в долях ширины окна
    t = 1.0 - np.exp(-depth / 0.07)
    iso = 0.5 + 0.5 * np.cos(2 * np.pi * depth / ring_step)
    iso = iso ** 3
    inner = interior_palette(0.05 + 0.8 * t + 0.12 * iso)
    inner = inner * (0.45 + 0.55 * iso[..., None]) * (0.5 + 0.5 * t[..., None])
    edge = np.exp(-depth / (orbit.view.pixel * 3.0))
    inner = 1.0 - (1.0 - inner) * (1.0 - edge[..., None] * rim_c * 0.7)
    out = np.where(orbit.inside[..., None], inner, out)
    return np.clip(out, 0.0, 1.0)
