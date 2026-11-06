-- Представления для аналитики и интерфейса

-- Рейтинг и охват по категориям (только опубликованные статьи)
CREATE OR REPLACE VIEW category_rating_view AS
SELECT category,
       ROUND(AVG(rating), 2) AS avg_rating,
       COUNT(*)              AS total_articles,
       SUM(views)            AS total_views
FROM article
WHERE status = 'опубликована'
GROUP BY category
ORDER BY avg_rating DESC NULLS LAST;

-- Пользователи онлайн и их подписки
CREATE OR REPLACE VIEW active_users_subscriptions AS
SELECT u.user_id, u.nickname, u.email, s.plan, s.status AS subscription_status
FROM app_user u
JOIN subscription s ON s.user_id = u.user_id
WHERE u.status = 'онлайн';

-- Популярность: рейтинг, умноженный на логарифм просмотров.
-- Логарифм не даёт одной вирусной статье задавить всё остальное.
CREATE OR REPLACE VIEW popular_articles AS
SELECT article_id, title, category, rating, views,
       ROUND((COALESCE(rating, 0) * LN(1 + views))::NUMERIC, 2) AS popularity
FROM article
WHERE status = 'опубликована'
ORDER BY popularity DESC;

-- Топ-авторы: тяжёлый агрегат кэшируется
DROP MATERIALIZED VIEW IF EXISTS top_authors;
CREATE MATERIALIZED VIEW top_authors AS
SELECT a.author_id,
       a.name AS author_name,
       a.nationality,
       COUNT(ar.article_id)                AS total_articles,
       ROUND(AVG(ar.rating), 2)            AS avg_article_rating,
       COALESCE(SUM(ar.views), 0)          AS total_views
FROM author a
JOIN article_author aa ON aa.author_id = a.author_id
JOIN article ar        ON ar.article_id = aa.article_id AND ar.status = 'опубликована'
GROUP BY a.author_id, a.name, a.nationality
ORDER BY total_articles DESC, avg_article_rating DESC NULLS LAST;

CREATE UNIQUE INDEX idx_top_authors ON top_authors (author_id);
-- Обновление без блокировки чтения: REFRESH MATERIALIZED VIEW CONCURRENTLY top_authors;
