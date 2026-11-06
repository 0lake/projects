package flats.common.protocol;

import flats.common.model.Flat;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;

/**
 * Ответ сервера.
 *
 * @param status  результат
 * @param message текстовое сообщение для пользователя
 * @param flats   элементы коллекции, отсортированные по названию; пустой список, если элементы не нужны
 */
public record Response(Status status, String message, List<Flat> flats) implements Serializable {
    private static final long serialVersionUID = 1L;

    /**
     * Копирует список в {@link ArrayList}, чтобы ответ не зависел от изменяемой коллекции сервера.
     */
    public Response {
        flats = flats == null ? new ArrayList<>() : new ArrayList<>(flats);
    }

    /** @return успешный ответ с сообщением */
    public static Response ok(String message) {
        return new Response(Status.OK, message, List.of());
    }

    /** @return успешный ответ с сообщением и списком элементов */
    public static Response ok(String message, List<Flat> flats) {
        return new Response(Status.OK, message, flats);
    }

    /** @return ответ с ошибкой */
    public static Response error(String message) {
        return new Response(Status.ERROR, message, List.of());
    }

    /** @return ответ с заданным статусом без элементов */
    public static Response of(Status status, String message) {
        return new Response(status, message, List.of());
    }

    /** @return true, если команда выполнена */
    public boolean isOk() {
        return status == Status.OK;
    }
}
