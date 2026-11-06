package flats.server.auth;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.util.HexFormat;

/**
 * Хеширование паролей: SHA-1 от соли и пароля.
 *
 * <p>SHA-1 выбран по требованию задания. Для реального сервиса нужен медленный
 * алгоритм с настраиваемой стоимостью (bcrypt, scrypt, Argon2), поэтому алгоритм изолирован
 * в этом классе и заменяется без изменения остального кода.
 */
public final class PasswordHasher {
    private static final int SALT_BYTES = 16;
    private final SecureRandom random = new SecureRandom();

    /** @return новая случайная соль в виде hex-строки */
    public String newSalt() {
        byte[] salt = new byte[SALT_BYTES];
        random.nextBytes(salt);
        return HexFormat.of().formatHex(salt);
    }

    /** @return hex-строка SHA-1 от соли и пароля */
    public String hash(String salt, String password) {
        try {
            var digest = MessageDigest.getInstance("SHA-1");
            digest.update(salt.getBytes(StandardCharsets.UTF_8));
            digest.update(password.getBytes(StandardCharsets.UTF_8));
            return HexFormat.of().formatHex(digest.digest());
        } catch (NoSuchAlgorithmException e) {
            throw new IllegalStateException("SHA-1 недоступен в этой JVM", e);
        }
    }

    /** @return true, если пароль даёт заданный хеш; сравнение за постоянное время */
    public boolean matches(String salt, String password, String expectedHash) {
        byte[] actual = hash(salt, password).getBytes(StandardCharsets.UTF_8);
        return MessageDigest.isEqual(actual, expectedHash.getBytes(StandardCharsets.UTF_8));
    }
}
