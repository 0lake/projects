package area;

/**
 * Область на плоскости, размер которой задаёт параметр R, и допустимые диапазоны координат точки.
 */
public interface Region {
    /** @return короткое имя области для интерфейса и логов */
    String name();

    /** @return допустимые значения X */
    Range xRange();

    /** @return допустимые значения Y */
    Range yRange();

    /**
     * Проверка попадания. Граница входит в область.
     *
     * @param x координата точки
     * @param y координата точки
     * @param r параметр размера области
     * @return true, если точка внутри области или на её границе
     */
    boolean contains(double x, double y, double r);
}
