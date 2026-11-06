package flats.server;

import flats.common.model.FlatDraft;
import flats.common.protocol.CommandType;
import flats.common.protocol.Request;
import flats.common.protocol.Response;
import flats.server.auth.AuthService;
import flats.server.auth.PasswordHasher;
import flats.server.collection.CollectionManager;
import flats.server.command.RequestProcessor;
import flats.server.store.FlatStore;
import flats.server.store.UserStore;
import flats.server.store.memory.MemoryFlatStore;
import flats.server.store.memory.MemoryUserStore;

/**
 * Собирает сервер без сети и базы данных для тестов.
 */
public final class ServerFixture {
    public final FlatStore flats;
    public final UserStore users;
    public final AuthService auth;
    public final CollectionManager collection;
    public final RequestProcessor processor;

    public ServerFixture() {
        this(new MemoryFlatStore(), new MemoryUserStore());
    }

    public ServerFixture(FlatStore flats, UserStore users) {
        this.flats = flats;
        this.users = users;
        this.auth = new AuthService(users, new PasswordHasher());
        this.collection = new CollectionManager(flats);
        this.processor = new RequestProcessor(auth, collection);
    }

    public Response register(String login, String password) {
        return processor.process(Request.of(login, password, CommandType.REGISTER));
    }

    public Response run(String login, String password, CommandType type) {
        return processor.process(Request.of(login, password, type));
    }

    public Response run(String login, String password, CommandType type, String argument, FlatDraft element) {
        return processor.process(new Request(login, password, type, argument, element));
    }
}
