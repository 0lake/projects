package flats.common.model;

import java.io.Serializable;
import java.time.ZonedDateTime;

/**
 * Квартира, хранимая в коллекции. Естественный порядок задаёт
 * {@link FlatDraft#VALUE_ORDER}, при равенстве значений порядок определяет id.
 *
 * @param id           уникальный положительный идентификатор, назначает база данных
 * @param name         название, не null и не пустое
 * @param coordinates  координаты, не null
 * @param creationDate дата создания, не null, назначается автоматически
 * @param area         площадь, null или больше 0
 * @param numberOfRooms количество комнат, больше 0
 * @param height       высота, больше 0
 * @param kitchenArea  площадь кухни, не null, больше 0
 * @param view         вид из окна, не null
 * @param house        дом, не null
 * @param owner        логин пользователя, создавшего квартиру
 */
public record Flat(long id, String name, Coordinates coordinates, ZonedDateTime creationDate,
                   Integer area, int numberOfRooms, int height, Float kitchenArea, View view,
                   House house, String owner) implements Comparable<Flat>, Serializable {
    private static final long serialVersionUID = 1L;

    /**
     * @throws ValidationException если нарушены ограничения полей
     */
    public Flat {
        Validation.positive(id, "id");
        Validation.notNull(creationDate, "creationDate");
        Validation.notBlank(owner, "owner");
        // остальные поля проверяет FlatDraft
        new FlatDraft(name, coordinates, area, numberOfRooms, height, kitchenArea, view, house);
    }

    /**
     * Создаёт квартиру из введённых пользователем данных.
     *
     * @param id           назначенный идентификатор
     * @param creationDate дата создания
     * @param owner        логин владельца
     * @param draft        данные квартиры
     */
    public static Flat of(long id, ZonedDateTime creationDate, String owner, FlatDraft draft) {
        return new Flat(id, draft.name(), draft.coordinates(), creationDate, draft.area(),
                draft.numberOfRooms(), draft.height(), draft.kitchenArea(), draft.view(),
                draft.house(), owner);
    }

    /**
     * @return значения, вводимые пользователем, без служебных полей
     */
    public FlatDraft toDraft() {
        return new FlatDraft(name, coordinates, area, numberOfRooms, height, kitchenArea, view, house);
    }

    /**
     * @return копию с новыми значениями; id, дата создания и владелец сохраняются
     */
    public Flat withDraft(FlatDraft draft) {
        return of(id, creationDate, owner, draft);
    }

    @Override
    public int compareTo(Flat other) {
        int byValue = FlatDraft.VALUE_ORDER.compare(toDraft(), other.toDraft());
        return byValue != 0 ? byValue : Long.compare(id, other.id);
    }
}
