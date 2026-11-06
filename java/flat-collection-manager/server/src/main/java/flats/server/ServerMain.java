package flats.server;

import flats.server.auth.AuthService;
import flats.server.auth.PasswordHasher;
import flats.server.collection.CollectionManager;
import flats.server.command.RequestProcessor;
import flats.server.net.Server;
import flats.server.store.FlatStore;
import flats.server.store.UserStore;
import flats.server.store.jdbc.Database;
import flats.server.store.jdbc.JdbcFlatStore;
import flats.server.store.jdbc.JdbcUserStore;
import flats.server.store.memory.MemoryFlatStore;
import flats.server.store.memory.MemoryUserStore;

/**
 * Точка входа сервера.
 */
public final class ServerMain {
    private static final System.Logger LOG = System.getLogger(ServerMain.class.getName());

    private ServerMain() {
    }

    public static void main(String[] args) throws Exception {
        ServerConfig config = ServerConfig.fromEnvironment(System.getenv());

        FlatStore flats;
        UserStore users;
        if (config.usesDatabase()) {
            var database = new Database(config.dbUrl(), config.dbUser(), config.dbPassword());
            database.initSchema();
            flats = new JdbcFlatStore(database);
            users = new JdbcUserStore(database);
            LOG.log(System.Logger.Level.INFO, "Хранилище: PostgreSQL");
        } else {
            flats = new MemoryFlatStore();
            users = new MemoryUserStore();
            LOG.log(System.Logger.Level.WARNING, "FLATS_DB_URL не задан, данные хранятся в памяти и пропадут при остановке");
        }

        var processor = new RequestProcessor(new AuthService(users, new PasswordHasher()), new CollectionManager(flats));
        var server = new Server(config.port(), processor, config.readThreads(), config.workThreads());
        Runtime.getRuntime().addShutdownHook(new Thread(server::close, "shutdown"));
        server.start();
        server.await();
    }
}
