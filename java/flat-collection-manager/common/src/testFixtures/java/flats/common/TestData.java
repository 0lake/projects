package flats.common;

import flats.common.model.Coordinates;
import flats.common.model.FlatDraft;
import flats.common.model.House;
import flats.common.model.View;

/**
 * Готовые объекты для тестов.
 */
public final class TestData {
    private TestData() {
    }

    public static House house() {
        return new House("Северный", 1998, 4L, 2);
    }

    public static FlatDraft draft(String name, Integer area, int rooms) {
        return new FlatDraft(name, new Coordinates(1L, 2f), area, rooms, 3, 9.5f, View.GOOD, house());
    }
}
