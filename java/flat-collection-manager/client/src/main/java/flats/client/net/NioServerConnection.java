package flats.client.net;

import flats.common.protocol.Request;
import flats.common.protocol.Response;
import flats.common.protocol.Wire;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.net.SocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.SelectionKey;
import java.nio.channels.Selector;
import java.nio.channels.SocketChannel;
import java.util.concurrent.TimeUnit;

/**
 * Неблокирующий клиент на {@link SocketChannel} и {@link Selector}.
 *
 * <p>Каждый запрос идёт по новому соединению. Подключение повторяется с нарастающей паузой,
 * потому что сервер может быть ещё не запущен. После того как запрос отправлен, повторов нет:
 * иначе команда {@code add} могла бы выполниться дважды, если оборвётся только ответ.
 */
public final class NioServerConnection implements ServerConnection {
    private static final long STEP_TIMEOUT_MS = 10_000;

    private final SocketAddress address;
    private final int connectAttempts;
    private final long firstBackoffMs;

    public NioServerConnection(String host, int port) {
        this(new InetSocketAddress(host, port), 3, 500);
    }

    public NioServerConnection(SocketAddress address, int connectAttempts, long firstBackoffMs) {
        this.address = address;
        this.connectAttempts = connectAttempts;
        this.firstBackoffMs = firstBackoffMs;
    }

    @Override
    public Response send(Request request) throws IOException {
        byte[] payload = Wire.encode(request);
        if (payload.length > Wire.MAX_REQUEST_BYTES) {
            throw new IOException("Запрос слишком большой");
        }
        try (SocketChannel channel = connectWithRetry(); Selector selector = Selector.open()) {
            channel.configureBlocking(false);
            ByteBuffer out = ByteBuffer.allocate(4 + payload.length).putInt(payload.length).put(payload).flip();
            var key = channel.register(selector, SelectionKey.OP_WRITE);
            writeAll(channel, selector, out);
            key.interestOps(SelectionKey.OP_READ);
            return readResponse(channel, selector);
        }
    }

    private SocketChannel connectWithRetry() throws IOException {
        IOException last = null;
        long backoff = firstBackoffMs;
        for (int attempt = 1; attempt <= connectAttempts; attempt++) {
            try {
                return connect();
            } catch (IOException e) {
                last = e;
                if (attempt < connectAttempts) {
                    sleep(backoff);
                    backoff *= 2;
                }
            }
        }
        throw new IOException("Сервер недоступен (" + address + ")", last);
    }

    private SocketChannel connect() throws IOException {
        SocketChannel channel = SocketChannel.open();
        try (Selector selector = Selector.open()) {
            channel.configureBlocking(false);
            if (!channel.connect(address)) {
                channel.register(selector, SelectionKey.OP_CONNECT);
                long deadline = System.nanoTime() + TimeUnit.MILLISECONDS.toNanos(STEP_TIMEOUT_MS);
                while (!channel.finishConnect()) {
                    long left = TimeUnit.NANOSECONDS.toMillis(deadline - System.nanoTime());
                    if (left <= 0) {
                        throw new IOException("Тайм-аут подключения");
                    }
                    selector.select(left);
                    selector.selectedKeys().clear();
                }
            }
            return channel;
        } catch (IOException e) {
            channel.close();
            throw e;
        }
    }

    private static void writeAll(SocketChannel channel, Selector selector, ByteBuffer buffer) throws IOException {
        while (buffer.hasRemaining()) {
            await(selector, "отправки запроса");
            channel.write(buffer);
        }
    }

    private static Response readResponse(SocketChannel channel, Selector selector) throws IOException {
        ByteBuffer header = ByteBuffer.allocate(4);
        fill(channel, selector, header);
        int length = header.flip().getInt();
        if (length <= 0 || length > Wire.MAX_RESPONSE_BYTES) {
            throw new IOException("Недопустимая длина ответа: " + length);
        }
        ByteBuffer body = ByteBuffer.allocate(length);
        fill(channel, selector, body);
        return Wire.decode(body.array(), Response.class, Wire.MAX_RESPONSE_BYTES);
    }

    private static void fill(SocketChannel channel, Selector selector, ByteBuffer buffer) throws IOException {
        while (buffer.hasRemaining()) {
            await(selector, "ответа сервера");
            if (channel.read(buffer) < 0) {
                throw new IOException("Сервер закрыл соединение до окончания ответа");
            }
        }
    }

    private static void await(Selector selector, String what) throws IOException {
        if (selector.select(STEP_TIMEOUT_MS) == 0) {
            throw new IOException("Тайм-аут ожидания " + what);
        }
        selector.selectedKeys().clear();
    }

    private static void sleep(long millis) throws IOException {
        try {
            Thread.sleep(millis);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new IOException("Подключение прервано", e);
        }
    }
}
