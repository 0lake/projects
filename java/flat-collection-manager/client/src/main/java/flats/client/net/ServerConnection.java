package flats.client.net;

import flats.common.protocol.Request;
import flats.common.protocol.Response;

import java.io.IOException;

/**
 * Канал связи с сервером: один запрос и один ответ.
 */
public interface ServerConnection {
    /**
     * Отправляет запрос и ждёт ответ.
     *
     * @throws IOException если сервер недоступен или обмен прервался
     */
    Response send(Request request) throws IOException;
}
