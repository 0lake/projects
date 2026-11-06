package flats.server.store;

import java.util.Optional;

/**
 * Хранилище учётных записей. Реализации обязаны быть потокобезопасными.
 */
public interface UserStore {
    /**
     * Учётная запись: логин, соль и хеш пароля.
     */
    record UserRecord(String login, String salt, String passwordHash) {
    }

    /**
     * Создаёт пользователя, если логина ещё нет.
     *
     * @return true, если пользователь создан; false, если логин занят
     */
    boolean create(UserRecord user);

    /** @return пользователь с заданным логином, если есть */
    Optional<UserRecord> find(String login);
}
