package flats.server.store;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNotEquals;
import static org.junit.Assert.assertNull;
import static org.junit.Assert.assertTrue;

import flats.common.TestData;
import flats.server.store.UserStore.UserRecord;
import java.util.List;
import org.junit.Test;

/**
 * Требования к любому хранилищу. Наследники подставляют реализацию: память или PostgreSQL.
 */
public abstract class StoreContract {
    protected abstract FlatStore flats();

    protected abstract UserStore users();

    private String owner(String login) {
        users().create(new UserRecord(login, "salt", "hash"));
        return login;
    }

    @Test
    public void insertAssignsIncreasingIds() {
        String anna = owner("anna");
        var first = flats().insert(anna, TestData.draft("a", 40, 2));
        var second = flats().insert(anna, TestData.draft("b", 50, 3));
        assertTrue(second.id() > first.id());
        assertEquals("anna", first.owner());
        assertEquals(first, flats().findById(first.id()).orElseThrow());
    }

    @Test
    public void roundTripKeepsAllFields() {
        String anna = owner("anna");
        var draft = TestData.draft("Лофт «Северный»", 45, 3);
        var saved = flats().insert(anna, draft);
        assertEquals(draft, flats().findById(saved.id()).orElseThrow().toDraft());
    }

    @Test
    public void absentAreaStaysAbsent() {
        String anna = owner("anna");
        var saved = flats().insert(anna, TestData.draft("a", null, 1));
        assertNull(flats().findById(saved.id()).orElseThrow().area());
    }

    @Test
    public void updateKeepsIdOwnerAndDate() {
        String anna = owner("anna");
        var saved = flats().insert(anna, TestData.draft("a", 40, 2));
        assertTrue(flats().update(saved.id(), TestData.draft("b", null, 5)));
        var after = flats().findById(saved.id()).orElseThrow();
        assertEquals("b", after.name());
        assertNull(after.area());
        assertEquals("anna", after.owner());
        assertEquals(saved.creationDate().toInstant().toEpochMilli(),
                after.creationDate().toInstant().toEpochMilli());
        assertFalse(flats().update(saved.id() + 1000, TestData.draft("c", 1, 1)));
    }

    @Test
    public void deleteAndDeleteAll() {
        String anna = owner("anna");
        var a = flats().insert(anna, TestData.draft("a", 1, 1));
        var b = flats().insert(anna, TestData.draft("b", 1, 1));
        var c = flats().insert(anna, TestData.draft("c", 1, 1));
        assertTrue(flats().delete(a.id()));
        assertFalse(flats().delete(a.id()));
        assertEquals(2, flats().deleteAll(List.of(b.id(), c.id(), 999_999L)));
        assertEquals(0, flats().deleteAll(List.of()));
        assertTrue(flats().findAll().isEmpty());
    }

    @Test
    public void usersAreUniqueByLogin() {
        assertTrue(users().create(new UserRecord("oleg", "s1", "h1")));
        assertFalse(users().create(new UserRecord("oleg", "s2", "h2")));
        assertEquals("s1", users().find("oleg").orElseThrow().salt());
        assertTrue(users().find("nobody").isEmpty());
        assertNotEquals(null, users().find("oleg"));
    }
}
