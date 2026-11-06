package flats.common.protocol;

import flats.common.model.FlatDraft;

import java.io.Serializable;

/**
 * Запрос клиента. Логин и пароль отправляются с каждым запросом.
 *
 * @param login    логин, может быть null до авторизации
 * @param password пароль в открытом виде, может быть null до авторизации
 * @param type     команда
 * @param argument аргумент из строки команды, может быть null
 * @param element  введённый элемент для команд, которым он нужен, иначе null
 */
public record Request(String login, String password, CommandType type, String argument,
                      FlatDraft element) implements Serializable {
    private static final long serialVersionUID = 1L;

    /**
     * @return запрос без аргумента и элемента
     */
    public static Request of(String login, String password, CommandType type) {
        return new Request(login, password, type, null, null);
    }

    /**
     * Строковое представление намеренно скрывает пароль, чтобы он не попал в журнал.
     */
    @Override
    public String toString() {
        return "Request[login=" + login + ", password=" + (password == null ? "null" : "***")
                + ", type=" + type + ", argument=" + argument + ", element=" + element + "]";
    }
}
