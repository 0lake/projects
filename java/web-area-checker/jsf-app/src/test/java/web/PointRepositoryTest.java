package web;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

import area.CheckInput;
import area.CheckResult;
import java.time.Instant;
import java.util.List;
import java.util.UUID;
import org.junit.Assume;
import org.junit.Before;
import org.junit.Test;

/**
 * Интеграционный тест. Запускается только при заданных TEST_DB_URL, TEST_DB_USER, TEST_DB_PASSWORD,
 * иначе пропускается.
 */
public class PointRepositoryTest {
    private PointRepository repository;
    private final String session = UUID.randomUUID().toString();

    @Before
    public void setUp() {
        String url = System.getenv("TEST_DB_URL");
        Assume.assumeTrue("TEST_DB_URL не задан", url != null && !url.isBlank());
        repository = new PointRepository(url,
                System.getenv().getOrDefault("TEST_DB_USER", "postgres"),
                System.getenv().getOrDefault("TEST_DB_PASSWORD", ""));
        repository.init();
    }

    private static CheckResult result(double x, boolean hit) {
        return new CheckResult(new CheckInput(x, 0, 2), hit, Instant.now());
    }

    @Test
    public void savesAndReturnsNewestFirst() {
        repository.save(session, result(1, true));
        repository.save(session, result(2, false));
        List<CheckResult> rows = repository.latest(session, 10);
        assertEquals(2, rows.size());
        assertEquals(2.0, rows.get(0).x(), 0);
        assertTrue(rows.get(1).hit());
    }

    @Test
    public void respectsLimit() {
        for (int i = 0; i < 5; i++) {
            repository.save(session, result(i, true));
        }
        assertEquals(3, repository.latest(session, 3).size());
    }

    @Test
    public void sessionsAreIsolated() {
        repository.save(session, result(1, true));
        assertEquals(0, repository.latest(UUID.randomUUID().toString(), 10).size());
    }

    @Test
    public void clearRemovesOnlyOwnRows() {
        String other = UUID.randomUUID().toString();
        repository.save(session, result(1, true));
        repository.save(other, result(2, true));
        repository.clear(session);
        assertEquals(0, repository.latest(session, 10).size());
        assertEquals(1, repository.latest(other, 10).size());
        repository.clear(other);
    }
}
