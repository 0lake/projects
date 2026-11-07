package web;

import static org.junit.Assert.assertEquals;

import area.CheckInput;
import area.CheckResult;
import java.time.Instant;
import java.util.List;
import org.junit.Test;

public class AreaBeanJsonTest {
    private static CheckResult result(double x, double y, double r, boolean hit) {
        return new CheckResult(new CheckInput(x, y, r), hit, Instant.EPOCH);
    }

    @Test
    public void emptyHistoryIsEmptyArray() {
        assertEquals("[]", AreaBean.toJson(List.of()));
    }

    @Test
    public void serializesNumbersWithDotRegardlessOfLocale() {
        java.util.Locale previous = java.util.Locale.getDefault();
        java.util.Locale.setDefault(java.util.Locale.forLanguageTag("ru-RU"));
        try {
            assertEquals("[{\"x\":-1.5,\"y\":0.5,\"r\":2.0,\"hit\":true}]",
                    AreaBean.toJson(List.of(result(-1.5, 0.5, 2, true))));
        } finally {
            java.util.Locale.setDefault(previous);
        }
    }

    @Test
    public void separatesItemsWithComma() {
        assertEquals("[{\"x\":0.0,\"y\":0.0,\"r\":1.0,\"hit\":true},{\"x\":3.0,\"y\":3.0,\"r\":1.0,\"hit\":false}]",
                AreaBean.toJson(List.of(result(0, 0, 1, true), result(3, 3, 1, false))));
    }
}
