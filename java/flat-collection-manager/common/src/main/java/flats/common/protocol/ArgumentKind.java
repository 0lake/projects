package flats.common.protocol;

/**
 * Вид аргумента, который команда принимает в той же строке, что и своё имя.
 */
public enum ArgumentKind {
    /** Без аргумента. */
    NONE(""),
    /** Идентификатор квартиры. */
    ID(" <id>"),
    /** Произвольная строка. */
    TEXT(" <text>"),
    /** Путь к файлу скрипта. */
    FILE(" <file_name>"),
    /** Логин пользователя. */
    LOGIN(" <login>");

    private final String usage;

    ArgumentKind(String usage) {
        this.usage = usage;
    }

    /**
     * @return шаблон аргумента для строки справки
     */
    public String usage() {
        return usage;
    }
}
