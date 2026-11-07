package area;

import java.io.Serializable;
import java.time.Instant;

/**
 * Результат проверки точки.
 *
 * @param input     проверенная точка и R
 * @param hit       попала ли точка в область
 * @param checkedAt момент проверки
 */
public record CheckResult(CheckInput input, boolean hit, Instant checkedAt) implements Serializable {
    private static final long serialVersionUID = 1L;

    public double x() {
        return input.x();
    }

    public double y() {
        return input.y();
    }

    public double r() {
        return input.r();
    }

    /** @return true, если точка попала в область (имя для EL: {@code result.hit}) */
    public boolean isHit() {
        return hit;
    }
}
