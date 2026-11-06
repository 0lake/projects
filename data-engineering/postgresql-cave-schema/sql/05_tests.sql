-- Проверки схемы и триггера. Любое нарушение завершает скрипт ошибкой.
-- Запуск: psql -v ON_ERROR_STOP=1 -f sql/05_tests.sql

BEGIN;

DO $$
DECLARE
    h1 INT; h2 INT; p1 INT; p2 INT; c1 INT;
    loc_gallery INT; loc_cave INT; loc_fog INT;
    s TEXT;
BEGIN
    SELECT location_id INTO loc_gallery FROM location WHERE name = 'Галерея';
    SELECT location_id INTO loc_cave    FROM location WHERE name = 'Зал пингвинов';
    SELECT location_id INTO loc_fog     FROM location WHERE name = 'Туманный зал';
    SELECT human_id    INTO h1 FROM human    WHERE name = 'Ворчун';
    SELECT human_id    INTO h2 FROM human    WHERE name = 'Скромник';
    SELECT penguin_id  INTO p1 FROM penguin  WHERE current_location = loc_cave;
    SELECT penguin_id  INTO p2 FROM penguin  WHERE current_location = loc_fog;
    SELECT creature_id INTO c1 FROM creature LIMIT 1;

    -- Сид: существо в галерее вместе с людьми
    SELECT status INTO s FROM human WHERE human_id = h1;
    ASSERT s = 'догнан существом', 'сид: человек должен быть догнан, а не ' || s;
    SELECT status INTO s FROM creature WHERE creature_id = c1;
    ASSERT s = 'жертва поймана', 'сид: существо поймало жертву';
    SELECT status INTO s FROM penguin WHERE penguin_id = p1;
    ASSERT s = 'в одиночестве', 'сид: пингвины одни';

    -- 1. Люди убегают к пингвинам: существо остаётся одно
    UPDATE human SET current_location = loc_cave WHERE human_id IN (h1, h2);
    SELECT status INTO s FROM creature WHERE creature_id = c1;
    ASSERT s = 'в поисках жертвы', 'после бегства существо ищет жертву, а не ' || s;
    SELECT status INTO s FROM human WHERE human_id = h1;
    ASSERT s = 'в группе с пингвином', 'человек смешался со стаей, а не ' || s;
    SELECT status INTO s FROM penguin WHERE penguin_id = p1;
    ASSERT s = 'в группе с человеком', 'пингвин в группе с человеком, а не ' || s;

    -- 2. Существо догоняет группу
    UPDATE creature SET current_location = loc_cave WHERE creature_id = c1;
    SELECT status INTO s FROM human WHERE human_id = h2;
    ASSERT s = 'догнан существом', 'группа догнана, а не ' || s;
    SELECT status INTO s FROM penguin WHERE penguin_id = p1;
    ASSERT s = 'догнан существом', 'пингвин догнан, а не ' || s;

    -- 3. Один человек уходит в туман к другой стае, оставшиеся в зале остаются догнанными
    UPDATE human SET current_location = loc_fog WHERE human_id = h2;
    SELECT status INTO s FROM human WHERE human_id = h2;
    ASSERT s = 'в группе с пингвином', 'в тумане человек со стаей, а не ' || s;
    SELECT status INTO s FROM human WHERE human_id = h1;
    ASSERT s = 'догнан существом', 'оставшийся человек всё ещё догнан, а не ' || s;

    -- 4. Существо уходит: прежнее место пересчитывается
    UPDATE creature SET current_location = loc_gallery WHERE creature_id = c1;
    SELECT status INTO s FROM human WHERE human_id = h1;
    ASSERT s = 'в группе с пингвином', 'после ухода существа человек снова в группе, а не ' || s;
    SELECT status INTO s FROM creature WHERE creature_id = c1;
    ASSERT s = 'в поисках жертвы', 'существо в пустой галерее, а не ' || s;

    -- 5. Удаление пингвинов пересчитывает место
    DELETE FROM penguin WHERE penguin_id = p2;
    SELECT status INTO s FROM human WHERE human_id = h2;
    ASSERT s = 'в одиночестве', 'без пингвинов человек один, а не ' || s;
END $$;

-- Ограничения целостности
DO $$
BEGIN
    BEGIN
        INSERT INTO cave (size, age, depth) VALUES (-1, 1, 1);
        RAISE EXCEPTION 'CHECK на cave.size не сработал';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
    BEGIN
        INSERT INTO gallery (size, carving_technique, cave_id) VALUES (10, 'дубль', 1);
        RAISE EXCEPTION 'UNIQUE на gallery.cave_id не сработал';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    BEGIN
        INSERT INTO human (name, age, gender) VALUES ('Тест', 30, 'м');
        UPDATE human SET status = 'выдумано' WHERE name = 'Тест';
        RAISE EXCEPTION 'CHECK на human.status не сработал';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
END $$;

ROLLBACK;
SELECT 'все проверки пройдены' AS result;
