package flats.server.store.memory;

import flats.server.store.UserStore;

import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Хранилище пользователей в памяти для тестов и запуска без базы данных.
 */
public final class MemoryUserStore implements UserStore {
    private final Map<String, UserRecord> users = new ConcurrentHashMap<>();

    @Override
    public boolean create(UserRecord user) {
        return users.putIfAbsent(user.login(), user) == null;
    }

    @Override
    public Optional<UserRecord> find(String login) {
        return Optional.ofNullable(users.get(login));
    }
}
