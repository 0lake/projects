package flats.server;

import java.util.Map;

/**
 * Настройки сервера. Берутся из переменных окружения, значения по умолчанию подходят
 * для локального запуска.
 *
 * @param port        порт TCP
 * @param dbUrl       JDBC URL; если пуст, используется хранилище в памяти
 * @param dbUser      пользователь базы данных
 * @param dbPassword  пароль базы данных
 * @param readThreads потоков чтения запросов
 * @param workThreads потоков обработки запросов
 */
public record ServerConfig(int port, String dbUrl, String dbUser, String dbPassword,
                           int readThreads, int workThreads) {

    /** @return true, если задана база данных */
    public boolean usesDatabase() {
        return dbUrl != null && !dbUrl.isBlank();
    }

    /**
     * Читает настройки из переменных окружения FLATS_PORT, FLATS_DB_URL, FLATS_DB_USER,
     * FLATS_DB_PASSWORD, FLATS_READ_THREADS, FLATS_WORK_THREADS.
     */
    public static ServerConfig fromEnvironment(Map<String, String> env) {
        int cpus = Runtime.getRuntime().availableProcessors();
        return new ServerConfig(
                intValue(env, "FLATS_PORT", 5555),
                env.getOrDefault("FLATS_DB_URL", ""),
                env.getOrDefault("FLATS_DB_USER", "flats"),
                env.getOrDefault("FLATS_DB_PASSWORD", ""),
                intValue(env, "FLATS_READ_THREADS", Math.max(2, cpus)),
                intValue(env, "FLATS_WORK_THREADS", Math.max(2, cpus)));
    }

    private static int intValue(Map<String, String> env, String key, int fallback) {
        String value = env.get(key);
        if (value == null || value.isBlank()) {
            return fallback;
        }
        try {
            int parsed = Integer.parseInt(value.strip());
            if (parsed <= 0) {
                throw new IllegalArgumentException(key + " должен быть положительным");
            }
            return parsed;
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException(key + " должен быть целым числом: " + value, e);
        }
    }
}
