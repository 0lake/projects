-- Схема базы данных. Скрипт идемпотентен и выполняется при каждом запуске сервера.

CREATE TABLE IF NOT EXISTS users (
    login         varchar(32)  PRIMARY KEY,
    salt          varchar(64)  NOT NULL,
    password_hash varchar(128) NOT NULL,
    created_at    timestamptz  NOT NULL DEFAULT now(),
    CONSTRAINT users_login_format CHECK (login ~ '^[A-Za-z0-9_.-]{3,32}$')
);

CREATE SEQUENCE IF NOT EXISTS flat_id_seq;

CREATE TABLE IF NOT EXISTS flats (
    id                   bigint           PRIMARY KEY DEFAULT nextval('flat_id_seq'),
    name                 text             NOT NULL CHECK (btrim(name) <> ''),
    coord_x              bigint           NOT NULL,
    coord_y              real             NOT NULL CHECK (coord_y > -519),
    creation_date        timestamptz      NOT NULL DEFAULT now(),
    area                 integer          CHECK (area > 0),
    number_of_rooms      integer          NOT NULL CHECK (number_of_rooms > 0),
    height               integer          NOT NULL CHECK (height > 0),
    kitchen_area         real             NOT NULL CHECK (kitchen_area > 0),
    view                 varchar(8)       NOT NULL CHECK (view IN ('STREET', 'YARD', 'BAD', 'GOOD')),
    house_name           text             NOT NULL,
    house_year           integer          NOT NULL CHECK (house_year > 0),
    house_flats_on_floor bigint           NOT NULL CHECK (house_flats_on_floor > 0),
    house_lifts          bigint           NOT NULL CHECK (house_lifts > 0),
    owner                varchar(32)      NOT NULL REFERENCES users (login)
);

CREATE INDEX IF NOT EXISTS flats_owner_idx ON flats (owner);
