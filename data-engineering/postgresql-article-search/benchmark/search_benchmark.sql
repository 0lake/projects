-- Бенчмарк полнотекстового поиска: GIN-индекс против последовательного скана.
-- Запускать на отдельной базе: скрипт добавляет 100 000 синтетических статей.
-- Порядок: psql -f sql/01_schema.sql -f sql/02_functions_triggers.sql -f benchmark/search_benchmark.sql

SELECT setseed(0.42);

INSERT INTO article (title, content, publication_date, views, status, category)
SELECT 'Статья ' || g || ': ' || (ARRAY['обзор','метод','анализ','модель','подход'])[1 + (g % 5)],
       (SELECT string_agg((ARRAY['данные','модель','поиск','рынок','сеть','текст','метод','выборка',
                                 'ранжирование','доверие','цены','алгоритм','система','анализ',
                                 'эксперимент','пользователь','рейтинг','источник'])[1 + floor(random()*18)::INT], ' ')
          FROM generate_series(1, 40) k WHERE g > 0),
       DATE '2020-01-01' + (g % 2000),
       (random() * 5000)::INT,
       'опубликована',
       ((ARRAY['наука','технологии','экономика','журналистика','гуманитарные науки','другое'])[1 + (g % 6)])::article_category
FROM generate_series(1, 100000) g;

-- Редкое слово, чтобы запрос был избирательным
UPDATE article SET content = content || ' квазикристалл' WHERE article_id % 5000 = 0;
ANALYZE article;

\echo '--- с GIN-индексом'
EXPLAIN (ANALYZE, BUFFERS, COSTS OFF)
SELECT article_id, title FROM article
WHERE search_vector @@ websearch_to_tsquery('russian', 'квазикристалл');

DROP INDEX idx_article_search;
ANALYZE article;

\echo '--- без индекса'
EXPLAIN (ANALYZE, BUFFERS, COSTS OFF)
SELECT article_id, title FROM article
WHERE search_vector @@ websearch_to_tsquery('russian', 'квазикристалл');

CREATE INDEX idx_article_search ON article USING GIN (search_vector);
