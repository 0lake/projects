package flats.common.model;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNull;
import static org.junit.Assert.assertTrue;
import static org.junit.Assert.fail;

import flats.common.TestData;
import java.time.ZonedDateTime;
import org.junit.Test;

public class ModelTest {
    @Test
    public void nameIsStripped() {
        assertEquals("Лофт", TestData.draft("  Лофт ", 40, 2).name());
    }

    @Test
    public void rejectsBlankName() {
        assertInvalid(() -> TestData.draft("   ", 40, 2));
    }

    @Test
    public void rejectsNonPositiveNumbers() {
        assertInvalid(() -> TestData.draft("a", 0, 2));
        assertInvalid(() -> TestData.draft("a", 40, 0));
        assertInvalid(() -> new House("h", 0, 1L, 1));
        assertInvalid(() -> new House("h", 2000, 1L, 0));
    }

    @Test
    public void areaMayBeAbsent() {
        assertNull(TestData.draft("a", null, 1).area());
    }

    @Test
    public void coordinateYMustExceedLimit() {
        assertInvalid(() -> new Coordinates(1L, -519f));
        assertEquals(-518.9f, new Coordinates(1L, -518.9f).y(), 0f);
    }

    @Test
    public void flatKeepsDraftValues() {
        var draft = TestData.draft("a", 40, 2);
        var flat = Flat.of(7, ZonedDateTime.now(), "oleg", draft);
        assertEquals(draft, flat.toDraft());
        var updated = flat.withDraft(TestData.draft("b", 50, 3));
        assertEquals(7, updated.id());
        assertEquals("oleg", updated.owner());
        assertEquals(flat.creationDate(), updated.creationDate());
        assertEquals("b", updated.name());
    }

    @Test
    public void orderingByAreaRoomsNameThenId() {
        var now = ZonedDateTime.now();
        var small = Flat.of(2, now, "u", TestData.draft("z", 30, 1));
        var big = Flat.of(1, now, "u", TestData.draft("a", 80, 1));
        var twin = Flat.of(3, now, "u", TestData.draft("z", 30, 1));
        assertTrue(small.compareTo(big) < 0);
        assertTrue(small.compareTo(twin) < 0);
        assertTrue(twin.compareTo(small) > 0);
    }

    @Test
    public void missingAreaSortsFirst() {
        assertTrue(FlatDraft.VALUE_ORDER.compare(TestData.draft("a", null, 1), TestData.draft("a", 1, 1)) < 0);
    }

    private static void assertInvalid(Runnable action) {
        try {
            action.run();
            fail("Ожидалось ValidationException");
        } catch (ValidationException expected) {
            // ожидаемо
        }
    }
}
