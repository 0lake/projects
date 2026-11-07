package area;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;
import static org.junit.Assert.fail;

import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import org.junit.Test;

public class CheckerTest {
    private final Clock clock = Clock.fixed(Instant.parse("2025-01-01T10:00:00Z"), ZoneOffset.UTC);
    private final Checker checker = new Checker(new CircleTriangleSquare(), clock);

    @Test
    public void acceptsCommaAsSeparator() throws Exception {
        CheckInput in = checker.parse("-1,5", "0,5", "2");
        assertEquals(-1.5, in.x(), 0);
        assertEquals(0.5, in.y(), 0);
    }

    @Test
    public void hitIsRecordedWithTime() throws Exception {
        CheckResult r = checker.check("0", "0", "2");
        assertTrue(r.hit());
        assertEquals(Instant.parse("2025-01-01T10:00:00Z"), r.checkedAt());
    }

    @Test
    public void missIsRecorded() throws Exception {
        assertFalse(checker.check("4", "-4", "2").hit());
    }

    @Test
    public void boundaryValuesOfRangesAreAllowed() throws Exception {
        checker.parse("-5", "-5", "1");
        checker.parse("5", "3", "3");
    }

    @Test
    public void outOfRangeReportsEveryProblem() {
        try {
            checker.parse("6", "4", "7");
            fail();
        } catch (InvalidInputException e) {
            assertEquals(3, e.problems().size());
        }
    }

    @Test
    public void rejectsGarbage() {
        for (String bad : new String[] {"abc", "", "  ", null, "NaN", "Infinity", "1e999", "1.2.3"}) {
            try {
                checker.parse(bad, "0", "2");
                fail("accepted: " + bad);
            } catch (InvalidInputException expected) {
                assertEquals(1, expected.problems().size());
            }
        }
    }

    @Test
    public void rejectsRadiusOutsideAllowedSet() {
        for (String r : new String[] {"0", "0.5", "1.7", "3.5", "-2"}) {
            try {
                checker.parse("0", "0", r);
                fail("accepted R=" + r);
            } catch (InvalidInputException expected) {
                // ok
            }
        }
    }

    @Test
    public void rejectsVeryLongNumber() {
        try {
            checker.parse("0." + "0".repeat(50) + "1", "0", "2");
            fail();
        } catch (InvalidInputException e) {
            assertTrue(e.getMessage().contains("длинный"));
        }
    }
}
