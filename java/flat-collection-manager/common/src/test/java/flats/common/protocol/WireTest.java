package flats.common.protocol;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;
import static org.junit.Assert.fail;

import flats.common.TestData;
import flats.common.model.Flat;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.ObjectOutputStream;
import java.time.ZonedDateTime;
import java.util.List;
import org.junit.Test;

public class WireTest {
    @Test
    public void requestRoundTrip() throws IOException {
        var request = new Request("oleg", "secret", CommandType.ADD, null, TestData.draft("a", 40, 2));
        var copy = Wire.decode(Wire.encode(request), Request.class, Wire.MAX_REQUEST_BYTES);
        assertEquals(request, copy);
    }

    @Test
    public void responseRoundTripKeepsFlats() throws IOException {
        var flat = Flat.of(1, ZonedDateTime.now(), "oleg", TestData.draft("a", 40, 2));
        var response = Response.ok("готово", List.of(flat));
        var copy = Wire.decode(Wire.encode(response), Response.class, Wire.MAX_RESPONSE_BYTES);
        assertEquals(response, copy);
    }

    @Test
    public void toStringHidesPassword() {
        var text = Request.of("oleg", "secret", CommandType.INFO).toString();
        assertFalse(text.contains("secret"));
    }

    @Test
    public void rejectsClassOutsideWhitelist() throws IOException {
        var bytes = new ByteArrayOutputStream();
        try (var out = new ObjectOutputStream(bytes)) {
            out.writeObject(new java.util.concurrent.atomic.AtomicLong(5));
        }
        try {
            Wire.decode(bytes.toByteArray(), Request.class, Wire.MAX_REQUEST_BYTES);
            fail("Класс вне белого списка должен быть отклонён");
        } catch (IOException expected) {
            assertTrue(true);
        }
    }

    @Test
    public void rejectsWrongType() throws IOException {
        byte[] payload = Wire.encode(Response.ok("x"));
        try {
            Wire.decode(payload, Request.class, Wire.MAX_RESPONSE_BYTES);
            fail("Ожидалась ошибка типа");
        } catch (IOException expected) {
            assertTrue(true);
        }
    }

    @Test
    public void rejectsOversizedPayload() {
        try {
            Wire.decode(new byte[Wire.MAX_REQUEST_BYTES + 1], Request.class, Wire.MAX_REQUEST_BYTES);
            fail("Ожидалась ошибка размера");
        } catch (IOException expected) {
            assertTrue(true);
        }
    }

    @Test
    public void commandTableIsConsistent() {
        for (CommandType type : CommandType.values()) {
            assertEquals(type, CommandType.byName(type.commandName()).orElseThrow());
            assertFalse(type.description().isBlank());
        }
        assertTrue(CommandType.byName("nope").isEmpty());
        assertEquals("update <id> {element}", CommandType.UPDATE.usage());
    }
}
