package flats.common.protocol;

import java.util.Arrays;
import java.util.Map;
import java.util.Optional;
import java.util.function.Function;
import java.util.stream.Collectors;

/**
 * Все команды приложения. Описание команды хранится в одном месте и используется
 * клиентом (разбор строки, справка) и сервером (диспетчеризация).
 */
public enum CommandType {
    HELP("help", ArgumentKind.NONE, false, true, false, "вывести справку по доступным командам"),
    REGISTER("register", ArgumentKind.LOGIN, false, false, false, "зарегистрировать нового пользователя"),
    LOGIN("login", ArgumentKind.LOGIN, false, false, false, "войти под существующим пользователем"),
    INFO("info", ArgumentKind.NONE, false, false, true,
            "вывести информацию о коллекции (тип, дата инициализации, количество элементов)"),
    SHOW("show", ArgumentKind.NONE, false, false, true,
            "вывести все элементы коллекции, отсортированные по названию"),
    ADD("add", ArgumentKind.NONE, true, false, true, "добавить новый элемент в коллекцию"),
    UPDATE("update", ArgumentKind.ID, true, false, true,
            "обновить значение своего элемента, id которого равен заданному"),
    REMOVE_BY_ID("remove_by_id", ArgumentKind.ID, false, false, true, "удалить свой элемент по id"),
    CLEAR("clear", ArgumentKind.NONE, false, false, true, "удалить все свои элементы"),
    EXECUTE_SCRIPT("execute_script", ArgumentKind.FILE, false, true, false,
            "считать и исполнить скрипт из указанного файла"),
    EXIT("exit", ArgumentKind.NONE, false, true, false, "завершить клиент"),
    ADD_IF_MIN("add_if_min", ArgumentKind.NONE, true, false, true,
            "добавить элемент, если его значение меньше наименьшего в коллекции"),
    REMOVE_GREATER("remove_greater", ArgumentKind.NONE, true, false, true,
            "удалить свои элементы, превышающие заданный"),
    REMOVE_LOWER("remove_lower", ArgumentKind.NONE, true, false, true,
            "удалить свои элементы, меньшие чем заданный"),
    SUM_OF_HEIGHT("sum_of_height", ArgumentKind.NONE, false, false, true,
            "вывести сумму значений поля height для всех элементов"),
    GROUP_COUNTING_BY_HOUSE("group_counting_by_house", ArgumentKind.NONE, false, false, true,
            "сгруппировать элементы по полю house и вывести количество в каждой группе"),
    FILTER_STARTS_WITH_NAME("filter_starts_with_name", ArgumentKind.TEXT, false, false, true,
            "вывести элементы, название которых начинается с заданной подстроки");

    private static final Map<String, CommandType> BY_NAME = Arrays.stream(values())
            .collect(Collectors.toUnmodifiableMap(CommandType::commandName, Function.identity()));

    private final String commandName;
    private final ArgumentKind argument;
    private final boolean takesElement;
    private final boolean clientSide;
    private final boolean requiresAuth;
    private final String description;

    CommandType(String commandName, ArgumentKind argument, boolean takesElement, boolean clientSide,
                boolean requiresAuth, String description) {
        this.commandName = commandName;
        this.argument = argument;
        this.takesElement = takesElement;
        this.clientSide = clientSide;
        this.requiresAuth = requiresAuth;
        this.description = description;
    }

    /**
     * @param name имя команды, как его вводит пользователь
     * @return команда или пустой Optional, если такой нет
     */
    public static Optional<CommandType> byName(String name) {
        return Optional.ofNullable(BY_NAME.get(name));
    }

    /** @return имя команды, как его вводит пользователь */
    public String commandName() {
        return commandName;
    }

    /** @return вид аргумента в строке команды */
    public ArgumentKind argument() {
        return argument;
    }

    /** @return true, если команде нужен элемент коллекции, вводимый по полям */
    public boolean takesElement() {
        return takesElement;
    }

    /** @return true, если команда выполняется на клиенте и на сервер не отправляется */
    public boolean clientSide() {
        return clientSide;
    }

    /** @return true, если команду разрешено выполнять только авторизованному пользователю */
    public boolean requiresAuth() {
        return requiresAuth;
    }

    /** @return текстовое описание команды */
    public String description() {
        return description;
    }

    /**
     * @return строка использования, например {@code update <id> {element}}
     */
    public String usage() {
        return commandName + argument.usage() + (takesElement ? " {element}" : "");
    }
}
