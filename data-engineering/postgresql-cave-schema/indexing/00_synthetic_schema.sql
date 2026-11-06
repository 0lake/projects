-- Учебная модель «люди, сессии, ведомости» и синтетические данные.
-- Исходная база курса недоступна, поэтому таблицы воссозданы по структуре запросов,
-- а данные сгенерированы. Абсолютные цифры плана отличаются от оригинала,
-- сравнивать нужно структуру плана до и после индексов.

DROP TABLE IF EXISTS records, sessions, people CASCADE;

CREATE TABLE people (
    id          SERIAL PRIMARY KEY,
    last_name   VARCHAR(50) NOT NULL,
    first_name  VARCHAR(50) NOT NULL
);

CREATE TABLE sessions (
    id         SERIAL PRIMARY KEY,
    person_id  INTEGER NOT NULL REFERENCES people (id),
    study_year VARCHAR(9) NOT NULL,
    session_on DATE NOT NULL
);

CREATE TABLE records (
    id         SERIAL PRIMARY KEY,
    person_id  INTEGER NOT NULL REFERENCES people (id),
    grade      INTEGER
);

SELECT setseed(0.42);

INSERT INTO people (last_name, first_name)
SELECT (ARRAY['Петров','Афанасьев','Иванов','Смирнов','Кузнецов','Попов','Соколов',
              'Лебедев','Козлов','Новиков','Морозов','Волков'])[1 + floor(random()*12)::int],
       (ARRAY['Алексей','Мария','Дмитрий','Анна','Сергей','Ольга'])[1 + floor(random()*6)::int]
FROM generate_series(1, 20000);

-- 150 000 сессий, примерно 75 на каждую дату из пятилетнего диапазона
INSERT INTO sessions (person_id, study_year, session_on)
SELECT 1 + floor(random()*20000)::int,
       '2003/2004',
       DATE '2000-01-01' + floor(random()*2000)::int
FROM generate_series(1, 150000);

INSERT INTO records (person_id, grade)
SELECT 1 + floor(random()*20000)::int, 2 + floor(random()*4)::int
FROM generate_series(1, 200000);

-- Гарантируем непустой результат для второго запроса
UPDATE records SET person_id = (SELECT id FROM people WHERE last_name = 'Афанасьев' LIMIT 1)
WHERE id = 149007;
INSERT INTO sessions (person_id, study_year, session_on)
SELECT person_id, '2003/2004', DATE '2004-01-17' FROM records WHERE id = 149007;

ANALYZE;
