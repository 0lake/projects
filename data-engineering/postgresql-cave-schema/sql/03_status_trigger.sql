-- Статусы участников сцены зависят от того, кто находится с ними в одном месте.
--
--   существо одно                  -> существо «в поисках жертвы»
--   человек и пингвин              -> «в группе с пингвином» / «в группе с человеком»
--   существо рядом с человеком или
--   пингвином                      -> «догнан существом» / «жертва поймана»
--   никого рядом                   -> «в одиночестве»
--
-- Функция пересчитывает статусы целого места по фактическому составу,
-- поэтому результат не зависит от порядка перемещений.

CREATE OR REPLACE FUNCTION refresh_location_status(p_location INTEGER)
RETURNS VOID AS $$
DECLARE
    has_human    BOOLEAN;
    has_penguin  BOOLEAN;
    has_creature BOOLEAN;
BEGIN
    IF p_location IS NULL THEN
        RETURN;
    END IF;

    SELECT EXISTS (SELECT 1 FROM human    WHERE current_location = p_location),
           EXISTS (SELECT 1 FROM penguin  WHERE current_location = p_location),
           EXISTS (SELECT 1 FROM creature WHERE current_location = p_location)
      INTO has_human, has_penguin, has_creature;

    UPDATE human
       SET status = CASE WHEN has_creature THEN 'догнан существом'
                         WHEN has_penguin  THEN 'в группе с пингвином'
                         ELSE 'в одиночестве' END
     WHERE current_location = p_location;

    UPDATE penguin
       SET status = CASE WHEN has_creature THEN 'догнан существом'
                         WHEN has_human    THEN 'в группе с человеком'
                         ELSE 'в одиночестве' END
     WHERE current_location = p_location;

    UPDATE creature
       SET status = CASE WHEN has_human OR has_penguin THEN 'жертва поймана'
                         ELSE 'в поисках жертвы' END
     WHERE current_location = p_location;
END;
$$ LANGUAGE plpgsql;

-- Триггерная функция: обновляет и новое, и прежнее место участника
CREATE OR REPLACE FUNCTION trg_update_status()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        PERFORM refresh_location_status(OLD.current_location);
        RETURN OLD;
    END IF;

    PERFORM refresh_location_status(NEW.current_location);

    IF TG_OP = 'UPDATE'
       AND OLD.current_location IS DISTINCT FROM NEW.current_location THEN
        PERFORM refresh_location_status(OLD.current_location);
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- UPDATE OF current_location: сами обновления status триггер не вызывают,
-- поэтому рекурсии нет.
DROP TRIGGER IF EXISTS update_human_status    ON human;
DROP TRIGGER IF EXISTS update_penguin_status  ON penguin;
DROP TRIGGER IF EXISTS update_creature_status ON creature;

CREATE TRIGGER update_human_status
    AFTER INSERT OR DELETE OR UPDATE OF current_location ON human
    FOR EACH ROW EXECUTE FUNCTION trg_update_status();

CREATE TRIGGER update_penguin_status
    AFTER INSERT OR DELETE OR UPDATE OF current_location ON penguin
    FOR EACH ROW EXECUTE FUNCTION trg_update_status();

CREATE TRIGGER update_creature_status
    AFTER INSERT OR DELETE OR UPDATE OF current_location ON creature
    FOR EACH ROW EXECUTE FUNCTION trg_update_status();

-- Начальная расстановка статусов для уже загруженных данных
SELECT refresh_location_status(location_id) FROM location;
