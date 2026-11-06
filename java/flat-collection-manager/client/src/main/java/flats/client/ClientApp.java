package flats.client;

import flats.client.form.ElementForm;
import flats.client.form.InputEnded;
import flats.client.io.InputSource;
import flats.client.io.ScriptInput;
import flats.client.net.ServerConnection;
import flats.common.model.ValidationException;
import flats.common.protocol.CommandType;
import flats.common.protocol.Request;
import flats.common.protocol.Response;

import java.io.IOException;
import java.io.PrintStream;
import java.nio.file.Files;
import java.nio.file.InvalidPathException;
import java.nio.file.Path;
import java.util.ArrayDeque;
import java.util.Arrays;
import java.util.Deque;

/**
 * Консольный клиент: читает команды, собирает запросы и печатает ответы.
 */
public final class ClientApp {
    private static final int MAX_SCRIPT_DEPTH = 16;

    private final ServerConnection connection;
    private final PrintStream out;
    private final Deque<Path> runningScripts = new ArrayDeque<>();
    private String login;
    private String password;
    private boolean exit;

    public ClientApp(ServerConnection connection, PrintStream out) {
        this.connection = connection;
        this.out = out;
    }

    /**
     * Выполняет команды до конца ввода или до команды exit.
     */
    public void run(InputSource input) throws IOException {
        if (input.interactive()) {
            out.println("Введите help для списка команд. Для начала выполните login или register.");
        }
        while (!exit) {
            if (input.interactive()) {
                out.print("> ");
                out.flush();
            }
            String line = input.readLine();
            if (line == null) {
                return;
            }
            executeLine(line, input);
        }
    }

    private void executeLine(String line, InputSource input) throws IOException {
        String trimmed = line.strip();
        if (trimmed.isEmpty() || trimmed.startsWith("#")) {
            return;
        }
        String[] parts = trimmed.split("\\s+", 2);
        String argument = parts.length > 1 ? parts[1].strip() : null;
        var type = CommandType.byName(parts[0]);
        if (type.isEmpty()) {
            out.println("Неизвестная команда: " + parts[0] + ". Введите help.");
            return;
        }
        CommandType command = type.get();
        String problem = checkArgument(command, argument);
        if (problem != null) {
            out.println(problem);
            return;
        }
        try {
            switch (command) {
                case HELP -> help();
                case EXIT -> exit = true;
                case EXECUTE_SCRIPT -> executeScript(argument);
                case REGISTER, LOGIN -> authenticate(command, argument, input);
                default -> remote(command, argument, input);
            }
        } catch (ValidationException e) {
            out.println(e.getMessage());
        } catch (InputEnded e) {
            out.println(e.getMessage());
        }
    }

    private static String checkArgument(CommandType command, String argument) {
        return switch (command.argument()) {
            case NONE -> argument == null ? null : "Команда " + command.commandName() + " не принимает аргументов";
            case ID -> {
                try {
                    yield argument != null && Long.parseLong(argument) > 0 ? null : "id должен быть положительным числом";
                } catch (NumberFormatException e) {
                    yield "id должен быть положительным числом";
                }
            }
            case LOGIN -> argument == null || argument.contains(" ") ? "Использование: " + command.usage() : null;
            case TEXT, FILE -> argument == null || argument.isEmpty() ? "Использование: " + command.usage() : null;
        };
    }

    private void help() {
        Arrays.stream(CommandType.values())
                .forEach(c -> out.printf("%-42s %s%n", c.usage(), c.description()));
    }

    private void authenticate(CommandType command, String loginArgument, InputSource input) throws IOException {
        out.print("Пароль: ");
        out.flush();
        String entered = input.readSecret();
        if (entered == null) {
            throw new InputEnded();
        }
        Response response = send(new Request(loginArgument, entered, command, null, null));
        if (response != null && response.isOk()) {
            login = loginArgument;
            password = entered;
        }
    }

    private void remote(CommandType command, String argument, InputSource input) throws IOException {
        if (login == null) {
            out.println("Сначала выполните login или register");
            return;
        }
        var element = command.takesElement() ? new ElementForm(input, out).read() : null;
        Response response = send(new Request(login, password, command, argument, element));
        if (response != null) {
            response.flats().forEach(f -> out.println(FlatFormatter.format(f)));
        }
    }

    /** Отправляет запрос и печатает сообщение; возвращает null, если сервер недоступен. */
    private Response send(Request request) {
        try {
            Response response = connection.send(request);
            out.println(response.message());
            return response;
        } catch (IOException e) {
            out.println("Ошибка связи с сервером: " + e.getMessage());
            return null;
        }
    }

    private void executeScript(String fileName) throws IOException {
        Path file;
        try {
            file = Path.of(fileName).toRealPath();
        } catch (InvalidPathException | IOException e) {
            out.println("Файл скрипта не найден: " + fileName);
            return;
        }
        if (!Files.isRegularFile(file) || !Files.isReadable(file)) {
            out.println("Файл скрипта недоступен: " + fileName);
            return;
        }
        if (runningScripts.contains(file)) {
            out.println("Рекурсивный вызов скрипта пропущен: " + fileName);
            return;
        }
        if (runningScripts.size() >= MAX_SCRIPT_DEPTH) {
            out.println("Слишком глубокая вложенность скриптов");
            return;
        }
        runningScripts.push(file);
        try (var script = new ScriptInput(file)) {
            String line;
            while (!exit && (line = script.readLine()) != null) {
                executeLine(line, script);
            }
        } finally {
            runningScripts.pop();
        }
    }
}
