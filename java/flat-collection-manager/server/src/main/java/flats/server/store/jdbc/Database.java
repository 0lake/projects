package flats.server.store.jdbc;

import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.charset.StandardCharsets;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

/**
 * Доступ к PostgreSQL. Каждая операция получает собственное соединение, а все запросы
 * выполняются через PreparedStatement.
 */
public final class Database {
    private final String url;
    private final String user;
    private final String password;

    public Database(String url, String user, String password) {
        this.url = url;
        this.user = user;
        this.password = password;
    }

    /**
     * Открывает новое соединение. Вызывающий обязан закрыть его.
     */
    public Connection connection() throws SQLException {
        return DriverManager.getConnection(url, user, password);
    }

    /**
     * Создаёт таблицы, если их ещё нет.
     */
    public void initSchema() {
        try (var in = Database.class.getResourceAsStream("/schema.sql")) {
            if (in == null) {
                throw new IllegalStateException("Не найден ресурс schema.sql");
            }
            String script = new String(in.readAllBytes(), StandardCharsets.UTF_8);
            try (var connection = connection(); var statement = connection.createStatement()) {
                statement.execute(script);
            }
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        } catch (SQLException e) {
            throw new StorageException("Не удалось создать схему базы данных", e);
        }
    }
}
