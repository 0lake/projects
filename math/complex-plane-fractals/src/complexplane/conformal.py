"""Конформные отображения областей, заданных как композиция элементарных шагов.

Исходная область F: верхняя полуплоскость без отрезка [0, i].

Цепочка шагов
    1. w = z^2           F -> C \\ [-1, +inf)      (полуплоскость раскрывается на плоскость с разрезом)
    2. w = w + 1         -> C \\ [0, +inf)
    3. w = i sqrt(-w)    -> {Im w > 0}            (главная ветвь корня непрерывна на области)
    4. w = J^{-1}(w)     -> {Im w > 0, |w| > 1}   (обратная функция Жуковского, корень с |w| > 1)
    5. w = log w         -> {0 < Im w < pi, Re w > 0}   (только для варианта B)

Вариант A заканчивается на шаге 4, вариант B продолжается шагом 5.
Каждый шаг обратим, обратные функции собраны в ConformalMap.inverse.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

Func = Callable[[np.ndarray], np.ndarray]
Mask = Callable[[np.ndarray], np.ndarray]


def joukowski_inverse(zeta: np.ndarray) -> np.ndarray:
    """Корень уравнения w + 1/w = 2 zeta с |w| >= 1.

    Функция Жуковского J(w) = (w + 1/w)/2 конформно переводит {Im w > 0, |w| > 1}
    на верхнюю полуплоскость. Обратная берёт из двух корней тот, что дальше от нуля.
    """
    zeta = np.asarray(zeta, dtype=complex)
    root = np.sqrt(zeta * zeta - 1.0)
    w1, w2 = zeta + root, zeta - root
    return np.where(np.abs(w1) >= np.abs(w2), w1, w2)


def joukowski(w: np.ndarray) -> np.ndarray:
    w = np.asarray(w, dtype=complex)
    return 0.5 * (w + 1.0 / w)


def to_upper_half_plane(w: np.ndarray) -> np.ndarray:
    """C \\ [0, +inf) -> {Im > 0}: i sqrt(-w), разрез главной ветви лежит на самом разрезе области."""
    return 1j * np.sqrt(-np.asarray(w, dtype=complex))


def from_upper_half_plane(zeta: np.ndarray) -> np.ndarray:
    """Обратное к to_upper_half_plane: zeta^2."""
    z = np.asarray(zeta, dtype=complex)
    return z * z


def sqrt_upper(w: np.ndarray) -> np.ndarray:
    """Корень с Im > 0 для w из C \\ [0, +inf): обратный к возведению в квадрат на полуплоскости."""
    return 1j * np.sqrt(-np.asarray(w, dtype=complex))


@dataclass(frozen=True)
class Stage:
    title: str                  # подпись шага (mathtext)
    forward: Func
    inverse: Func
    inside: Mask                # принадлежность точки образу после этого шага


def _all(w: np.ndarray) -> np.ndarray:
    return np.ones(np.shape(w), dtype=bool)


def _upper(w: np.ndarray) -> np.ndarray:
    return np.asarray(w).imag > 0


def _outside_unit_upper(w: np.ndarray) -> np.ndarray:
    w = np.asarray(w)
    return (w.imag > 0) & (np.abs(w) > 1)


def _half_strip(w: np.ndarray) -> np.ndarray:
    w = np.asarray(w)
    return (w.imag > 0) & (w.imag < np.pi) & (w.real > 0)


STAGES: dict[str, Stage] = {
    "square": Stage(r"$w=z^2$", lambda z: z * z, sqrt_upper, _all),
    "shift": Stage(r"$w=z+1$", lambda w: w + 1.0, lambda w: w - 1.0, _all),
    "upper": Stage(r"$w=i\sqrt{-z}$", to_upper_half_plane, from_upper_half_plane, _upper),
    "joukowski": Stage(r"$w=J^{-1}(z)$", joukowski_inverse, joukowski, _outside_unit_upper),
    "log": Stage(r"$w=\ln z$", np.log, np.exp, _half_strip),
}


@dataclass(frozen=True)
class ConformalMap:
    name: str
    source_title: str
    target_title: str
    stages: tuple[Stage, ...]
    formula: str
    inverse_formula: str

    def forward(self, z: np.ndarray, upto: int | None = None) -> np.ndarray:
        """Применяет первые upto шагов (все, если не указано)."""
        w = np.asarray(z, dtype=complex)
        for stage in self.stages[:upto]:
            w = stage.forward(w)
        return w

    def forward_from(self, w: np.ndarray, start: int) -> np.ndarray:
        """Применяет шаги, начиная с номера start (образ после start шагов -> цель)."""
        w = np.asarray(w, dtype=complex)
        for stage in self.stages[start:]:
            w = stage.forward(w)
        return w

    def inverse(self, w: np.ndarray) -> np.ndarray:
        z = np.asarray(w, dtype=complex)
        for stage in reversed(self.stages):
            z = stage.inverse(z)
        return z

    def __call__(self, z: np.ndarray) -> np.ndarray:
        return self.forward(z)

    @property
    def target_inside(self) -> Mask:
        return self.stages[-1].inside


def in_source(z: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    """Принадлежность F: Im z > 0 и точка не лежит на отрезке [0, i]."""
    z = np.asarray(z)
    on_slit = (np.abs(z.real) <= eps) & (z.imag > 0) & (z.imag <= 1.0)
    return (z.imag > 0) & ~on_slit


def exterior_half_plane() -> ConformalMap:
    """F -> {Im w > 0, |w| > 1}."""
    return ConformalMap(
        name="A",
        source_title=r"$F=\{\mathrm{Im}\,z>0\}\setminus[0,i]$",
        target_title=r"$G=\{\mathrm{Im}\,w>0,\ |w|>1\}$",
        stages=(STAGES["square"], STAGES["shift"], STAGES["upper"], STAGES["joukowski"]),
        formula=r"g(z)=J^{-1}\!\left(i\sqrt{-(z^2+1)}\right)",
        inverse_formula=r"f(w)=i\sqrt{1-\left(\frac{w+1/w}{2}\right)^2}",
    )


def half_strip() -> ConformalMap:
    """F -> {0 < Im w < pi, Re w > 0}."""
    return ConformalMap(
        name="B",
        source_title=r"$F=\{\mathrm{Im}\,z>0\}\setminus[0,i]$",
        target_title=r"$G=\{0<\mathrm{Im}\,w<\pi,\ \mathrm{Re}\,w>0\}$",
        stages=(STAGES["square"], STAGES["shift"], STAGES["upper"], STAGES["joukowski"], STAGES["log"]),
        formula=r"g(z)=\ln J^{-1}\!\left(i\sqrt{-(z^2+1)}\right)=\operatorname{arccosh}\!\left(i\sqrt{-(z^2+1)}\right)",
        inverse_formula=r"f(w)=i\sqrt{1-\cosh^2 w}",
    )
