"""Командная строка: отдельные картинки, все иллюстрации проекта и PDF с раскрасками."""

from __future__ import annotations

from pathlib import Path

import click
import numpy as np

from . import coloring as C
from . import palettes as P
from .grid import make_view
from .newton import newton_basins, unit_roots
from .render import render, save

MODES = ["smooth", "classic", "histogram", "distance", "stripes", "trap", "shaded", "binary"]


def _complex(ctx, param, value: str) -> complex:  # noqa: ANN001
    try:
        return complex(value.replace(" ", "").replace("i", "j"))
    except ValueError as exc:
        raise click.BadParameter(f"не комплексное число: {value}") from exc


def _colorer(mode: str, palette: str):
    pal = P.get(palette)
    return {
        "smooth": lambda o: C.smooth(o, pal),
        "classic": lambda o: C.classic(o, palette),
        "histogram": lambda o: C.histogram(o, pal),
        "distance": lambda o: C.distance(o, pal),
        "stripes": lambda o: C.stripes(o, pal),
        "trap": lambda o: C.orbit_trap(o, pal),
        "shaded": lambda o: C.shade(C.smooth(o, pal), o),
        "binary": lambda o: C.binary_decomposition(o),
    }[mode]


common = [
    click.option("--center", default="-0.6+0j", callback=_complex, show_default=True,
                 help="центр окна, например -0.7436+0.1318j"),
    click.option("--width", default=3.1, show_default=True, type=float, help="ширина окна"),
    click.option("--size", default=1200, show_default=True, type=int, help="ширина картинки в пикселях"),
    click.option("--iters", default=800, show_default=True, type=int, help="максимум итераций"),
    click.option("--palette", default="sunset", show_default=True, help="имя палитры проекта или matplotlib"),
    click.option("--mode", default="smooth", type=click.Choice(MODES), show_default=True, help="способ раскраски"),
    click.option("--out", default="out/image.jpg", show_default=True, type=click.Path(path_type=Path)),
]


def add_common(f):
    for opt in reversed(common):
        f = opt(f)
    return f


@click.group()
def cli() -> None:
    """Фракталы и конформные отображения на комплексной плоскости."""


@cli.command()
@add_common
def mandelbrot(center, width, size, iters, palette, mode, out) -> None:
    """Множество Мандельброта (любая область, любая раскраска)."""
    view = make_view(center, width, size)
    save(render(view, _colorer(mode, palette), max_iter=iters, bailout=2.0 if mode == "classic" else 256.0), out)
    click.echo(f"сохранено: {out}")


@cli.command()
@click.option("--c", "c", default="-0.5251993+0.5251993j", callback=_complex, show_default=True,
              help="параметр c")
@add_common
def julia(c, center, width, size, iters, palette, mode, out) -> None:
    """Заполненное множество Жюлиа для заданного c."""
    center = center if center != -0.6 + 0j else 0j
    width = width if width != 3.1 else 3.0
    view = make_view(center, width, size, aspect=1.0)
    save(render(view, _colorer(mode, palette), kind="julia", c=c, max_iter=iters,
                bailout=2.0 if mode == "classic" else 256.0), out)
    click.echo(f"сохранено: {out}")


@cli.command()
@click.option("--degree", default=3, show_default=True, type=click.IntRange(2, 12), help="уравнение z^n = 1")
@click.option("--size", default=1000, show_default=True, type=int)
@click.option("--half-width", default=1.7, show_default=True, type=float)
@click.option("--iters", default=60, show_default=True, type=int)
@click.option("--out", default="out/newton.jpg", show_default=True, type=click.Path(path_type=Path))
def newton(degree, size, half_width, iters, out) -> None:
    """Бассейны Ньютона для z^n - 1."""
    view = make_view(0, 2 * half_width, size, aspect=1.0)
    b = newton_basins(view, unit_roots(degree), max_iter=iters)
    hues = P.Palette.matplotlib("turbo")((np.arange(degree) + 0.5) / degree * 0.95)[:, :3]
    shade = 0.30 + 0.70 * np.exp(-b.steps / 6.5)
    img = np.where((b.root >= 0)[..., None], hues[np.clip(b.root, 0, degree - 1)] * shade[..., None], 0.05)
    save(img, out)
    click.echo(f"сохранено: {out}")


@cli.command()
@click.argument("variant", type=click.Choice(["a", "b"]))
@click.option("--out", default="out", show_default=True, type=click.Path(path_type=Path))
def conformal(variant, out) -> None:
    """Иллюстрация конформного отображения по шагам: вариант a (круг) или b (полуполоса)."""
    from . import figures

    path = figures.ALL[f"conformal-{variant}"](out, 1.0)
    click.echo(f"сохранено: {path}")


@cli.command()
@click.argument("names", nargs=-1)
@click.option("--out", default="assets", show_default=True, type=click.Path(path_type=Path))
@click.option("--scale", default=1.0, show_default=True, type=float, help="разрешение: 1 для публикации")
def figures(names, out, scale) -> None:
    """Все иллюстрации проекта (или выбранные по именам)."""
    from . import figures as fig

    for path in fig.build(list(names), out, scale):
        click.echo(f"сохранено: {path}")


@cli.command()
@click.option("--out", default="docs/mandelbrot-colorings.pdf", show_default=True, type=click.Path(path_type=Path))
@click.option("--scale", default=1.0, show_default=True, type=float)
def gallery(out, scale) -> None:
    """PDF со всеми раскрасками множества Мандельброта."""
    from . import gallery as gal

    click.echo(f"сохранено: {gal.build(out, scale)}")
