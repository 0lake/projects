-- Сервис поиска научных, журналистских и других статей.
-- PostgreSQL 14+. Скрипт идемпотентен.

DROP MATERIALIZED VIEW IF EXISTS top_authors;
DROP VIEW IF EXISTS popular_articles, category_rating_view, active_users_subscriptions;
DROP TABLE IF EXISTS search_query, favorite, review, article_tag, tag,
                     article_author, article, author, subscription, app_user CASCADE;
DROP TYPE IF EXISTS user_status, user_role, subscription_plan, subscription_status,
                    article_status, article_category CASCADE;

CREATE TYPE user_status         AS ENUM ('онлайн', 'оффлайн', 'деактивирован');
CREATE TYPE user_role           AS ENUM ('читатель', 'автор', 'модератор', 'администратор');
CREATE TYPE subscription_plan   AS ENUM ('бесплатная', 'базовая', 'премиум');
CREATE TYPE subscription_status AS ENUM ('активна', 'не оплачена',
                                         'не оплачена больше месяца', 'отменена');
CREATE TYPE article_status      AS ENUM ('черновик', 'опубликована', 'архив');
CREATE TYPE article_category    AS ENUM ('наука', 'технологии', 'экономика',
                                         'журналистика', 'гуманитарные науки', 'другое');

-- Пользователь. Таблица называется app_user, потому что user зарезервировано в SQL.
CREATE TABLE app_user (
    user_id        SERIAL PRIMARY KEY,
    nickname       VARCHAR(30)  NOT NULL UNIQUE,
    email          VARCHAR(254) NOT NULL UNIQUE
                   CHECK (email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$'),
    phone_number   VARCHAR(16)  NOT NULL UNIQUE
                   CHECK (phone_number ~ '^\+[1-9][0-9]{9,14}$'),         -- формат E.164
    password_hash  VARCHAR(255) NOT NULL,
    age            INTEGER      NOT NULL CHECK (age BETWEEN 18 AND 120),   -- регистрация с 18 лет
    status         user_status  NOT NULL DEFAULT 'оффлайн',
    role           user_role    NOT NULL DEFAULT 'читатель',
    created_at     TIMESTAMPTZ  NOT NULL DEFAULT now()
);

-- Подписка принадлежит пользователю (1:1). Так цена и статус оплаты
-- не могут оказаться общими для нескольких людей.
CREATE TABLE subscription (
    subscription_id  SERIAL PRIMARY KEY,
    user_id          INTEGER NOT NULL UNIQUE REFERENCES app_user (user_id) ON DELETE CASCADE,
    plan             subscription_plan   NOT NULL DEFAULT 'бесплатная',
    price            INTEGER             NOT NULL DEFAULT 0 CHECK (price >= 0),
    terms            VARCHAR(100),
    status           subscription_status NOT NULL DEFAULT 'активна',
    updated_at       TIMESTAMPTZ         NOT NULL DEFAULT now(),
    CHECK (plan <> 'бесплатная' OR price = 0)
);

CREATE TABLE author (
    author_id       SERIAL PRIMARY KEY,
    name            VARCHAR(50) NOT NULL,
    description     VARCHAR(500),
    user_id         INTEGER UNIQUE REFERENCES app_user (user_id) ON DELETE SET NULL,
    nationality     CHAR(2) CHECK (nationality ~ '^[A-Z]{2}$'),            -- ISO 3166-1 alpha-2
    total_articles  INTEGER NOT NULL DEFAULT 0 CHECK (total_articles >= 0), -- поддерживает триггер
    rating          NUMERIC(3,2) CHECK (rating BETWEEN 0 AND 5),            -- поддерживает триггер
    scopus_id       VARCHAR(11) UNIQUE CHECK (scopus_id ~ '^[0-9]{11}$')
);

CREATE TABLE article (
    article_id        SERIAL PRIMARY KEY,
    title             VARCHAR(200) NOT NULL,
    content           TEXT NOT NULL,
    publication_date  DATE,
    size              INTEGER GENERATED ALWAYS AS (char_length(content)) STORED,
    views             INTEGER NOT NULL DEFAULT 0 CHECK (views >= 0),
    status            article_status   NOT NULL DEFAULT 'черновик',
    category          article_category NOT NULL,
    scopus_id         VARCHAR(11) UNIQUE CHECK (scopus_id ~ '^[0-9]{11}$'),
    rating            NUMERIC(3,2) CHECK (rating BETWEEN 0 AND 5),          -- поддерживает триггер
    -- Полнотекстовый вектор: заголовок весомее текста
    search_vector     TSVECTOR GENERATED ALWAYS AS (
                          setweight(to_tsvector('russian', title),   'A') ||
                          setweight(to_tsvector('russian', content), 'B')
                      ) STORED,
    CHECK (status = 'черновик' OR publication_date IS NOT NULL)
);

-- Авторство: у статьи может быть несколько авторов, у автора много статей
CREATE TABLE article_author (
    author_id   INTEGER NOT NULL REFERENCES author  (author_id)  ON DELETE CASCADE,
    article_id  INTEGER NOT NULL REFERENCES article (article_id) ON DELETE CASCADE,
    PRIMARY KEY (author_id, article_id)
);

-- Теги вынесены в справочник: один тег применяется ко многим статьям
CREATE TABLE tag (
    tag_id       SERIAL PRIMARY KEY,
    name         VARCHAR(20) NOT NULL UNIQUE,
    colour       VARCHAR(7)  CHECK (colour ~ '^#[0-9A-Fa-f]{6}$'),
    description  VARCHAR(100)
);

CREATE TABLE article_tag (
    article_id  INTEGER NOT NULL REFERENCES article (article_id) ON DELETE CASCADE,
    tag_id      INTEGER NOT NULL REFERENCES tag     (tag_id)     ON DELETE CASCADE,
    PRIMARY KEY (article_id, tag_id)
);

-- Один пользователь оставляет не больше одного отзыва на статью
CREATE TABLE review (
    review_id    SERIAL PRIMARY KEY,
    user_id      INTEGER  NOT NULL REFERENCES app_user (user_id)  ON DELETE CASCADE,
    article_id   INTEGER  NOT NULL REFERENCES article  (article_id) ON DELETE CASCADE,
    rating       SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    content      VARCHAR(400),
    review_date  DATE NOT NULL DEFAULT current_date,
    UNIQUE (user_id, article_id)
);

CREATE TABLE favorite (
    user_id     INTEGER NOT NULL REFERENCES app_user (user_id)   ON DELETE CASCADE,
    article_id  INTEGER NOT NULL REFERENCES article  (article_id) ON DELETE CASCADE,
    added_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (user_id, article_id)
);

-- История поисковых запросов, основа для аналитики спроса
CREATE TABLE search_query (
    search_id    SERIAL PRIMARY KEY,
    user_id      INTEGER NOT NULL REFERENCES app_user (user_id) ON DELETE CASCADE,
    query_text   VARCHAR(200) NOT NULL,
    searched_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Индексы
CREATE INDEX idx_article_search     ON article USING GIN (search_vector);
CREATE INDEX idx_article_category   ON article (category, rating DESC) WHERE status = 'опубликована';
CREATE INDEX idx_review_article     ON review (article_id);
CREATE INDEX idx_article_author_art ON article_author (article_id);
CREATE INDEX idx_article_tag_tag    ON article_tag (tag_id);
CREATE INDEX idx_favorite_article   ON favorite (article_id);
CREATE INDEX idx_search_user_time   ON search_query (user_id, searched_at DESC);
