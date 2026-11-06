package flats.server.store;

import flats.server.store.memory.MemoryFlatStore;
import flats.server.store.memory.MemoryUserStore;

public class MemoryStoreTest extends StoreContract {
    private final FlatStore flats = new MemoryFlatStore();
    private final UserStore users = new MemoryUserStore();

    @Override
    protected FlatStore flats() {
        return flats;
    }

    @Override
    protected UserStore users() {
        return users;
    }
}
