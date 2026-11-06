package flats.client;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import flats.client.net.NioServerConnection;
import flats.common.protocol.CommandType;
import flats.common.protocol.Request;
import flats.common.protocol.Status;
import flats.server.ServerFixture;
import flats.server.net.Server;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.PrintStream;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;

/**
 * Клиент и сервер, соединённые настоящим TCP-сокетом на свободном порту.
 */
public class EndToEndTest {
    private static final String[] FLAT = {
        "Лофт", "10", "-5.5", "45", "2", "3", "9.5", "good", "Северный", "1998", "4", "2"};

    private ServerFixture fixture;
    private Server server;
    private NioServerConnection connection;

    @Before
    public void start() throws IOException {
        fixture = new ServerFixture();
        server = new Server(0, fixture.processor, 2, 2);
        server.start();
        connection = new NioServerConnection(new InetSocketAddress("127.0.0.1", server.port()), 2, 50);
    }

    @After
    public void stop() {
        server.close();
    }

    private String session(String... lines) throws IOException {
        var bytes = new ByteArrayOutputStream();
        var app = new ClientApp(connection, new PrintStream(bytes, true, StandardCharsets.UTF_8));
        app.run(new ScriptedInput(List.of(lines)));
        return bytes.toString(StandardCharsets.UTF_8);
    }

    private static List<String> lines(String... head) {
        return new ArrayList<>(List.of(head));
    }

    @Test
    public void registerAddShowFlow() throws IOException {
        var input = lines("register oleg", "secret1", "add");
        input.addAll(List.of(FLAT));
        input.addAll(List.of("show", "exit"));
        String output = session(input.toArray(String[]::new));
        assertTrue(output, output.contains("зарегистрирован"));
        assertTrue(output, output.contains("Квартира добавлена, id = "));
        assertTrue(output, output.contains("название: Лофт"));
        assertEquals(1, fixture.collection.size());
        assertEquals("oleg", fixture.flats.findAll().get(0).owner());
    }

    @Test
    public void commandsNeedLogin() throws IOException {
        String output = session("show", "exit");
        assertTrue(output, output.contains("Сначала выполните login"));
    }

    @Test
    public void wrongPasswordIsRejected() throws IOException {
        fixture.register("oleg", "secret1");
        String output = session("login oleg", "wrong", "show", "exit");
        assertTrue(output, output.contains("Неверный логин или пароль"));
        assertTrue(output, output.contains("Сначала выполните login"));
    }

    @Test
    public void invalidFieldIsAskedAgain() throws IOException {
        var input = lines("register oleg", "secret1", "add", "Лофт", "x", "10", "-5.5", "-3", "45");
        input.addAll(List.of("2", "3", "9.5", "good", "Северный", "1998", "4", "2", "exit"));
        String output = session(input.toArray(String[]::new));
        assertTrue(output, output.contains("Некорректное число. Повторите ввод."));
        assertEquals(1, fixture.collection.size());
    }

    @Test
    public void unknownAndMalformedCommandsAreReported() throws IOException {
        String output = session("register oleg", "secret1", "fly", "remove_by_id abc", "info extra", "exit");
        assertTrue(output, output.contains("Неизвестная команда: fly"));
        assertTrue(output, output.contains("id должен быть положительным числом"));
        assertTrue(output, output.contains("не принимает аргументов"));
    }

    @Test
    public void scriptRunsAndRecursionIsSkipped() throws IOException {
        Path script = Files.createTempFile("flats", ".txt");
        Path nested = Files.createTempFile("flats-nested", ".txt");
        try {
            var body = lines("add");
            body.addAll(List.of(FLAT));
            body.add("execute_script " + script);
            body.add("sum_of_height");
            Files.write(script, body, StandardCharsets.UTF_8);
            Files.write(nested, List.of("# комментарий", "info"), StandardCharsets.UTF_8);
            String output = session("register oleg", "secret1", "execute_script " + script,
                    "execute_script " + nested, "exit");
            assertTrue(output, output.contains("Рекурсивный вызов скрипта пропущен"));
            assertTrue(output, output.contains("Сумма высот: 3"));
            assertTrue(output, output.contains("Количество элементов: 1"));
            assertEquals(1, fixture.collection.size());
        } finally {
            Files.deleteIfExists(script);
            Files.deleteIfExists(nested);
        }
    }

    @Test
    public void invalidValueInScriptAbortsTheCommand() throws IOException {
        Path script = Files.createTempFile("flats-bad", ".txt");
        try {
            Files.write(script, List.of("add", "Лофт", "не число"), StandardCharsets.UTF_8);
            String output = session("register oleg", "secret1", "execute_script " + script, "exit");
            assertTrue(output, output.contains("Ошибка в скрипте"));
            assertEquals(0, fixture.collection.size());
        } finally {
            Files.deleteIfExists(script);
        }
    }

    @Test
    public void usersDoNotTouchEachOthersFlats() throws IOException {
        var anna = lines("register anna", "secret1", "add");
        anna.addAll(List.of(FLAT));
        anna.add("exit");
        session(anna.toArray(String[]::new));
        long id = fixture.flats.findAll().get(0).id();
        String output = session("register boris", "secret2", "remove_by_id " + id, "clear", "exit");
        assertTrue(output, output.contains("принадлежит другому пользователю"));
        assertTrue(output, output.contains("Удалено ваших элементов: 0"));
        assertEquals(1, fixture.collection.size());
    }

    @Test
    public void serverUnavailableIsReported() throws IOException {
        server.close();
        var down = new NioServerConnection(new InetSocketAddress("127.0.0.1", server.port()), 2, 10);
        var bytes = new ByteArrayOutputStream();
        new ClientApp(down, new PrintStream(bytes, true, StandardCharsets.UTF_8))
                .run(new ScriptedInput(List.of("register oleg", "secret1", "exit")));
        assertTrue(bytes.toString(StandardCharsets.UTF_8).contains("Ошибка связи с сервером"));
    }

    @Test
    public void manyClientsInParallel() throws Exception {
        fixture.register("oleg", "secret1");
        ExecutorService pool = Executors.newFixedThreadPool(10);
        List<Future<Status>> results = new ArrayList<>();
        for (int i = 0; i < 100; i++) {
            results.add(pool.submit(() -> connection.send(
                    Request.of("oleg", "secret1", CommandType.INFO)).status()));
        }
        for (Future<Status> result : results) {
            assertEquals(Status.OK, result.get());
        }
        pool.shutdown();
    }

    @Test
    public void garbageFromNetworkDoesNotKillServer() throws Exception {
        try (Socket socket = new Socket("127.0.0.1", server.port())) {
            socket.getOutputStream().write(new byte[] {0x7f, 0x7f, 0x7f, 0x7f, 1, 2, 3});
            socket.getOutputStream().flush();
            assertFalse(socket.getInputStream().read() > 0);
        }
        try (Socket socket = new Socket("127.0.0.1", server.port())) {
            socket.getOutputStream().write(new byte[] {0, 0, 0, 5, 1, 2, 3, 4, 5});
            socket.getOutputStream().flush();
            assertFalse(socket.getInputStream().read() > 0);
        }
        fixture.register("oleg", "secret1");
        assertEquals(Status.OK, connection.send(Request.of("oleg", "secret1", CommandType.INFO)).status());
    }
}
