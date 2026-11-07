"""Сетки на комплексной плоскости."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class View:
    """Прямоугольное окно просмотра: центр, ширина и размер картинки в пикселях.

    Высота окна определяется шириной и пропорциями картинки, пиксели квадратные.
    """

    center: complex
    width: float
    px_width: int
    px_height: int

    @property
    def height(self) -> float:
        return self.width * self.px_height / self.px_width

    @property
    def pixel(self) -> float:
        """Сторона пикселя в единицах комплексной плоскости."""
        return self.width / self.px_width

    @property
    def extent(self) -> tuple[float, float, float, float]:
        """(left, right, bottom, top) в формате matplotlib."""
        cx, cy = self.center.real, self.center.imag
        return (cx - self.width / 2, cx + self.width / 2,
                cy - self.height / 2, cy + self.height / 2)

    def scaled(self, factor: int) -> "View":
        """То же окно с разрешением в factor раз выше (для сглаживания)."""
        return View(self.center, self.width, self.px_width * factor, self.px_height * factor)

    def rows(self, start: int, stop: int) -> np.ndarray:
        """Комплексные координаты пикселей строк [start, stop), строка 0 сверху."""
        left, _, _, top = self.extent
        xs = left + (np.arange(self.px_width) + 0.5) * self.pixel
        ys = top - (np.arange(start, stop) + 0.5) * self.pixel
        return xs[np.newaxis, :] + 1j * ys[:, np.newaxis]

    def grid(self) -> np.ndarray:
        return self.rows(0, self.px_height)


def make_view(center: complex, width: float, px_width: int, aspect: float = 1.5) -> View:
    """Окно с заданными пропорциями ширина:высота = aspect."""
    return View(complex(center), float(width), int(px_width), int(round(px_width / aspect)))
