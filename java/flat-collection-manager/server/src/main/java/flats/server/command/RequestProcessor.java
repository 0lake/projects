package flats.server.command;

import flats.common.model.Flat;
import flats.common.model.FlatDraft;
import flats.common.protocol.CommandType;
import flats.common.protocol.Request;
import flats.common.protocol.Response;
import flats.common.protocol.Status;
import flats.server.auth.AuthService;
import flats.server.auth.AuthService.RegistrationResult;
import flats.server.collection.CollectionManager;
import flats.server.collection.CollectionManager.Outcome;
import flats.server.store.jdbc.StorageException;

import java.time.format.DateTimeFormatter;
import java.util.Comparator;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Выполняет запрос клиента: проверяет пользователя, вызывает операцию над коллекцией
 * и формирует ответ. Не знает о сети, поэтому проверяется без сокетов.
 */
public final class RequestProcessor {
    private static final System.Logger LOG = System.getLogger(RequestProcessor.class.getName());
    private static final String BAD_CREDENTIALS = "Неверный логин или пароль";

    private final AuthService auth;
    private final CollectionManager collection;

    public RequestProcessor(AuthService auth, CollectionManager collection) {
        this.auth = auth;
        this.collection = collection;
    }

    /**
     * Обрабатывает запрос. Метод не бросает исключений: любая ошибка превращается в ответ.
     */
    public Response process(Request request) {
        try {
            return dispatch(request);
        } catch (IllegalArgumentException e) {
            return Response.error(e.getMessage());
        } catch (StorageException e) {
            LOG.log(System.Logger.Level.ERROR, "Ошибка хранилища при выполнении " + request.type(), e);
            return Response.error("Ошибка базы данных, повторите попытку позже");
        } catch (RuntimeException e) {
            LOG.log(System.Logger.Level.ERROR, "Сбой при выполнении " + request.type(), e);
            return Response.error("Внутренняя ошибка сервера");
        }
    }

    private Response dispatch(Request request) {
        CommandType type = request.type();
        if (type == null || type.clientSide()) {
            return Response.error("Команда не выполняется на сервере");
        }
        if (type == CommandType.REGISTER) {
            return register(request);
        }
        if (!auth.authenticate(request.login(), request.password())) {
            return Response.of(Status.AUTH_REQUIRED, BAD_CREDENTIALS);
        }
        String user = request.login();
        return switch (type) {
            case LOGIN -> Response.ok("Вы вошли как " + user);
            case INFO -> info();
            case SHOW -> {
                var flats = collection.sortedByName();
                yield Response.ok(flats.isEmpty() ? "Коллекция пуста" : "Элементов: " + flats.size(), flats);
            }
            case ADD -> {
                Flat saved = collection.add(user, element(request));
                yield Response.ok("Квартира добавлена, id = " + saved.id());
            }
            case ADD_IF_MIN -> collection.addIfMin(user, element(request))
                    .map(saved -> Response.ok("Квартира добавлена, id = " + saved.id()))
                    .orElseGet(() -> Response.ok("Элемент не добавлен: он не меньше наименьшего в коллекции"));
            case UPDATE -> update(request, user);
            case REMOVE_BY_ID -> remove(request, user);
            case CLEAR -> Response.ok("Удалено ваших элементов: " + collection.clear(user));
            case REMOVE_GREATER -> Response.ok("Удалено элементов: "
                    + collection.removeGreater(user, element(request)));
            case REMOVE_LOWER -> Response.ok("Удалено элементов: "
                    + collection.removeLower(user, element(request)));
            case SUM_OF_HEIGHT -> Response.ok("Сумма высот: " + collection.sumOfHeight());
            case GROUP_COUNTING_BY_HOUSE -> groupByHouse();
            case FILTER_STARTS_WITH_NAME -> filter(request);
            default -> Response.error("Неизвестная команда");
        };
    }

    private Response register(Request request) {
        RegistrationResult result = auth.register(request.login(), request.password());
        return switch (result) {
            case CREATED -> Response.ok("Пользователь " + request.login() + " зарегистрирован");
            case LOGIN_TAKEN -> Response.error("Логин уже занят");
            case INVALID_LOGIN -> Response.error("Логин: 3-32 символа, латиница, цифры и _ . -");
            case INVALID_PASSWORD -> Response.error("Пароль: от 4 до 128 символов");
        };
    }

    private Response info() {
        var date = collection.initializedAt().format(DateTimeFormatter.ofPattern("dd.MM.yyyy HH:mm:ss"));
        return Response.ok("Тип коллекции: PriorityQueue<Flat>\nДата инициализации: " + date
                + "\nКоличество элементов: " + collection.size());
    }

    private Response update(Request request, String user) {
        Long id = parseId(request.argument());
        if (id == null) {
            return Response.error("id должен быть положительным целым числом");
        }
        return outcome(collection.update(id, user, element(request)), id, "обновлена");
    }

    private Response remove(Request request, String user) {
        Long id = parseId(request.argument());
        if (id == null) {
            return Response.error("id должен быть положительным целым числом");
        }
        return outcome(collection.remove(id, user), id, "удалена");
    }

    private static Response outcome(Outcome outcome, long id, String done) {
        return switch (outcome) {
            case OK -> Response.ok("Квартира " + id + " " + done);
            case NOT_FOUND -> Response.of(Status.NOT_FOUND, "Квартира с id " + id + " не найдена");
            case FORBIDDEN -> Response.of(Status.FORBIDDEN, "Квартира " + id + " принадлежит другому пользователю");
        };
    }

    private Response groupByHouse() {
        var counts = collection.countByHouse();
        if (counts.isEmpty()) {
            return Response.ok("Коллекция пуста");
        }
        String text = counts.entrySet().stream()
                .sorted(Comparator.comparing((java.util.Map.Entry<flats.common.model.House, Long> e) ->
                        e.getKey().name()).thenComparing(e -> e.getKey().year()))
                .map(e -> "Дом «" + e.getKey().name() + "», " + e.getKey().year() + " г., лифтов "
                        + e.getKey().numberOfLifts() + ": " + e.getValue())
                .collect(Collectors.joining("\n"));
        return Response.ok(text);
    }

    private Response filter(Request request) {
        String prefix = request.argument();
        if (prefix == null || prefix.isEmpty()) {
            return Response.error("Укажите начало названия");
        }
        List<Flat> found = collection.startingWith(prefix);
        return Response.ok(found.isEmpty() ? "Ничего не найдено" : "Найдено: " + found.size(), found);
    }

    private static FlatDraft element(Request request) {
        if (request.element() == null) {
            throw new IllegalArgumentException("К команде не приложен элемент");
        }
        return request.element();
    }

    private static Long parseId(String text) {
        try {
            long id = Long.parseLong(text == null ? "" : text.strip());
            return id > 0 ? id : null;
        } catch (NumberFormatException e) {
            return null;
        }
    }
}
