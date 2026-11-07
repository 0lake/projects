package area;

/**
 * Область для версии на сервлетах:
 * <ul>
 *   <li>вторая четверть: четверть круга радиуса R/2;</li>
 *   <li>первая четверть: треугольник с вершинами (0, 0), (R/2, 0), (0, R/2);</li>
 *   <li>третья четверть: квадрат со стороной R.</li>
 * </ul>
 * Четвёртая четверть в область не входит.
 */
public final class CircleTriangleSquare implements Region {
    @Override
    public String name() {
        return "circle-triangle-square";
    }

    @Override
    public Range xRange() {
        return new Range(-5, 5);
    }

    @Override
    public Range yRange() {
        return new Range(-5, 3);
    }

    @Override
    public boolean contains(double x, double y, double r) {
        double half = r / 2;
        boolean circle = x <= 0 && y >= 0 && x * x + y * y <= half * half;
        boolean triangle = x >= 0 && y >= 0 && y <= -x + half;
        boolean square = x <= 0 && x >= -r && y <= 0 && y >= -r;
        return circle || triangle || square;
    }
}
