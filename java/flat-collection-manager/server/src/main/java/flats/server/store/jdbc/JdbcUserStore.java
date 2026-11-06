package flats.server.store.jdbc;

import flats.server.store.UserStore;

import java.sql.SQLException;
import java.util.Optional;

/**
 * Пользователи в таблице {@code users}.
 */
public final class JdbcUserStore implements UserStore {
    private final Database database;

    public JdbcUserStore(Database database) {
        this.database = database;
    }

    @Override
    public boolean create(UserRecord user) {
        String sql = "INSERT INTO users (login, salt, password_hash) VALUES (?, ?, ?) "
                + "ON CONFLICT (login) DO NOTHING";
        try (var connection = database.connection(); var ps = connection.prepareStatement(sql)) {
            ps.setString(1, user.login());
            ps.setString(2, user.salt());
            ps.setString(3, user.passwordHash());
            return ps.executeUpdate() == 1;
        } catch (SQLException e) {
            throw new StorageException("Не удалось создать пользователя", e);
        }
    }

    @Override
    public Optional<UserRecord> find(String login) {
        String sql = "SELECT login, salt, password_hash FROM users WHERE login = ?";
        try (var connection = database.connection(); var ps = connection.prepareStatement(sql)) {
            ps.setString(1, login);
            try (var rs = ps.executeQuery()) {
                return rs.next()
                        ? Optional.of(new UserRecord(rs.getString(1), rs.getString(2), rs.getString(3)))
                        : Optional.empty();
            }
        } catch (SQLException e) {
            throw new StorageException("Не удалось найти пользователя", e);
        }
    }
}
