package flats.server.store.jdbc;

import flats.common.model.Coordinates;
import flats.common.model.Flat;
import flats.common.model.FlatDraft;
import flats.common.model.House;
import flats.common.model.View;
import flats.server.store.FlatStore;

import java.sql.Array;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Types;
import java.time.OffsetDateTime;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.Optional;

/**
 * Квартиры в таблице {@code flats}.
 */
public final class JdbcFlatStore implements FlatStore {
    private static final String COLUMNS = "id, name, coord_x, coord_y, creation_date, area, "
            + "number_of_rooms, height, kitchen_area, view, house_name, house_year, "
            + "house_flats_on_floor, house_lifts, owner";

    private final Database database;

    public JdbcFlatStore(Database database) {
        this.database = database;
    }

    @Override
    public List<Flat> findAll() {
        try (var connection = database.connection();
             var ps = connection.prepareStatement("SELECT " + COLUMNS + " FROM flats ORDER BY id");
             var rs = ps.executeQuery()) {
            var result = new ArrayList<Flat>();
            while (rs.next()) {
                result.add(read(rs));
            }
            return result;
        } catch (SQLException e) {
            throw new StorageException("Не удалось прочитать коллекцию", e);
        }
    }

    @Override
    public Optional<Flat> findById(long id) {
        try (var connection = database.connection();
             var ps = connection.prepareStatement("SELECT " + COLUMNS + " FROM flats WHERE id = ?")) {
            ps.setLong(1, id);
            try (var rs = ps.executeQuery()) {
                return rs.next() ? Optional.of(read(rs)) : Optional.empty();
            }
        } catch (SQLException e) {
            throw new StorageException("Не удалось прочитать квартиру", e);
        }
    }

    @Override
    public Flat insert(String owner, FlatDraft draft) {
        String sql = "INSERT INTO flats (name, coord_x, coord_y, area, number_of_rooms, height, "
                + "kitchen_area, view, house_name, house_year, house_flats_on_floor, house_lifts, owner) "
                + "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) RETURNING " + COLUMNS;
        try (var connection = database.connection(); var ps = connection.prepareStatement(sql)) {
            int next = bindDraft(ps, draft);
            ps.setString(next, owner);
            try (var rs = ps.executeQuery()) {
                rs.next();
                return read(rs);
            }
        } catch (SQLException e) {
            throw new StorageException("Не удалось сохранить квартиру", e);
        }
    }

    @Override
    public boolean update(long id, FlatDraft draft) {
        String sql = "UPDATE flats SET name = ?, coord_x = ?, coord_y = ?, area = ?, "
                + "number_of_rooms = ?, height = ?, kitchen_area = ?, view = ?, house_name = ?, "
                + "house_year = ?, house_flats_on_floor = ?, house_lifts = ? WHERE id = ?";
        try (var connection = database.connection(); var ps = connection.prepareStatement(sql)) {
            int next = bindDraft(ps, draft);
            ps.setLong(next, id);
            return ps.executeUpdate() == 1;
        } catch (SQLException e) {
            throw new StorageException("Не удалось обновить квартиру", e);
        }
    }

    @Override
    public boolean delete(long id) {
        try (var connection = database.connection();
             var ps = connection.prepareStatement("DELETE FROM flats WHERE id = ?")) {
            ps.setLong(1, id);
            return ps.executeUpdate() == 1;
        } catch (SQLException e) {
            throw new StorageException("Не удалось удалить квартиру", e);
        }
    }

    @Override
    public int deleteAll(Collection<Long> ids) {
        if (ids.isEmpty()) {
            return 0;
        }
        try (var connection = database.connection();
             var ps = connection.prepareStatement("DELETE FROM flats WHERE id = ANY (?)")) {
            Array array = connection.createArrayOf("bigint", ids.toArray(Long[]::new));
            ps.setArray(1, array);
            return ps.executeUpdate();
        } catch (SQLException e) {
            throw new StorageException("Не удалось удалить квартиры", e);
        }
    }

    /** Заполняет первые 12 параметров значениями черновика и возвращает номер следующего. */
    private static int bindDraft(PreparedStatement ps, FlatDraft d) throws SQLException {
        ps.setString(1, d.name());
        ps.setLong(2, d.coordinates().x());
        ps.setFloat(3, d.coordinates().y());
        if (d.area() == null) {
            ps.setNull(4, Types.INTEGER);
        } else {
            ps.setInt(4, d.area());
        }
        ps.setInt(5, d.numberOfRooms());
        ps.setInt(6, d.height());
        ps.setFloat(7, d.kitchenArea());
        ps.setString(8, d.view().name());
        ps.setString(9, d.house().name());
        ps.setInt(10, d.house().year());
        ps.setLong(11, d.house().numberOfFlatsOnFloor());
        ps.setLong(12, d.house().numberOfLifts());
        return 13;
    }

    private static Flat read(ResultSet rs) throws SQLException {
        int areaValue = rs.getInt(6);
        Integer area = rs.wasNull() ? null : areaValue;
        return new Flat(
                rs.getLong(1),
                rs.getString(2),
                new Coordinates(rs.getLong(3), rs.getFloat(4)),
                rs.getObject(5, OffsetDateTime.class).toZonedDateTime(),
                area,
                rs.getInt(7),
                rs.getInt(8),
                rs.getFloat(9),
                View.valueOf(rs.getString(10)),
                new House(rs.getString(11), rs.getInt(12), rs.getLong(13), rs.getLong(14)),
                rs.getString(15));
    }
}
