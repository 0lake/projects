package flats.server.auth;

import flats.server.store.UserStore;
import flats.server.store.UserStore.UserRecord;

import java.util.regex.Pattern;

/**
 * Регистрация и проверка пользователей.
 */
public final class AuthService {
    /** Результат регистрации. */
    public enum RegistrationResult { CREATED, LOGIN_TAKEN, INVALID_LOGIN, INVALID_PASSWORD }

    private static final Pattern LOGIN = Pattern.compile("[A-Za-z0-9_.-]{3,32}");
    private static final int MIN_PASSWORD = 4;
    private static final int MAX_PASSWORD = 128;

    private final UserStore users;
    private final PasswordHasher hasher;

    public AuthService(UserStore users, PasswordHasher hasher) {
        this.users = users;
        this.hasher = hasher;
    }

    /**
     * Регистрирует пользователя.
     */
    public RegistrationResult register(String login, String password) {
        if (login == null || !LOGIN.matcher(login).matches()) {
            return RegistrationResult.INVALID_LOGIN;
        }
        if (password == null || password.length() < MIN_PASSWORD || password.length() > MAX_PASSWORD) {
            return RegistrationResult.INVALID_PASSWORD;
        }
        String salt = hasher.newSalt();
        var record = new UserRecord(login, salt, hasher.hash(salt, password));
        return users.create(record) ? RegistrationResult.CREATED : RegistrationResult.LOGIN_TAKEN;
    }

    /**
     * @return true, если пользователь существует и пароль верен
     */
    public boolean authenticate(String login, String password) {
        if (login == null || password == null) {
            return false;
        }
        return users.find(login)
                .map(user -> hasher.matches(user.salt(), password, user.passwordHash()))
                .orElse(false);
    }
}
