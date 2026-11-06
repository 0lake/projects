package flats.server.store;

import static org.junit.Assume.assumeNotNull;

import flats.server.store.jdbc.Database;
import flats.server.store.jdbc.JdbcFlatStore;
import flats.server.store.jdbc.JdbcUserStore;
import java.sql.SQLException;
import org.junit.Before;

/**
 * Те же требования на настоящем PostgreSQL. Тест пропускается, если не задан TEST_DB_URL,
 * например {@code jdbc:postgresql://localhost:5432/flats}; пользователь и пароль берутся из
 * TEST_DB_USER и TEST_DB_PASSWORD. Таблицы очищаются перед каждым тестом.
 */
public class JdbcStoreTest extends StoreContract {
    private Database database;
    private FlatStore flats;
    private UserStore users;

    @Before
    public void connect() throws SQLException {
        String url = System.getenv("TEST_DB_URL");
        assumeNotNull(url);
        database = new Database(url, System.getenv().getOrDefault("TEST_DB_USER", "flats"),
                System.getenv().getOrDefault("TEST_DB_PASSWORD", "flats"));
        database.initSchema();
        try (var connection = database.connection(); var statement = connection.createStatement()) {
            statement.execute("TRUNCATE flats, users");
        }
        flats = new JdbcFlatStore(database);
        users = new JdbcUserStore(database);
    }

    @Override
    protected FlatStore flats() {
        return flats;
    }

    @Override
    protected UserStore users() {
        return users;
    }
}
