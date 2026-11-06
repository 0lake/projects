package flats.server.collection;

import flats.common.model.Flat;
import flats.common.model.FlatDraft;
import flats.common.model.House;
import flats.server.store.FlatStore;

import java.time.ZonedDateTime;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.PriorityQueue;
import java.util.concurrent.locks.ReadWriteLock;
import java.util.concurrent.locks.ReentrantReadWriteLock;
import java.util.function.Predicate;
import java.util.stream.Collectors;

/**
 * Коллекция квартир в памяти поверх постоянного хранилища.
 *
 * <p>Изменения сначала записываются в хранилище и только после успеха попадают в очередь
 * с приоритетом, поэтому память и база не расходятся. Доступ к очереди защищён
 * блокировкой чтения и записи: просмотры идут параллельно, изменения исключают друг друга.
 * Права на изменение (только своих элементов) проверяются здесь, в одном месте.
 */
public final class CollectionManager {
    /** Результат операции над конкретным элементом. */
    public enum Outcome { OK, NOT_FOUND, FORBIDDEN }

    private static final Comparator<Flat> BY_NAME = Comparator.comparing(Flat::name).thenComparingLong(Flat::id);

    private final FlatStore store;
    private final PriorityQueue<Flat> queue = new PriorityQueue<>();
    private final ReadWriteLock lock = new ReentrantReadWriteLock();
    private final ZonedDateTime initializedAt = ZonedDateTime.now();

    /**
     * Загружает коллекцию из хранилища.
     */
    public CollectionManager(FlatStore store) {
        this.store = store;
        queue.addAll(store.findAll());
    }

    /** @return дата инициализации коллекции */
    public ZonedDateTime initializedAt() {
        return initializedAt;
    }

    /** @return количество элементов */
    public int size() {
        return read(queue::size);
    }

    /** @return все элементы, отсортированные по названию */
    public List<Flat> sortedByName() {
        return read(() -> queue.stream().sorted(BY_NAME).toList());
    }

    /** @return элементы, название которых начинается с заданной подстроки, по названию */
    public List<Flat> startingWith(String prefix) {
        return read(() -> queue.stream().filter(f -> f.name().startsWith(prefix)).sorted(BY_NAME).toList());
    }

    /** @return сумма высот потолков всех элементов */
    public long sumOfHeight() {
        return read(() -> queue.stream().mapToLong(Flat::height).sum());
    }

    /** @return количество элементов в каждом доме */
    public Map<House, Long> countByHouse() {
        return read(() -> queue.stream().collect(Collectors.groupingBy(Flat::house, Collectors.counting())));
    }

    /**
     * Добавляет элемент.
     */
    public Flat add(String owner, FlatDraft draft) {
        return write(() -> {
            Flat saved = store.insert(owner, draft);
            queue.add(saved);
            return saved;
        });
    }

    /**
     * Добавляет элемент, если он меньше наименьшего в коллекции или коллекция пуста.
     *
     * @return добавленный элемент или пустой Optional
     */
    public Optional<Flat> addIfMin(String owner, FlatDraft draft) {
        return write(() -> {
            Flat min = queue.peek();
            if (min != null && FlatDraft.VALUE_ORDER.compare(draft, min.toDraft()) >= 0) {
                return Optional.<Flat>empty();
            }
            Flat saved = store.insert(owner, draft);
            queue.add(saved);
            return Optional.of(saved);
        });
    }

    /**
     * Заменяет значения полей своего элемента.
     */
    public Outcome update(long id, String owner, FlatDraft draft) {
        return write(() -> {
            Flat current = find(id);
            if (current == null) {
                return Outcome.NOT_FOUND;
            }
            if (!current.owner().equals(owner)) {
                return Outcome.FORBIDDEN;
            }
            if (!store.update(id, draft)) {
                return Outcome.NOT_FOUND;
            }
            queue.remove(current);
            queue.add(current.withDraft(draft));
            return Outcome.OK;
        });
    }

    /**
     * Удаляет свой элемент по id.
     */
    public Outcome remove(long id, String owner) {
        return write(() -> {
            Flat current = find(id);
            if (current == null) {
                return Outcome.NOT_FOUND;
            }
            if (!current.owner().equals(owner)) {
                return Outcome.FORBIDDEN;
            }
            store.delete(id);
            queue.remove(current);
            return Outcome.OK;
        });
    }

    /**
     * Удаляет все элементы пользователя.
     *
     * @return количество удалённых
     */
    public int clear(String owner) {
        return removeIf(f -> f.owner().equals(owner));
    }

    /**
     * Удаляет элементы пользователя, большие заданного.
     *
     * @return количество удалённых
     */
    public int removeGreater(String owner, FlatDraft draft) {
        return removeIf(f -> f.owner().equals(owner) && FlatDraft.VALUE_ORDER.compare(f.toDraft(), draft) > 0);
    }

    /**
     * Удаляет элементы пользователя, меньшие заданного.
     *
     * @return количество удалённых
     */
    public int removeLower(String owner, FlatDraft draft) {
        return removeIf(f -> f.owner().equals(owner) && FlatDraft.VALUE_ORDER.compare(f.toDraft(), draft) < 0);
    }

    private int removeIf(Predicate<Flat> condition) {
        return write(() -> {
            List<Flat> victims = queue.stream().filter(condition).toList();
            if (victims.isEmpty()) {
                return 0;
            }
            int deleted = store.deleteAll(victims.stream().map(Flat::id).toList());
            queue.removeAll(victims);
            return deleted;
        });
    }

    /** Поиск по id; вызывать под блокировкой. */
    private Flat find(long id) {
        return queue.stream().filter(f -> f.id() == id).findFirst().orElse(null);
    }

    private <T> T read(java.util.function.Supplier<T> action) {
        lock.readLock().lock();
        try {
            return action.get();
        } finally {
            lock.readLock().unlock();
        }
    }

    private <T> T write(java.util.function.Supplier<T> action) {
        lock.writeLock().lock();
        try {
            return action.get();
        } finally {
            lock.writeLock().unlock();
        }
    }
}
