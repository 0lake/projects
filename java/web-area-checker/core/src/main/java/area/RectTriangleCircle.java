package area;

/**
 * Область для версии на JSF:
 * <ul>
 *   <li>вторая четверть: прямоугольник от -R/2 до 0 по X и от 0 до R по Y;</li>
 *   <li>четвёртая четверть: треугольник с вершинами (0, 0), (R, 0), (0, -R/2);</li>
 *   <li>первая четверть: четверть круга радиуса R/2.</li>
 * </ul>
 * Третья четверть в область не входит.
 */
public final class RectTriangleCircle implements Region {
    @Override
    public String name() {
        return "rect-triangle-circle";
    }

    @Override
    public Range xRange() {
        return new Range(-3, 3);
    }

    @Override
    public Range yRange() {
        return new Range(-5, 3);
    }

    @Override
    public boolean contains(double x, double y, double r) {
        double half = r / 2;
        boolean rect = x <= 0 && x >= -half && y >= 0 && y <= r;
        boolean triangle = x >= 0 && x <= r && y <= 0 && y >= x / 2 - half;
        boolean circle = x >= 0 && y >= 0 && x * x + y * y <= half * half;
        return rect || triangle || circle;
    }
}
