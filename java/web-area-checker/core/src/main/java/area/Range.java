package area;

/**
 * Замкнутый числовой отрезок.
 *
 * @param min нижняя граница, включительно
 * @param max верхняя граница, включительно
 */
public record Range(double min, double max) {
    public Range {
        if (!(min <= max)) {
            throw new IllegalArgumentException("min > max: " + min + " > " + max);
        }
    }

    /** @return true, если значение конечно и лежит в отрезке */
    public boolean contains(double value) {
        return Double.isFinite(value) && value >= min && value <= max;
    }
}
