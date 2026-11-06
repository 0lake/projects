package flats.common.model;

import java.io.Serializable;

/**
 * Дом, в котором находится квартира. Два дома равны, если равны все поля,
 * поэтому по дому можно группировать квартиры.
 *
 * @param name                название, не null
 * @param year                год постройки, больше 0
 * @param numberOfFlatsOnFloor количество квартир на этаже, больше 0
 * @param numberOfLifts       количество лифтов, больше 0
 */
public record House(String name, Integer year, Long numberOfFlatsOnFloor, long numberOfLifts)
        implements Serializable {
    private static final long serialVersionUID = 1L;

    /**
     * @throws ValidationException если нарушены ограничения полей
     */
    public House {
        Validation.notNull(name, "name");
        Validation.positive(Validation.notNull(year, "year"), "year");
        Validation.positive(Validation.notNull(numberOfFlatsOnFloor, "numberOfFlatsOnFloor"),
                "numberOfFlatsOnFloor");
        Validation.positive(numberOfLifts, "numberOfLifts");
    }
}
