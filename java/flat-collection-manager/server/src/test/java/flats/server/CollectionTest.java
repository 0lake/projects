package flats.server;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

import flats.common.TestData;
import flats.common.model.Flat;
import flats.common.protocol.CommandType;
import flats.common.protocol.Status;
import java.util.List;
import org.junit.Before;
import org.junit.Test;

public class CollectionTest {
    private static final String PASS = "secret1";
    private final ServerFixture s = new ServerFixture();

    @Before
    public void users() {
        s.register("anna", PASS);
        s.register("boris", PASS);
    }

    private long add(String user, String name, Integer area, int rooms) {
        var response = s.run(user, PASS, CommandType.ADD, null, TestData.draft(name, area, rooms));
        assertEquals(response.message(), Status.OK, response.status());
        return s.collection.sortedByName().stream().filter(f -> f.name().equals(name)).findFirst().orElseThrow().id();
    }

    @Test
    public void showIsSortedByName() {
        add("anna", "Яблоко", 50, 2);
        add("boris", "Арбуз", 60, 3);
        add("anna", "Мандарин", 40, 1);
        List<Flat> shown = s.run("anna", PASS, CommandType.SHOW).flats();
        assertEquals(List.of("Арбуз", "Мандарин", "Яблоко"), shown.stream().map(Flat::name).toList());
    }

    @Test
    public void ownerIsTakenFromCredentialsNotFromRequest() {
        long id = add("anna", "a", 50, 2);
        assertEquals("anna", s.flats.findById(id).orElseThrow().owner());
    }

    @Test
    public void updateOnlyOwnElement() {
        long id = add("anna", "a", 50, 2);
        var foreign = s.run("boris", PASS, CommandType.UPDATE, String.valueOf(id), TestData.draft("hack", 1, 1));
        assertEquals(Status.FORBIDDEN, foreign.status());
        assertEquals("a", s.flats.findById(id).orElseThrow().name());

        var own = s.run("anna", PASS, CommandType.UPDATE, String.valueOf(id), TestData.draft("b", 70, 3));
        assertEquals(Status.OK, own.status());
        var stored = s.flats.findById(id).orElseThrow();
        assertEquals("b", stored.name());
        assertEquals("anna", stored.owner());
        assertEquals("b", s.collection.sortedByName().get(0).name());
    }

    @Test
    public void removeOnlyOwnElement() {
        long id = add("anna", "a", 50, 2);
        assertEquals(Status.FORBIDDEN, s.run("boris", PASS, CommandType.REMOVE_BY_ID, String.valueOf(id), null).status());
        assertEquals(1, s.collection.size());
        assertEquals(Status.OK, s.run("anna", PASS, CommandType.REMOVE_BY_ID, String.valueOf(id), null).status());
        assertEquals(0, s.collection.size());
        assertEquals(Status.NOT_FOUND, s.run("anna", PASS, CommandType.REMOVE_BY_ID, String.valueOf(id), null).status());
    }

    @Test
    public void badIdIsReportedNotThrown() {
        assertEquals(Status.ERROR, s.run("anna", PASS, CommandType.REMOVE_BY_ID, "abc", null).status());
        assertEquals(Status.ERROR, s.run("anna", PASS, CommandType.REMOVE_BY_ID, "-5", null).status());
        assertEquals(Status.ERROR, s.run("anna", PASS, CommandType.ADD).status());
    }

    @Test
    public void clearRemovesOnlyOwn() {
        add("anna", "a1", 50, 2);
        add("anna", "a2", 50, 2);
        add("boris", "b1", 50, 2);
        s.run("anna", PASS, CommandType.CLEAR);
        assertEquals(List.of("b1"), s.collection.sortedByName().stream().map(Flat::name).toList());
        assertEquals(1, s.flats.findAll().size());
    }

    @Test
    public void addIfMin() {
        add("anna", "mid", 50, 2);
        assertTrue(s.run("anna", PASS, CommandType.ADD_IF_MIN, null, TestData.draft("big", 90, 2)).message().contains("не добавлен"));
        assertEquals(1, s.collection.size());
        assertTrue(s.run("anna", PASS, CommandType.ADD_IF_MIN, null, TestData.draft("small", 20, 1)).message().contains("добавлена"));
        assertEquals(2, s.collection.size());
    }

    @Test
    public void addIfMinOnEmptyCollectionAdds() {
        s.run("anna", PASS, CommandType.ADD_IF_MIN, null, TestData.draft("first", 20, 1));
        assertEquals(1, s.collection.size());
    }

    @Test
    public void removeGreaterAndLowerTouchOnlyOwn() {
        add("anna", "small", 20, 1);
        add("anna", "mid", 50, 2);
        add("anna", "big", 90, 3);
        add("boris", "boris-big", 95, 3);
        s.run("anna", PASS, CommandType.REMOVE_GREATER, null, TestData.draft("mid", 50, 2));
        assertEquals(List.of("boris-big", "mid", "small"), names());
        s.run("anna", PASS, CommandType.REMOVE_LOWER, null, TestData.draft("mid", 50, 2));
        assertEquals(List.of("boris-big", "mid"), names());
    }

    @Test
    public void aggregates() {
        add("anna", "a", 20, 1);
        add("boris", "b", 30, 1);
        assertEquals("Сумма высот: 6", s.run("anna", PASS, CommandType.SUM_OF_HEIGHT).message());
        assertTrue(s.run("anna", PASS, CommandType.GROUP_COUNTING_BY_HOUSE).message().endsWith(": 2"));
        assertEquals(1, s.run("anna", PASS, CommandType.FILTER_STARTS_WITH_NAME, "b", null).flats().size());
        assertEquals("Ничего не найдено", s.run("anna", PASS, CommandType.FILTER_STARTS_WITH_NAME, "zzz", null).message());
        assertTrue(s.run("anna", PASS, CommandType.INFO).message().contains("Количество элементов: 2"));
    }

    @Test
    public void collectionIsLoadedFromStoreOnStart() {
        add("anna", "kept", 20, 1);
        var restarted = new ServerFixture(s.flats, s.users);
        assertEquals(1, restarted.collection.size());
        assertEquals(Status.OK, restarted.run("anna", PASS, CommandType.SHOW).status());
    }

    @Test
    public void clientSideCommandsAreNotExecutedOnServer() {
        assertEquals(Status.ERROR, s.run("anna", PASS, CommandType.EXIT).status());
    }

    private List<String> names() {
        return s.collection.sortedByName().stream().map(Flat::name).toList();
    }
}
