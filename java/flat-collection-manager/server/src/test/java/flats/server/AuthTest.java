package flats.server;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNotEquals;
import static org.junit.Assert.assertTrue;

import flats.common.protocol.CommandType;
import flats.common.protocol.Status;
import flats.server.auth.AuthService.RegistrationResult;
import flats.server.auth.PasswordHasher;
import org.junit.Test;

public class AuthTest {
    private final ServerFixture server = new ServerFixture();

    @Test
    public void hashDependsOnSalt() {
        var hasher = new PasswordHasher();
        String a = hasher.newSalt();
        String b = hasher.newSalt();
        assertNotEquals(a, b);
        assertNotEquals(hasher.hash(a, "pass"), hasher.hash(b, "pass"));
        assertTrue(hasher.matches(a, "pass", hasher.hash(a, "pass")));
        assertFalse(hasher.matches(a, "other", hasher.hash(a, "pass")));
    }

    @Test
    public void passwordIsNotStoredInPlainText() {
        server.register("oleg", "secret1");
        var record = server.users.find("oleg").orElseThrow();
        assertFalse(record.passwordHash().contains("secret1"));
        assertEquals(40, record.passwordHash().length());
    }

    @Test
    public void registerThenAuthenticate() {
        assertEquals(RegistrationResult.CREATED, server.auth.register("oleg", "secret1"));
        assertTrue(server.auth.authenticate("oleg", "secret1"));
        assertFalse(server.auth.authenticate("oleg", "wrong"));
        assertFalse(server.auth.authenticate("nobody", "secret1"));
        assertFalse(server.auth.authenticate(null, null));
    }

    @Test
    public void duplicateLoginIsRejected() {
        server.register("oleg", "secret1");
        assertEquals(RegistrationResult.LOGIN_TAKEN, server.auth.register("oleg", "other11"));
    }

    @Test
    public void invalidCredentialsAreRejectedOnRegistration() {
        assertEquals(RegistrationResult.INVALID_LOGIN, server.auth.register("a b", "secret1"));
        assertEquals(RegistrationResult.INVALID_LOGIN, server.auth.register("ab", "secret1"));
        assertEquals(RegistrationResult.INVALID_LOGIN, server.auth.register("x'; DROP TABLE users;--", "secret1"));
        assertEquals(RegistrationResult.INVALID_PASSWORD, server.auth.register("oleg", "abc"));
    }

    @Test
    public void commandsRequireValidCredentials() {
        server.register("oleg", "secret1");
        assertEquals(Status.AUTH_REQUIRED, server.run("oleg", "wrong", CommandType.SHOW).status());
        assertEquals(Status.AUTH_REQUIRED, server.run(null, null, CommandType.SHOW).status());
        assertEquals(Status.OK, server.run("oleg", "secret1", CommandType.LOGIN).status());
    }
}
