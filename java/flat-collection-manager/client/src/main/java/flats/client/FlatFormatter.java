package flats.client;

import flats.common.model.Flat;

import java.time.format.DateTimeFormatter;

/**
 * Текстовое представление квартиры для консоли.
 */
public final class FlatFormatter {
    private static final DateTimeFormatter DATE = DateTimeFormatter.ofPattern("dd.MM.yyyy HH:mm");

    private FlatFormatter() {
    }

    /** @return многострочное описание квартиры */
    public static String format(Flat f) {
        return """
                id: %d (владелец: %s)
                  название: %s
                  координаты: %s
                  создана: %s
                  площадь: %s, комнат: %d, высота: %d, кухня: %s
                  вид: %s
                  дом: «%s», %d г., квартир на этаже: %d, лифтов: %d"""
                .formatted(f.id(), f.owner(), f.name(), f.coordinates(), f.creationDate().format(DATE),
                        f.area() == null ? "не задана" : f.area(), f.numberOfRooms(), f.height(),
                        f.kitchenArea(), f.view(), f.house().name(), f.house().year(),
                        f.house().numberOfFlatsOnFloor(), f.house().numberOfLifts());
    }
}
