"""Иллюстрации проекта. Каждая функция сохраняет один файл и возвращает путь.

Параметр scale задаёт разрешение: 1.0 для публикации, 0.15 для быстрых проверок.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import hsv_to_rgb  # noqa: E402

from . import coloring as C  # noqa: E402
from . import palettes as P  # noqa: E402
from .conformal import ConformalMap, exterior_half_plane, half_strip, in_source  # noqa: E402
from .engine import compute, escapes  # noqa: E402
from .grid import View, make_view  # noqa: E402
from .newton import newton_basins, unit_roots  # noqa: E402
from .render import mosaic, render, save  # noqa: E402

BG = "#0f0c1d"
FG = "#e9e6ff"
MUTED = "#9a95c8"

TASK_C = -0.5251993 + 0.5251993j   # параметр, для которого Жюлиа особенно красиво


def _px(base: int, scale: float, minimum: int = 48) -> int:
    return max(int(base * scale), minimum)


def _iters(base: int, scale: float) -> int:
    return max(int(base * min(1.0, 0.35 + scale)), 40)


# ---------------------------------------------------------------- Мандельброт

def hero(out: Path, scale: float = 1.0) -> Path:
    view = make_view(-0.55, 3.1, _px(1800, scale), aspect=1.5)
    rgb = render(view, lambda o: C.shade(C.smooth(o, P.get("sunset"), cycles=0.05), o, strength=0.5),
                 max_iter=_iters(1500, scale), supersample=2 if scale >= 0.5 else 1)
    return save(rgb, out / "mandelbrot-hero.jpg")


ZOOMS = [
    ("Долина морских коньков", -0.7436447860 + 0.1318252536j, 0.0035, 2500, "ice"),
    ("Слоновья долина", 0.2859 + 0.0127j, 0.006, 2500, "gold"),
    ("Двойная спираль", -0.7615740 - 0.0847596j, 0.0006, 3500, "neon"),
    ("Мини-копия на оси", -1.7549 + 0.0j, 0.080, 1500, "aurora"),
    ("Спирали у перешейка", -0.7453 + 0.1127j, 0.010, 2500, "fire"),
    ("Тонкая нить", -1.2272 + 0.1652j, 0.0065, 3000, "ultraviolet"),
]


def zooms(out: Path, scale: float = 1.0) -> Path:
    tiles = []
    for _, centre, width, iters, pal in ZOOMS:
        view = make_view(centre, width, _px(900, scale), aspect=1.5)
        tiles.append(render(view, lambda o, pal=pal: C.shade(C.smooth(o, P.get(pal), cycles=0.07, log_scale=True), o, strength=0.45),
                            max_iter=_iters(iters, scale), supersample=2 if scale >= 0.5 else 1))
    return save(mosaic(tiles, cols=2), out / "mandelbrot-zooms.jpg")


def iterations(out: Path, scale: float = 1.0) -> Path:
    """Как число итераций меняет картинку: Мандельброт у границы и Жюлиа."""
    counts = [24, 256, 1200]
    tiles = []
    mview = make_view(-0.7436447860 + 0.1318252536j, 0.02, _px(700, scale), aspect=1.0)
    jview = make_view(0, 3.0, _px(700, scale), aspect=1.0)
    for it in counts:
        tiles.append(render(mview, lambda o: C.classic(o, "twilight_shifted"), max_iter=_iters(it, 1.0),
                            bailout=2.0, supersample=1))
    for it in counts:
        tiles.append(render(jview, lambda o: C.classic(o, "twilight_shifted"), kind="julia", c=TASK_C,
                            max_iter=_iters(it, 1.0), bailout=2.0, supersample=1))
    return save(mosaic(tiles, cols=3), out / "iterations.jpg")


# ------------------------------------------------------------------ Жюлиа

JULIA = [
    (TASK_C, "ice", "сильно закрученный"),
    (-0.8 + 0.156j, "neon", ""),
    (-0.123 + 0.745j, "sunset", "кролик Дуади"),
    (0.285 + 0.01j, "gold", ""),
    (-0.70176 - 0.3842j, "aurora", ""),
    (-0.835 - 0.2321j, "fire", ""),
    (1j, "ultraviolet", "дендрит"),
    (-0.4 + 0.6j, "ocean", ""),
    (-0.75 + 0.11j, "emerald", ""),
]


def julia_gallery(out: Path, scale: float = 1.0) -> Path:
    tiles = []
    for c, pal, _ in JULIA:
        view = make_view(0, 3.0, _px(720, scale), aspect=1.0)
        tiles.append(render(view, lambda o, pal=pal: C.shade(C.smooth(o, P.get(pal), cycles=0.06), o, strength=0.4),
                            kind="julia", c=c, max_iter=_iters(900, scale), supersample=2 if scale >= 0.5 else 1))
    return save(mosaic(tiles, cols=3), out / "julia-gallery.jpg")


# ----------------------------------------------------------------- Ньютон

def newton_figure(out: Path, scale: float = 1.0) -> Path:
    cases = [
        (unit_roots(3), 1.7, "z^3 - 1"),
        (unit_roots(5), 1.6, "z^5 - 1"),
        (np.roots([1, 0, -2, 2]), 2.4, "z^3 - 2z + 2"),
    ]
    base = np.array([[1.00, 0.30, 0.45], [0.20, 0.85, 0.95], [1.00, 0.82, 0.25],
                     [0.68, 0.45, 1.00], [0.30, 0.95, 0.55]])
    tiles = []
    for roots, half, _ in cases:
        view = make_view(0, 2 * half, _px(900, scale), aspect=1.0)
        b = newton_basins(view.scaled(2 if scale >= 0.5 else 1), roots=roots, max_iter=60)
        shade = 0.30 + 0.70 * np.exp(-b.steps / 6.5)
        img = np.where((b.root >= 0)[..., None], base[np.clip(b.root, 0, 4)] * shade[..., None],
                       np.array([0.07, 0.06, 0.12]))
        tiles.append(C.downsample(img, 2 if scale >= 0.5 else 1))
    return save(mosaic(tiles, cols=3), out / "newton-basins.jpg")


# ----------------------------------------------------- свойства множества

def properties(out: Path, scale: float = 1.0) -> Path:
    fig = plt.figure(figsize=(15, 4.9), facecolor=BG)
    gs = fig.add_gridspec(1, 3, wspace=0.18, left=0.04, right=0.985, top=0.86, bottom=0.12)

    def style(ax, title):
        ax.set_facecolor(BG)
        ax.set_title(title, color=FG, fontsize=13, pad=10)
        ax.tick_params(colors=MUTED, labelsize=9)
        for s in ax.spines.values():
            s.set_color("#2b2748")

    # (a) симметрия
    ax = fig.add_subplot(gs[0])
    view = make_view(-0.6, 3.1, _px(1200, scale), aspect=1.5)
    rgb = render(view, lambda o: C.shade(C.smooth(o, P.get("ultraviolet"), cycles=0.05), o, strength=0.45),
                 max_iter=_iters(600, scale), supersample=1)
    ax.imshow(rgb, extent=view.extent, aspect="equal")
    c = -0.12 + 0.74j
    for cc, col in ((c, "#5ff0c1"), (np.conj(c), "#ffd166")):
        z, pts = 0j, [0j]
        for _ in range(14):
            z = z * z + cc
            pts.append(z)
        pts = np.array(pts)
        ax.plot(pts.real, pts.imag, "-", color=col, lw=1.0, alpha=0.8)
        ax.plot(pts.real, pts.imag, "o", color=col, ms=3.2)
        ax.plot([cc.real], [cc.imag], "o", color=col, ms=8, mec="white", mew=1.2)
    ax.axhline(0, color="white", lw=0.8, ls=(0, (4, 4)), alpha=0.7)
    ax.text(c.real - 0.2, c.imag + 0.06, r"$c$", color="#5ff0c1", fontsize=15)
    ax.text(c.real - 0.2, -c.imag - 0.2, r"$\bar c$", color="#ffd166", fontsize=15)
    ax.set_xlim(view.extent[0], view.extent[1])
    ax.set_ylim(view.extent[2], view.extent[3])
    style(ax, r"Орбиты $c$ и $\bar c$ зеркальны")

    # (b) область |c| <= 2
    ax = fig.add_subplot(gs[1])
    view2 = make_view(0, 6.0, _px(1000, scale), aspect=1.0)
    orbit = compute(view2, max_iter=_iters(300, scale), bailout=2.0)
    v = np.log(orbit.n + 1.0)
    v = v / v.max()
    img = np.where(orbit.inside[..., None], np.array([0.96, 0.93, 0.88]),
                   P.Palette.matplotlib("magma")(np.clip(v * 0.92, 0, 0.999))[..., :3])
    ax.imshow(img, extent=view2.extent, aspect="equal")
    th = np.linspace(0, 2 * np.pi, 400)
    ax.plot(2 * np.cos(th), 2 * np.sin(th), color="#5ff0c1", lw=1.8)
    ax.text(1.55, 1.75, r"$|c|=2$", color="#5ff0c1", fontsize=13)
    ax.plot([-2], [0], "o", color="white", ms=6)
    ax.text(-2.9, 0.3, r"$c=-2$", color="white", fontsize=11)
    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 3)
    style(ax, r"Множество целиком внутри круга $|c|\leq 2$")

    # (c) геометрический рост
    ax = fig.add_subplot(gs[2])
    for cval, col in ((2.05, "#5ff0c1"), (2.4, "#ffd166"), (3.0, "#ff6a8b")):
        z, mods = 0.0, [abs(cval)]
        z = cval
        for _ in range(5):
            z = z * z + cval
            mods.append(abs(z))
        n = np.arange(1, len(mods) + 1)
        ax.semilogy(n, mods, "o-", color=col, lw=1.8, ms=5, label=rf"$|z_n|$, $c={cval}$")
        ax.semilogy(n, cval * (cval - 1) ** (n - 1), "--", color=col, lw=1.0, alpha=0.8)
    ax.semilogy([], [], "--", color=MUTED, label=r"оценка $|c|(|c|-1)^{n-1}$")
    ax.set_xlabel("n", color=MUTED)
    ax.grid(color="#2b2748", lw=0.6)
    leg = ax.legend(facecolor=BG, edgecolor="#2b2748", labelcolor=FG, fontsize=9, loc="upper left")
    leg.get_frame().set_alpha(0.9)
    style(ax, r"Рост орбиты при $|c|>2$")
    return _save_fig(fig, out / "properties.png")


def _save_fig(fig, path: Path, dpi: int = 150) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=dpi, facecolor=fig.get_facecolor())
    plt.close(fig)
    return path


# ------------------------------------------------------- конформные карты

def _line(d: np.ndarray, width: float) -> np.ndarray:
    """Мягкая линия: 1 на самой линии, 0 далеко. d: расстояние до ближайшей линии (в долях периода)."""
    return np.exp(-(d / width) ** 2)


def _texture_polar(w: np.ndarray) -> np.ndarray:
    th = np.angle(w)
    lr = np.log(np.maximum(np.abs(w), 1e-9))
    hue = (0.58 + 0.42 * th / np.pi) % 1.0
    val = 0.55 + 0.38 * (0.5 + 0.5 * np.cos(2 * np.pi * lr * 2.4))
    hsv = np.stack([hue, np.full_like(hue, 0.62), val], axis=-1)
    rgb = hsv_to_rgb(np.clip(hsv, 0, 1))
    g1 = np.abs((th / (np.pi / 12)) % 1.0 - 0.5) * 2    # 1 в центре клетки, 0 на линии
    g2 = np.abs((lr / 0.3) % 1.0 - 0.5) * 2
    lines = np.maximum(_line(1 - g1, 0.035), _line(1 - g2, 0.05))
    return rgb * (1 - 0.7 * lines[..., None]) + 0.0


def _texture_strip(w: np.ndarray) -> np.ndarray:
    u, v = w.real, w.imag
    hue = (0.58 + 0.42 * np.clip(v, 0, np.pi) / np.pi) % 1.0
    val = 0.55 + 0.38 * (0.5 + 0.5 * np.cos(2 * np.pi * u * 1.6))
    hsv = np.stack([hue, np.full_like(hue, 0.62), val], axis=-1)
    rgb = hsv_to_rgb(np.clip(hsv, 0, 1))
    g1 = np.abs((v / (np.pi / 12)) % 1.0 - 0.5) * 2
    g2 = np.abs((u / 0.3) % 1.0 - 0.5) * 2
    lines = np.maximum(_line(1 - g1, 0.035), _line(1 - g2, 0.05))
    return rgb * (1 - 0.7 * lines[..., None])


EXTENTS_A = [(-3.2, 3.2, -0.45, 3.35), (-6.0, 6.0, -4.5, 4.5), (-5.0, 7.0, -4.5, 4.5),
             (-4.0, 4.0, -0.5, 3.5), (-4.0, 4.0, -0.5, 3.5)]
EXTENTS_B = EXTENTS_A + [(-0.35, 3.2, -0.3, 3.45)]
TITLES = ["$F$", r"$z\mapsto z^2$", r"$w\mapsto w+1$", r"$w\mapsto i\sqrt{-w}$",
          r"$\zeta\mapsto J^{-1}(\zeta)$", r"$w\mapsto\ln w$"]
BOUNDARY_COLORS = ["#4ad8ff", "#ff9f43", "#ff5fa2", "#7dff8a"]


def _boundary(extent_left: float = 6.0) -> list[np.ndarray]:
    eps = 1e-7
    xs = np.concatenate([np.linspace(-extent_left * 6, -1e-3, 1500), np.linspace(1e-3, extent_left * 6, 1500)])
    left = xs[xs < 0] + 1j * eps
    right = xs[xs > 0] + 1j * eps
    # концы разреза пропускаем: на самой вещественной оси знак нулевой мнимой части выбирает ветвь корня
    t = np.linspace(1e-6, 1.0 - 1e-6, 400)
    return [left, right, -eps + 1j * t, eps + 1j * t]


def conformal_figure(cmap: ConformalMap, out: Path, scale: float = 1.0) -> Path:
    n_stage = len(cmap.stages)
    extents = EXTENTS_A if n_stage == 4 else EXTENTS_B
    texture = _texture_polar if n_stage == 4 else _texture_strip
    titles = TITLES[:n_stage + 1]
    fig, axes = plt.subplots(2, 3, figsize=(15, 9.6), facecolor=BG)
    boundary = _boundary()
    for k, ax in enumerate(axes.ravel()):
        if k > n_stage:
            ax.axis("off")
            continue
        x0, x1, y0, y1 = extents[k]
        w = _px(1000, scale)
        h = int(w * (y1 - y0) / (x1 - x0))
        xs = np.linspace(x0, x1, w)
        ys = np.linspace(y1, y0, h)
        grid = xs[None, :] + 1j * ys[:, None]
        mask = in_source(grid) if k == 0 else cmap.stages[k - 1].inside(grid)
        with np.errstate(all="ignore"):
            target = cmap.forward_from(grid, k)
        img = np.zeros(grid.shape + (4,))
        img[..., :3] = texture(np.where(mask, target, 1 + 1j))
        img[..., 3] = mask.astype(float)
        bg = np.array([0.12, 0.10, 0.21, 1.0])
        img = img * img[..., 3:4] + bg * (1 - img[..., 3:4])
        ax.imshow(np.clip(img, 0, 1), extent=(x0, x1, y0, y1), aspect="equal", interpolation="bilinear")
        ax.axhline(0, color="#3a3566", lw=0.8)
        ax.axvline(0, color="#3a3566", lw=0.8)
        for pts, col in zip(boundary, BOUNDARY_COLORS):
            with np.errstate(all="ignore"):
                img_pts = cmap.forward(pts, upto=k)
            if k == 0:
                img_pts = pts
            ax.plot(img_pts.real, img_pts.imag, color=col, lw=2.2, solid_capstyle="round")
        ax.set_xlim(x0, x1)
        ax.set_ylim(y0, y1)
        ax.set_facecolor(BG)
        ax.tick_params(colors=MUTED, labelsize=9)
        for s in ax.spines.values():
            s.set_color("#2b2748")
        label = (f"{k}.  " if k else "") + titles[k]
        if k == n_stage:
            label = f"{k}.  {titles[k]}  =  $G$" if k else titles[k]
        ax.set_title(label, color=FG, fontsize=14, pad=9)
    fig.suptitle(f"{cmap.source_title}  $\\longrightarrow$  {cmap.target_title}", color=FG, fontsize=17, y=0.995)
    fig.text(0.5, 0.012, f"${cmap.formula}$        ${cmap.inverse_formula}$", color=MUTED, ha="center", fontsize=12.5)
    fig.subplots_adjust(left=0.035, right=0.99, top=0.9, bottom=0.075, wspace=0.12, hspace=0.26)
    return _save_fig(fig, out / f"conformal-{cmap.name.lower()}.png", dpi=130)


def conformal_a(out: Path, scale: float = 1.0) -> Path:
    return conformal_figure(exterior_half_plane(), out, scale)


def conformal_b(out: Path, scale: float = 1.0) -> Path:
    return conformal_figure(half_strip(), out, scale)


ALL = {
    "hero": hero,
    "zooms": zooms,
    "iterations": iterations,
    "julia": julia_gallery,
    "newton": newton_figure,
    "properties": properties,
    "conformal-a": conformal_a,
    "conformal-b": conformal_b,
}


def build(names: list[str] | None, out: Path, scale: float = 1.0) -> list[Path]:
    """Строит выбранные иллюстрации (все, если names пуст)."""
    selected = names or list(ALL)
    unknown = [n for n in selected if n not in ALL]
    if unknown:
        raise KeyError(f"неизвестные иллюстрации: {', '.join(unknown)}; доступны: {', '.join(ALL)}")
    return [ALL[n](out, scale) for n in selected]
