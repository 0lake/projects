package flats.server.store;

import flats.common.model.Flat;
import flats.common.model.FlatDraft;

import java.util.Collection;
import java.util.List;
import java.util.Optional;

/**
 * Постоянное хранилище квартир. Реализации обязаны быть потокобезопасными.
 */
public interface FlatStore {
    /** @return все квартиры в произвольном порядке */
    List<Flat> findAll();

    /** @return квартира с заданным id, если есть */
    Optional<Flat> findById(long id);

    /**
     * Сохраняет новую квартиру; id и дату создания назначает хранилище.
     *
     * @return сохранённая квартира
     */
    Flat insert(String owner, FlatDraft draft);

    /**
     * Заменяет значения полей квартиры, id, дата создания и владелец не меняются.
     *
     * @return true, если квартира существовала
     */
    boolean update(long id, FlatDraft draft);

    /** @return true, если квартира существовала и была удалена */
    boolean delete(long id);

    /**
     * Удаляет квартиры с заданными id.
     *
     * @return количество удалённых
     */
    int deleteAll(Collection<Long> ids);
}
