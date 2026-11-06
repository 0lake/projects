package flats.server.store.memory;

import flats.common.model.Flat;
import flats.common.model.FlatDraft;
import flats.server.store.FlatStore;

import java.time.ZonedDateTime;
import java.util.Collection;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

/**
 * Хранилище в памяти для тестов и запуска без базы данных.
 */
public final class MemoryFlatStore implements FlatStore {
    private final Map<Long, Flat> flats = new ConcurrentHashMap<>();
    private final AtomicLong sequence = new AtomicLong();

    @Override
    public List<Flat> findAll() {
        return List.copyOf(flats.values());
    }

    @Override
    public Optional<Flat> findById(long id) {
        return Optional.ofNullable(flats.get(id));
    }

    @Override
    public Flat insert(String owner, FlatDraft draft) {
        var flat = Flat.of(sequence.incrementAndGet(), ZonedDateTime.now(), owner, draft);
        flats.put(flat.id(), flat);
        return flat;
    }

    @Override
    public boolean update(long id, FlatDraft draft) {
        return flats.computeIfPresent(id, (key, old) -> old.withDraft(draft)) != null;
    }

    @Override
    public boolean delete(long id) {
        return flats.remove(id) != null;
    }

    @Override
    public int deleteAll(Collection<Long> ids) {
        return (int) ids.stream().filter(this::delete).count();
    }
}
