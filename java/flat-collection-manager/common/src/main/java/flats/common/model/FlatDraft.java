package flats.common.model;

import java.io.Serializable;
import java.util.Comparator;

/**
 * Данные квартиры, которые вводит пользователь. Поля {@code id}, {@code creationDate}
 * и владелец генерируются автоматически и появляются только у {@link Flat}.
 *
 * <p>Порядок по умолчанию задаёт {@link #VALUE_ORDER}: по площади, затем по количеству
 * комнат и названию.
 *
 * @param name          название, не null и не пустое
 * @param coordinates   координаты, не null
 * @param area          площадь, null или больше 0
 * @param numberOfRooms количество комнат, больше 0
 * @param height        высота, больше 0
 * @param kitchenArea   площадь кухни, не null, больше 0
 * @param view          вид из окна, не null
 * @param house         дом, не null
 */
public record FlatDraft(String name, Coordinates coordinates, Integer area, int numberOfRooms,
                        int height, Float kitchenArea, View view, House house) implements Serializable {
    private static final long serialVersionUID = 1L;

    /** Порядок сравнения квартир по значению, без учёта id. */
    public static final Comparator<FlatDraft> VALUE_ORDER = Comparator
            .comparingInt((FlatDraft d) -> d.area() == null ? 0 : d.area())
            .thenComparingInt(FlatDraft::numberOfRooms)
            .thenComparing(FlatDraft::name);

    /**
     * @throws ValidationException если нарушены ограничения полей
     */
    public FlatDraft {
        name = Validation.notBlank(name, "name");
        Validation.notNull(coordinates, "coordinates");
        if (area != null) {
            Validation.positive(area, "area");
        }
        Validation.positive(numberOfRooms, "numberOfRooms");
        Validation.positive(height, "height");
        Validation.positive(Validation.notNull(kitchenArea, "kitchenArea"), "kitchenArea");
        Validation.notNull(view, "view");
        Validation.notNull(house, "house");
    }
}
