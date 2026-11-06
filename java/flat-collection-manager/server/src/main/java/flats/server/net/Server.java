package flats.server.net;

import flats.common.protocol.Request;
import flats.common.protocol.Response;
import flats.common.protocol.Wire;
import flats.server.command.RequestProcessor;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.net.InetSocketAddress;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.SocketTimeoutException;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.ForkJoinPool;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Многопоточный TCP-сервер. Одно соединение обслуживает один запрос.
 *
 * <p>Обработка конвейером: приём соединений идёт в одном потоке; чтение запроса выполняет
 * пул чтения, выполнение команды пул обработки, отправку ответа {@link ForkJoinPool}.
 * Этапы связаны через {@link CompletableFuture}, поэтому медленный клиент блокирует только
 * свой поток чтения, а не обработку остальных.
 */
public final class Server implements AutoCloseable {
    private static final System.Logger LOG = System.getLogger(Server.class.getName());
    private static final int IO_TIMEOUT_MS = 10_000;

    private final RequestProcessor processor;
    private final ServerSocket serverSocket;
    private final ExecutorService readPool;
    private final ExecutorService workPool;
    private final ForkJoinPool sendPool = new ForkJoinPool();
    private final AtomicInteger inFlight = new AtomicInteger();
    private volatile boolean running = true;
    private Thread acceptThread;

    /**
     * Открывает порт. Порт 0 означает «любой свободный», фактический порт возвращает {@link #port()}.
     */
    public Server(int port, RequestProcessor processor, int readThreads, int workThreads) throws IOException {
        this.processor = processor;
        this.readPool = Executors.newFixedThreadPool(readThreads);
        this.workPool = Executors.newFixedThreadPool(workThreads);
        this.serverSocket = new ServerSocket();
        serverSocket.setReuseAddress(true);
        serverSocket.bind(new InetSocketAddress(port));
    }

    /** @return порт, на котором сервер принимает соединения */
    public int port() {
        return serverSocket.getLocalPort();
    }

    /** Запускает приём соединений в отдельном потоке. */
    public void start() {
        acceptThread = new Thread(this::acceptLoop, "accept");
        acceptThread.start();
        LOG.log(System.Logger.Level.INFO, "Сервер слушает порт " + port());
    }

    /** Блокирует вызывающий поток до остановки сервера. */
    public void await() throws InterruptedException {
        acceptThread.join();
    }

    private void acceptLoop() {
        while (running) {
            try {
                Socket socket = serverSocket.accept();
                inFlight.incrementAndGet();
                CompletableFuture
                        .supplyAsync(() -> readRequest(socket), readPool)
                        .thenApplyAsync(request -> request == null ? null : processor.process(request), workPool)
                        .thenAcceptAsync(response -> sendAndClose(socket, response), sendPool)
                        .exceptionally(error -> {
                            LOG.log(System.Logger.Level.ERROR, "Сбой обработки соединения", error);
                            closeQuietly(socket);
                            return null;
                        })
                        .whenComplete((ignored, error) -> inFlight.decrementAndGet());
            } catch (IOException e) {
                if (running) {
                    LOG.log(System.Logger.Level.ERROR, "Ошибка приёма соединения", e);
                }
            }
        }
    }

    private Request readRequest(Socket socket) {
        try {
            socket.setSoTimeout(IO_TIMEOUT_MS);
            var in = new DataInputStream(socket.getInputStream());
            int length = in.readInt();
            if (length <= 0 || length > Wire.MAX_REQUEST_BYTES) {
                LOG.log(System.Logger.Level.WARNING, "Недопустимая длина запроса: " + length);
                return null;
            }
            byte[] payload = new byte[length];
            in.readFully(payload);
            return Wire.decode(payload, Request.class, Wire.MAX_REQUEST_BYTES);
        } catch (SocketTimeoutException e) {
            LOG.log(System.Logger.Level.WARNING, "Клиент не прислал запрос вовремя");
            return null;
        } catch (IOException e) {
            LOG.log(System.Logger.Level.WARNING, "Не удалось прочитать запрос: " + e.getMessage());
            return null;
        }
    }

    private void sendAndClose(Socket socket, Response response) {
        try (socket) {
            if (response == null) {
                return;
            }
            byte[] payload = Wire.encode(response);
            var out = new DataOutputStream(socket.getOutputStream());
            out.writeInt(payload.length);
            out.write(payload);
            out.flush();
        } catch (IOException e) {
            LOG.log(System.Logger.Level.WARNING, "Не удалось отправить ответ: " + e.getMessage());
        }
    }

    private static void closeQuietly(Socket socket) {
        try {
            socket.close();
        } catch (IOException ignored) {
            // соединение уже закрыто
        }
    }

    /**
     * Останавливает приём соединений, дожидается начатых запросов (не дольше 5 секунд)
     * и только потом закрывает пулы, чтобы не отклонять этапы уже принятых запросов.
     */
    @Override
    public void close() {
        running = false;
        try {
            serverSocket.close();
        } catch (IOException e) {
            LOG.log(System.Logger.Level.WARNING, "Ошибка закрытия порта", e);
        }
        try {
            if (acceptThread != null) {
                acceptThread.join(5_000);
            }
            long deadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(5);
            while (inFlight.get() > 0 && System.nanoTime() < deadline) {
                Thread.sleep(10);
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        readPool.shutdown();
        workPool.shutdown();
        sendPool.shutdown();
    }
}
