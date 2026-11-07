package area;

import java.util.List;

/**
 * Допустимые значения параметра R.
 */
public final class Radius {
    /** Допустимые значения R. */
    public static final List<Double> VALUES = List.of(1.0, 1.5, 2.0, 2.5, 3.0);

    private Radius() {
    }

    /** @return true, если R входит в список допустимых */
    public static boolean isAllowed(double r) {
        return VALUES.contains(r);
    }
}
