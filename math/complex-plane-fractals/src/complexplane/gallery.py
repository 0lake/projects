"""PDF со всеми раскрасками множества Мандельброта.

Одно и то же изображение считается один раз, затем красится десятками способов.
Каждая страница это одна раскраска, в начале обложка с оглавлением и листы-миниатюры.
"""

from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import matplotlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from . import coloring as C
from . import palettes as P
from .engine import Orbit, compute
from .grid import make_view
from .palettes import to_rgb255

Colorer = Callable[[Orbit, Orbit], np.ndarray]    # (гладкие данные, данные с радиусом 2)

CLASSIC_CMAPS = ["afmhot", "twilight", "twilight_shifted", "inferno", "magma", "plasma", "viridis",
                 "cividis", "turbo", "nipy_spectral", "jet", "hsv", "gist_earth", "ocean", "cubehelix",
                 "Spectral", "coolwarm", "gnuplot2"]
SMOOTH_PALETTES = ["fire", "ice", "aurora", "sunset", "neon", "gold", "ocean", "candy", "ultraviolet",
                   "ember", "emerald", "paper", "rainbow", "magenta-teal", "warm-cool", "deep-sea"]


@dataclass(frozen=True)
class Entry:
    group: str
    title: str
    note: str
    colorer: Colorer


def entries() -> list[Entry]:
    out: list[Entry] = []
    g1 = "Классические полосы"
    for name in CLASSIC_CMAPS:
        note = "число итераций до выхода, логарифмическая шкала, палитра matplotlib"
        if name == "afmhot":
            note += " (как в исходном задании)"
        out.append(Entry(g1, name, note, lambda sm, c2, name=name: C.classic(c2, name)))

    g2 = "Гладкая раскраска"
    for name in SMOOTH_PALETTES:
        out.append(Entry(g2, name, "нормированное число итераций без полос, циклическая палитра",
                         lambda sm, c2, name=name: C.smooth(sm, P.get(name), cycles=0.05)))

    g3 = "Алгоритмы"
    out += [
        Entry(g3, "Выравнивание гистограммы, aurora", "цвета распределены по площади равномерно",
              lambda sm, c2: C.histogram(sm, P.get("aurora"))),
        Entry(g3, "Выравнивание гистограммы, fire", "то же, другая палитра",
              lambda sm, c2: C.histogram(sm, P.get("fire"), cycles=2.0)),
        Entry(g3, "Логарифмический потенциал, twilight",
              "синус от log log |z| минус n log 2: волны вокруг множества (как во второй части задания)",
              lambda sm, c2: C.potential_bands(sm, "twilight")),
        Entry(g3, "Оценка расстояния, neon", "яркость по оценке расстояния до границы, видны тонкие нити",
              lambda sm, c2: C.distance(sm, P.get("neon"))),
        Entry(g3, "Оценка расстояния, ice", "то же в холодной палитре",
              lambda sm, c2: C.distance(sm, P.get("ice"))),
        Entry(g3, "Stripe average, sunset", "среднее значение sin от угла орбиты",
              lambda sm, c2: C.stripes(sm, P.get("sunset"))),
        Entry(g3, "Stripe average, ocean", "то же, другая палитра",
              lambda sm, c2: C.stripes(sm, P.get("ocean"), cycles=1.6)),
        Entry(g3, "Ловушка орбит, ocean", "расстояние орбиты до точки 0",
              lambda sm, c2: C.orbit_trap(sm, P.get("ocean"))),
        Entry(g3, "Ловушка орбит, fire", "та же ловушка, огненная палитра",
              lambda sm, c2: C.orbit_trap(sm, P.get("fire"), strength=1.4)),
        Entry(g3, "Бинарное разложение", "знак Im z при выходе: шахматный узор эквипотенциалей и лучей",
              lambda sm, c2: C.binary_decomposition(sm)),
        Entry(g3, "Внешний угол, rainbow", "оттенок по аргументу z при выходе",
              lambda sm, c2: C.external_angle(sm, P.get("rainbow"))),
        Entry(g3, "Внутренность по модулю орбиты", "внутри множества цвет задаёт |z| на последней итерации",
              lambda sm, c2: C.interior_decay(sm, P.get("gold"), P.get("ice"))),
        Entry(g3, "Рельеф, ultraviolet", "гладкая раскраска с боковым светом по высоте",
              lambda sm, c2: C.shade(C.smooth(sm, P.get("ultraviolet"), cycles=0.05), sm, strength=0.5)),
        Entry(g3, "Рельеф, sunset", "то же в тёплой палитре",
              lambda sm, c2: C.shade(C.smooth(sm, P.get("sunset"), cycles=0.05), sm, strength=0.5)),
    ]
    return out


def _font(bold: bool, size: int) -> ImageFont.FreeTypeFont:
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    path = Path(matplotlib.get_data_path()) / "fonts" / "ttf" / name
    return ImageFont.truetype(str(path), size)


def _jpeg(img: Image.Image, quality: int) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True, subsampling=0)
    return buf.getvalue()


def _page(image: np.ndarray, number: int, total: int, e: Entry, width: int, height: int) -> Image.Image:
    bar = int(height * 0.075)
    page = Image.new("RGB", (width, height + bar), (15, 12, 29))
    page.paste(Image.fromarray(to_rgb255(image)), (0, 0))
    d = ImageDraw.Draw(page)
    pad = int(width * 0.02)
    d.text((pad, height + bar * 0.5), e.title, font=_font(True, int(bar * 0.38)), fill=(233, 230, 255), anchor="lm")
    tw = d.textlength(e.title, font=_font(True, int(bar * 0.38)))
    d.text((pad + tw + pad, height + bar * 0.5), e.note, font=_font(False, int(bar * 0.26)),
           fill=(154, 149, 200), anchor="lm")
    d.text((width - pad, height + bar * 0.5), f"{number} / {total}", font=_font(False, int(bar * 0.3)),
           fill=(154, 149, 200), anchor="rm")
    return page


def _cover(width: int, height: int, groups: list[tuple[str, int, int]], total: int) -> Image.Image:
    img = Image.new("RGB", (width, height), (15, 12, 29))
    yy, xx = np.mgrid[0:height, 0:width]
    glow = np.exp(-(((xx - width * 0.8) / (width * 0.45)) ** 2 + ((yy - height * 0.25) / (height * 0.5)) ** 2))
    arr = np.asarray(img).astype(float)
    arr += glow[..., None] * np.array([70, 40, 120])
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    pad = int(width * 0.07)
    d.text((pad, int(height * 0.2)), "Множество Мандельброта", font=_font(True, int(height * 0.075)), fill=(233, 230, 255))
    d.text((pad, int(height * 0.31)), f"{total} раскрасок одного и того же изображения",
           font=_font(False, int(height * 0.034)), fill=(95, 240, 193))
    y = int(height * 0.48)
    for title, first, last in groups:
        d.text((pad, y), title, font=_font(True, int(height * 0.032)), fill=(233, 230, 255))
        d.text((width - pad, y), f"стр. {first}–{last}", font=_font(False, int(height * 0.03)),
               fill=(154, 149, 200), anchor="ra")
        y += int(height * 0.085)
    d.text((pad, height - pad), "z → z² + c,  z₀ = 0,  |z| > 2 означает уход на бесконечность",
           font=_font(False, int(height * 0.026)), fill=(154, 149, 200), anchor="ld")
    return img


def _sheet(thumbs: list[tuple[Image.Image, str]], title: str, width: int, height: int, cols: int = 4) -> Image.Image:
    img = Image.new("RGB", (width, height), (15, 12, 29))
    d = ImageDraw.Draw(img)
    pad = int(width * 0.03)
    d.text((pad, pad * 0.9), title, font=_font(True, int(height * 0.03)), fill=(233, 230, 255))
    rows = (len(thumbs) + cols - 1) // cols
    top = int(pad * 2.4)
    gap = int(pad * 0.45)
    tw = (width - 2 * pad - gap * (cols - 1)) // cols
    th = int(tw * 2 / 3)
    label_h = int(th * 0.2)
    for i, (im, label) in enumerate(thumbs):
        r, c = divmod(i, cols)
        x = pad + c * (tw + gap)
        y = top + r * (th + label_h + gap * 0.6)
        img.paste(im.resize((tw, th), Image.LANCZOS), (x, int(y)))
        d.text((x, int(y) + th + label_h * 0.5), label, font=_font(False, int(label_h * 0.5)),
               fill=(154, 149, 200), anchor="lm")
    return img


def build(out_pdf: str | Path, scale: float = 1.0, quality: int = 86) -> Path:
    """Считает данные, красит всеми способами и собирает PDF."""
    try:
        import img2pdf
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("для PDF нужен пакет img2pdf: pip install img2pdf") from exc

    width, height = max(int(1500 * scale), 150), max(int(1000 * scale), 100)
    ss = 2 if scale >= 0.5 else 1
    view = make_view(-0.6, 3.1, width, aspect=width / height).scaled(ss)
    iters = max(int(1500 * min(1.0, 0.3 + scale)), 60)
    smooth_orbit = compute(view, max_iter=iters, bailout=256.0)
    classic_orbit = compute(view, max_iter=iters, bailout=2.0)

    items = entries()
    total = len(items)
    pages: list[Image.Image] = []
    thumbs: dict[str, list[tuple[Image.Image, str]]] = {}
    for i, e in enumerate(items, start=1):
        rgb = C.downsample(e.colorer(smooth_orbit, classic_orbit), ss)
        page = _page(rgb, i, total, e, width, height)
        pages.append(page)
        thumbs.setdefault(e.group, []).append((page.crop((0, 0, width, height)), e.title))

    groups: list[tuple[str, int, int]] = []
    sheets: list[Image.Image] = []
    n_front = 1 + len(thumbs)
    cursor = n_front + 1
    for title, items_g in thumbs.items():
        groups.append((title, cursor, cursor + len(items_g) - 1))
        cursor += len(items_g)
        sheets.append(_sheet(items_g, f"{title}: миниатюры", width, height + int(height * 0.075)))

    front = [_cover(width, height + int(height * 0.075), groups, total)] + sheets
    all_pages = front + pages
    out_pdf = Path(out_pdf)
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    layout = img2pdf.get_layout_fun((img2pdf.in_to_pt(10.0), img2pdf.in_to_pt(10.0 * all_pages[0].height / width)))
    out_pdf.write_bytes(img2pdf.convert([_jpeg(p, quality) for p in all_pages], layout_fun=layout,
                                        title="Множество Мандельброта: раскраски"))
    return out_pdf
