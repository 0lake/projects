-- Схема предметной области «Пещера, туман и существо».
-- PostgreSQL 14+. Скрипт идемпотентен: его можно запускать повторно.

DROP TABLE IF EXISTS blur, chase, explore, gallery, cave, fog,
                     creature, human, penguin, location CASCADE;
DROP MATERIALIZED VIEW IF EXISTS cave_gallery_mv;
DROP TYPE IF EXISTS gender_enum CASCADE;

CREATE TYPE gender_enum AS ENUM ('м', 'ж');

-- Справочник мест, где могут находиться участники сцены
CREATE TABLE location (
    location_id  SERIAL PRIMARY KEY,
    name         VARCHAR(100) NOT NULL UNIQUE,
    coordinates  POINT
);

CREATE TABLE cave (
    cave_id  SERIAL PRIMARY KEY,
    size     INTEGER NOT NULL CHECK (size  >= 0),
    age      INTEGER NOT NULL CHECK (age   >= 0),
    depth    INTEGER NOT NULL CHECK (depth >= 0)
);

-- Одна галерея принадлежит ровно одной пещере (UNIQUE делает связь 1:1)
CREATE TABLE gallery (
    gallery_id         SERIAL PRIMARY KEY,
    size               INTEGER NOT NULL CHECK (size >= 0),
    carving_technique  VARCHAR(100) NOT NULL,
    cave_id            INTEGER NOT NULL UNIQUE
                       REFERENCES cave (cave_id) ON DELETE CASCADE
);

CREATE TABLE penguin (
    penguin_id        SERIAL PRIMARY KEY,
    habitat           VARCHAR(100) NOT NULL,
    population_size   INTEGER NOT NULL CHECK (population_size >= 0),
    behaviour         VARCHAR(100),
    current_location  INTEGER REFERENCES location (location_id),
    status            VARCHAR(30) NOT NULL DEFAULT 'в одиночестве'
                      CHECK (status IN ('в одиночестве',
                                        'в группе с человеком',
                                        'догнан существом'))
);

CREATE TABLE human (
    human_id          SERIAL PRIMARY KEY,
    name              VARCHAR(50) NOT NULL,
    age               INTEGER CHECK (age BETWEEN 0 AND 120),
    gender            gender_enum,
    emotion           VARCHAR(100),
    current_location  INTEGER REFERENCES location (location_id),
    status            VARCHAR(30) NOT NULL DEFAULT 'в одиночестве'
                      CHECK (status IN ('в одиночестве',
                                        'в группе с пингвином',
                                        'догнан существом'))
);

CREATE TABLE creature (
    creature_id       SERIAL PRIMARY KEY,
    name              VARCHAR(100) NOT NULL,
    speed             INTEGER CHECK (speed BETWEEN 0 AND 300000),
    description       TEXT,
    current_location  INTEGER REFERENCES location (location_id),
    status            VARCHAR(30) NOT NULL DEFAULT 'в поисках жертвы'
                      CHECK (status IN ('в поисках жертвы',
                                        'жертва поймана'))
);

CREATE TABLE fog (
    fog_id         SERIAL PRIMARY KEY,
    visibility     INTEGER  NOT NULL CHECK (visibility >= 0),
    density        INTEGER  NOT NULL CHECK (density BETWEEN 0 AND 10),
    duration_time  INTERVAL CHECK (duration_time >= INTERVAL '0')
);

-- Ассоциативные таблицы: составные первичные ключи, каскадное удаление
CREATE TABLE explore (
    cave_id   INTEGER NOT NULL REFERENCES cave  (cave_id)  ON DELETE CASCADE,
    human_id  INTEGER NOT NULL REFERENCES human (human_id) ON DELETE CASCADE,
    PRIMARY KEY (cave_id, human_id)
);

CREATE TABLE chase (
    creature_id  INTEGER NOT NULL REFERENCES creature (creature_id) ON DELETE CASCADE,
    penguin_id   INTEGER NOT NULL REFERENCES penguin  (penguin_id)  ON DELETE CASCADE,
    human_id     INTEGER NOT NULL REFERENCES human    (human_id)    ON DELETE CASCADE,
    PRIMARY KEY (creature_id, penguin_id, human_id)
);

CREATE TABLE blur (
    fog_id      INTEGER NOT NULL REFERENCES fog     (fog_id)     ON DELETE CASCADE,
    penguin_id  INTEGER NOT NULL REFERENCES penguin (penguin_id) ON DELETE CASCADE,
    human_id    INTEGER NOT NULL REFERENCES human   (human_id)   ON DELETE CASCADE,
    PRIMARY KEY (fog_id, penguin_id, human_id)
);

-- Индексы под внешние ключи: по ним фильтрует триггер и ссылочные проверки.
-- Первичные ключи ассоциаций покрывают только первый столбец составного ключа,
-- поэтому для остальных столбцов нужны отдельные индексы.
CREATE INDEX idx_human_location     ON human    (current_location);
CREATE INDEX idx_penguin_location   ON penguin  (current_location);
CREATE INDEX idx_creature_location  ON creature (current_location);
CREATE INDEX idx_explore_human      ON explore  (human_id);
CREATE INDEX idx_chase_penguin      ON chase    (penguin_id);
CREATE INDEX idx_chase_human        ON chase    (human_id);
CREATE INDEX idx_blur_penguin       ON blur     (penguin_id);
CREATE INDEX idx_blur_human         ON blur     (human_id);
