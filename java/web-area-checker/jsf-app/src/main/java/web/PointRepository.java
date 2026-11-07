package web;

import area.CheckInput;
import area.CheckResult;
import jakarta.annotation.PostConstruct;
import jakarta.enterprise.context.ApplicationScoped;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;

/**
 * Хранилище точек в PostgreSQL. Параметры подключения берутся из переменных окружения
 * {@code AREA_DB_URL}, {@code AREA_DB_USER} и {@code AREA_DB_PASSWORD}, в коде их нет.
 * Для каждого запроса открывается короткое соединение: нагрузка небольшая, а пул здесь только усложнил бы проект.
 */
@ApplicationScoped
public class PointRepository {
    static final String DEFAULT_URL = "jdbc:postgresql://localhost:5432/area";

    private final String url;
    private final String user;
    private final String password;

    public PointRepository() {
        this(env("AREA_DB_URL", DEFAULT_URL), env("AREA_DB_USER", "area"), env("AREA_DB_PASSWORD", ""));
    }

    public PointRepository(String url, String user, String password) {
        this.url = url;
        this.user = user;
        this.password = password;
    }

    /** Создаёт таблицу при первом запуске. */
    @PostConstruct
    public void init() {
        try (Connection c = open(); Statement st = c.createStatement()) {
            st.execute(readSchema());
        } catch (SQLException | IOException e) {
            throw new IllegalStateException("Не удалось подготовить базу данных: " + e.getMessage(), e);
        }
    }

    /** Сохраняет результат проверки, привязывая его к сессии. */
    public void save(String sessionId, CheckResult result) {
        String sql = "INSERT INTO points (session_id, x, y, r, hit, checked_at) VALUES (?, ?, ?, ?, ?, ?)";
        try (Connection c = open(); PreparedStatement ps = c.prepareStatement(sql)) {
            ps.setString(1, sessionId);
            ps.setDouble(2, result.x());
            ps.setDouble(3, result.y());
            ps.setDouble(4, result.r());
            ps.setBoolean(5, result.hit());
            ps.setObject(6, result.checkedAt().atOffset(java.time.ZoneOffset.UTC));
            ps.executeUpdate();
        } catch (SQLException e) {
            throw new IllegalStateException("Не удалось сохранить точку", e);
        }
    }

    /** @return последние точки сессии, новые первыми */
    public List<CheckResult> latest(String sessionId, int limit) {
        String sql = "SELECT x, y, r, hit, checked_at FROM points WHERE session_id = ? ORDER BY id DESC LIMIT ?";
        List<CheckResult> out = new ArrayList<>();
        try (Connection c = open(); PreparedStatement ps = c.prepareStatement(sql)) {
            ps.setString(1, sessionId);
            ps.setInt(2, limit);
            try (ResultSet rs = ps.executeQuery()) {
                while (rs.next()) {
                    out.add(new CheckResult(
                            new CheckInput(rs.getDouble("x"), rs.getDouble("y"), rs.getDouble("r")),
                            rs.getBoolean("hit"),
                            rs.getObject("checked_at", java.time.OffsetDateTime.class).toInstant()));
                }
            }
        } catch (SQLException e) {
            throw new IllegalStateException("Не удалось прочитать историю", e);
        }
        return out;
    }

    /** Удаляет все точки сессии. */
    public void clear(String sessionId) {
        try (Connection c = open(); PreparedStatement ps = c.prepareStatement("DELETE FROM points WHERE session_id = ?")) {
            ps.setString(1, sessionId);
            ps.executeUpdate();
        } catch (SQLException e) {
            throw new IllegalStateException("Не удалось очистить историю", e);
        }
    }

    private Connection open() throws SQLException {
        return DriverManager.getConnection(url, user, password);
    }

    private static String readSchema() throws IOException {
        try (InputStream in = PointRepository.class.getResourceAsStream("/db/schema.sql")) {
            if (in == null) {
                throw new IOException("db/schema.sql не найден");
            }
            return new String(in.readAllBytes(), StandardCharsets.UTF_8);
        }
    }

    private static String env(String name, String fallback) {
        String value = System.getenv(name);
        return value == null || value.isBlank() ? fallback : value;
    }
}
