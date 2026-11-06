package flats.common.model;

import java.util.Arrays;
import java.util.stream.Collectors;

/**
 * Вид из окна квартиры.
 */
public enum View {
    STREET,
    YARD,
    BAD,
    GOOD;

    /**
     * @return имена всех констант через запятую, для подсказки пользователю
     */
    public static String names() {
        return Arrays.stream(values()).map(Enum::name).collect(Collectors.joining(", "));
    }
}
