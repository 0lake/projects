package flats.common.protocol;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InvalidClassException;
import java.io.ObjectInputFilter;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.io.Serializable;

/**
 * Сериализация сообщений для передачи по TCP.
 *
 * <p>Сообщение передаётся кадром: четыре байта длины (big-endian) и затем сериализованный объект.
 * Десериализация данных из сети небезопасна, поэтому разрешены только классы протокола и модели
 * из белого списка, а размер и глубина графа объектов ограничены.
 */
public final class Wire {
    /** Максимальный размер запроса, байт. */
    public static final int MAX_REQUEST_BYTES = 64 * 1024;
    /** Максимальный размер ответа, байт. */
    public static final int MAX_RESPONSE_BYTES = 32 * 1024 * 1024;

    private static final String FILTER_PATTERN = "flats.common.**;java.lang.*;java.util.ArrayList;"
            + "java.time.*;java.time.zone.*;!*";

    private Wire() {
    }

    /**
     * Сериализует объект.
     *
     * @throws IOException если объект не удалось сериализовать
     */
    public static byte[] encode(Serializable message) throws IOException {
        var bytes = new ByteArrayOutputStream();
        try (var out = new ObjectOutputStream(bytes)) {
            out.writeObject(message);
        }
        return bytes.toByteArray();
    }

    /**
     * Десериализует объект ожидаемого типа с проверкой по белому списку классов.
     *
     * @param payload  байты сообщения
     * @param type     ожидаемый тип
     * @param maxBytes ограничение размера
     * @throws IOException если данные повреждены, запрещены или имеют не тот тип
     */
    public static <T> T decode(byte[] payload, Class<T> type, int maxBytes) throws IOException {
        if (payload.length > maxBytes) {
            throw new IOException("Сообщение слишком большое: " + payload.length + " байт");
        }
        var filter = ObjectInputFilter.Config.createFilter(FILTER_PATTERN
                + ";maxdepth=20;maxrefs=500000;maxbytes=" + maxBytes);
        try (var in = new ObjectInputStream(new ByteArrayInputStream(payload))) {
            in.setObjectInputFilter(filter);
            Object value = in.readObject();
            if (!type.isInstance(value)) {
                throw new InvalidClassException("Ожидался " + type.getSimpleName());
            }
            return type.cast(value);
        } catch (ClassNotFoundException e) {
            throw new IOException("Неизвестный класс в сообщении", e);
        }
    }
}
