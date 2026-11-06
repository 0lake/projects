package flats.common.model;

import java.io.Serializable;

/**
 * Координаты квартиры.
 *
 * @param x координата x, не null
 * @param y координата y, не null, строго больше {@value #MIN_Y}
 */
public record Coordinates(Long x, Float y) implements Serializable {
    private static final long serialVersionUID = 1L;

    /** Нижняя (исключённая) граница координаты y. */
    public static final float MIN_Y = -519f;

    /**
     * @throws ValidationException если нарушены ограничения полей
     */
    public Coordinates {
        Validation.notNull(x, "x");
        Validation.notNull(y, "y");
        if (!(y > MIN_Y)) {
            throw new ValidationException("Значение поля 'y' должно быть больше " + (int) MIN_Y);
        }
    }

    @Override
    public String toString() {
        return x + ";" + y;
    }
}
