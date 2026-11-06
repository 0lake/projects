package flats.common.model;

/**
 * Проверки полей, общие для всех классов модели. Один набор правил используют
 * клиент (проверка ввода), сервер (проверка запроса) и база данных (CHECK).
 */
public final class Validation {
    private Validation() {
    }

    /**
     * @return значение, если оно не null
     * @throws ValidationException если значение null
     */
    public static <T> T notNull(T value, String field) {
        if (value == null) {
            throw new ValidationException("Поле '" + field + "' не может быть пустым");
        }
        return value;
    }

    /**
     * @return непустую строку без пробелов по краям
     * @throws ValidationException если строка null или состоит из пробелов
     */
    public static String notBlank(String value, String field) {
        if (value == null || value.isBlank()) {
            throw new ValidationException("Поле '" + field + "' не может быть пустым");
        }
        return value.strip();
    }

    /**
     * Проверяет, что строка не пуста.
     *
     * @return строка без пробелов по краям
     */
    public static String requireNotBlank(String value) {
        return notBlank(value, "значение");
    }

    /**
     * Проверяет, что число строго больше нуля.
     */
    public static void positive(long value, String field) {
        if (value <= 0) {
            throw new ValidationException("Значение поля '" + field + "' должно быть больше 0");
        }
    }

    /**
     * Проверяет, что число строго больше нуля.
     */
    public static void positive(float value, String field) {
        if (!(value > 0)) {
            throw new ValidationException("Значение поля '" + field + "' должно быть больше 0");
        }
    }
}
