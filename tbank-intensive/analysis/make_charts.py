"""Иллюстрации для README: перерисованные графики сравнения сегментов Т-Премиум и остальных.

Значения получены в R-анализе (hypothesis_check_tpremium.R) и записаны ниже,
чтобы картинки собирались без закрытых учебных датасетов.
Запуск: python make_charts.py [папка_вывода]
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager as fm
from matplotlib.patches import FancyBboxPatch, Wedge, Circle

YELLOW, GREY, WHITE, MUTED = "#FFDD2D", "#3b3b46", "#f5f5f7", "#9a9aa6"
BG0, BG1 = "#06060a", "#101320"

for f in fm.findSystemFonts():
    if "/inter/" in f.lower():
        fm.fontManager.addfont(f)
plt.rcParams["font.family"] = ["Inter", "DejaVu Sans"]

DATA = {
    "share": {"premium": 36, "others": 64},
    "check": {"premium": 18993, "others": 12811},
    "orders": {"premium": 7.53, "others": 4.38},
    "price": {  # доли поездок по диапазонам стоимости, %
        "labels": ["До 10 тыс.", "10-30 тыс.", "30 тыс. и выше"],
        "others": [56.2, 36.7, 7.1],
        "premium": [48.5, 36.7, 14.8],
    },
}
SOURCE = "Учебный датасет «Авиа» и «Путешествия», НИУ ВШЭ и Т-Банк"
S = 8  # масштаб: холст 8 x 8 дюймов, 200 dpi = 1600 px


def canvas(title, subtitle):
    fig = plt.figure(figsize=(S, S), dpi=200)
    bg = fig.add_axes([0, 0, 1, 1]); bg.axis("off")
    yy, xx = np.mgrid[0:1:400j, 0:1:400j]
    c0, c1 = np.array(matplotlib.colors.to_rgb(BG0)), np.array(matplotlib.colors.to_rgb(BG1))
    img = c0 + (c1 - c0) * (yy[..., None])
    for cx, cy, r, col, a in ((0.08, 0.92, 0.55, (0.10, 0.45, 0.42), 0.50), (0.95, 0.08, 0.6, (0.22, 0.18, 0.62), 0.55),
                              (0.55, 0.5, 0.45, (0.30, 0.28, 0.05), 0.12)):
        d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / r
        img = img + (np.array(col) - img) * (a * np.clip(1 - d, 0, 1) ** 2)[..., None]
    bg.imshow(np.clip(img[::-1], 0, 1), extent=[0, 1, 0, 1], aspect="auto", zorder=0)
    bg.set_xlim(0, 1); bg.set_ylim(0, 1)
    bg.add_patch(FancyBboxPatch((0.012, 0.012), 0.976, 0.976, boxstyle="round,pad=0,rounding_size=0.035",
                                fc="none", ec=(1, 1, 1, 0.10), lw=1.4, transform=bg.transAxes))
    bg.add_patch(plt.Rectangle((0.07, 0.915), 0.045, 0.008, fc=YELLOW, ec="none"))
    bg.text(0.07, 0.875, title, color=WHITE, fontsize=25, fontweight="bold", va="center")
    bg.text(0.07, 0.832, subtitle, color=MUTED, fontsize=14.5, va="center")
    bg.text(0.07, 0.05, SOURCE, color=(1, 1, 1, 0.38), fontsize=10.5, va="center")
    return fig, bg


def pill(ax, x, y, text, fs=16):
    ax.text(x, y, text, color="#17150a", fontsize=fs, fontweight="bold", ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.45,rounding_size=0.9", fc=YELLOW, ec="none"), transform=ax.transAxes)


def rbar(ax, x, w, h, color, glow=False, r=0.012):
    if glow:
        for k, a in ((0.020, 0.05), (0.013, 0.07), (0.007, 0.10)):
            ax.add_patch(FancyBboxPatch((x - k, 0 - k), w + 2 * k, h + 2 * k, boxstyle=f"round,pad=0,rounding_size={r + k}",
                                        fc=color, ec="none", alpha=a, zorder=2))
    ax.add_patch(FancyBboxPatch((x, 0), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=color, ec="none", zorder=3))


def plot_axes(fig, left=0.10, bottom=0.16, width=0.80, height=0.58):
    ax = fig.add_axes([left, bottom, width, height]); ax.axis("off")
    return ax


def two_bars(path, title, subtitle, vals, fmt, badge):
    fig, bg = canvas(title, subtitle)
    ax = plot_axes(fig)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1.18)
    top = max(vals)
    xs, w = (0.06, 0.60), 0.32
    for x, v, c, name in zip(xs, vals, (GREY, YELLOW), ("Другие", "Т-Премиум")):
        h = v / top
        rbar(ax, x, w, h, c, glow=c == YELLOW)
        ax.text(x + w / 2, h + 0.04, fmt(v), ha="center", va="bottom", color=WHITE if c == GREY else YELLOW,
                fontsize=30, fontweight="bold")
        ax.text(x + w / 2, -0.08, name, ha="center", va="top", color=MUTED, fontsize=16)
    ax.plot([0, 1], [0, 0], color=(1, 1, 1, .18), lw=1.2, zorder=1)
    ax.plot([xs[0] + w, xs[1]], [vals[0] / top] * 2, color=(1, 1, 1, .35), lw=1.4, ls=(0, (3, 4)), zorder=2)
    ax.plot([xs[1] + w / 2, xs[1] + w / 2], [vals[0] / top, vals[1] / top], color=(1, 1, 1, 0), lw=0)
    pill(ax, 0.49, vals[0] / top + 0.09, badge, fs=17)
    fig.savefig(path, facecolor=BG0)
    plt.close(fig)


def donut(path):
    p = DATA["share"]["premium"]
    fig, bg = canvas("Т-Премиум: каждый третий", "Распределение пользователей «Т-Путешествий» по сегментам")
    ax = fig.add_axes([0.14, 0.12, 0.72, 0.62]); ax.set_aspect("equal"); ax.axis("off")
    ax.set_xlim(-1.25, 1.25); ax.set_ylim(-1.25, 1.25)
    start = 90
    for k, a in ((0.10, 0.05), (0.06, 0.08), (0.03, 0.12)):
        ax.add_patch(Wedge((0, 0), 1 + k, start - 360 * p / 100, start, width=0.34 + 2 * k, fc=YELLOW, ec="none", alpha=a))
    ax.add_patch(Wedge((0, 0), 1, start - 360 * p / 100, start, width=0.34, fc=YELLOW, ec="none"))
    ax.add_patch(Wedge((0, 0), 1, start, start + 360 * (100 - p) / 100, width=0.34, fc=GREY, ec="none"))
    for ang in (start, start - 360 * p / 100):
        a = np.deg2rad(ang)
        ax.add_patch(Circle((0.83 * np.cos(a), 0.83 * np.sin(a)), 0.17, fc=YELLOW if ang == start else YELLOW, ec="none", alpha=0))
    ax.text(0, 0.12, f"{p}%", ha="center", va="center", color=YELLOW, fontsize=64, fontweight="bold")
    ax.text(0, -0.28, "Т-Премиум", ha="center", va="center", color=WHITE, fontsize=17)
    ax.add_patch(FancyBboxPatch((-1.18, -1.2), 0.16, 0.09, boxstyle="round,pad=0,rounding_size=0.03", fc=GREY, ec="none"))
    ax.text(-0.95, -1.155, f"Другие  {100 - p}%", ha="left", va="center", color=WHITE, fontsize=15)
    ax.add_patch(FancyBboxPatch((0.20, -1.2), 0.16, 0.09, boxstyle="round,pad=0,rounding_size=0.03", fc=YELLOW, ec="none"))
    ax.text(0.43, -1.155, f"Т-Премиум  {p}%", ha="left", va="center", color=WHITE, fontsize=15)
    fig.savefig(path, facecolor=BG0)
    plt.close(fig)


def grouped(path):
    d = DATA["price"]
    fig, bg = canvas("Дорогие поездки: вдвое чаще", "Доля поездок по стоимости у Т-Премиум и остальных, %")
    ax = plot_axes(fig)
    ax.set_xlim(0, 3); ax.set_ylim(0, 66 * 1.12)
    w = 0.34
    for i, lab in enumerate(d["labels"]):
        x0 = i + 0.5 - w - 0.02
        for x, v, c in ((x0, d["others"][i], GREY), (x0 + w + 0.04, d["premium"][i], YELLOW)):
            rbar(ax, x, w, v, c, glow=c == YELLOW and i == 2, r=0.05)
            ax.text(x + w / 2, v + 1.4, f"{v:g}".replace(".", ",") + "%", ha="center", va="bottom",
                    color=WHITE if c == GREY else YELLOW, fontsize=17, fontweight="bold")
        ax.text(i + 0.5, -4.2, lab, ha="center", va="top", color=MUTED, fontsize=15)
    ax.plot([0, 3], [0, 0], color=(1, 1, 1, .18), lw=1.2)
    pill(ax, 0.835, 0.34, "x2,1", fs=17)
    ax.add_patch(FancyBboxPatch((0.0, 53), 0.02, 0.02, fc="none", ec="none"))
    # легенда
    for j, (c, t) in enumerate(((GREY, "Другие"), (YELLOW, "Т-Премиум"))):
        ax.add_patch(FancyBboxPatch((0.02 + j * 0.62, 66 * 1.12 - 6.4), 0.1, 3.4, boxstyle="round,pad=0,rounding_size=0.04", fc=c, ec="none"))
        ax.text(0.16 + j * 0.62, 66 * 1.12 - 4.7, t, color=WHITE, fontsize=15, va="center")
    fig.savefig(path, facecolor=BG0)
    plt.close(fig)


def main(out):
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    donut(out / "01-audience-share.png")
    c = DATA["check"]
    two_bars(out / "02-average-check.png", "Чек Т-Премиум выше на 48%", "Средняя стоимость заказа, ₽",
             [c["others"], c["premium"]], lambda v: f"{v:,.0f}".replace(",", " "), "+48%")
    grouped(out / "03-price-structure.png")
    o = DATA["orders"]
    two_bars(out / "04-repeat-orders.png", "Т-Премиум возвращаются чаще", "Среднее число заказов на пользователя",
             [o["others"], o["premium"]], lambda v: f"{v:.2f}".replace(".", ","), "x1,7")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "../assets/charts")
