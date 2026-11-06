-- Аналитические запросы: оконные функции

-- 1. Лучший рейтинг среди статей каждого автора рядом с рейтингом самой статьи
SELECT a.article_id, a.title, aa.author_id, a.rating,
       MAX(a.rating) OVER (PARTITION BY aa.author_id) AS max_rating_per_author
FROM article a
JOIN article_author aa ON aa.article_id = a.article_id
WHERE a.status = 'опубликована'
ORDER BY aa.author_id, a.rating DESC NULLS LAST;

-- 2. Статья против лучшей в своей категории: насколько она отстаёт
SELECT article_id, title, category, rating,
       MAX(rating) OVER w                    AS best_in_category,
       rating - MAX(rating) OVER w           AS gap_to_best
FROM article
WHERE status = 'опубликована'
WINDOW w AS (PARTITION BY category)
ORDER BY category, rating DESC NULLS LAST;

-- 3. Квартили по рейтингу: 1 квартиль самые высокие рейтинги, 4 самые низкие
SELECT article_id, title, rating,
       NTILE(4) OVER (ORDER BY rating DESC NULLS LAST) AS rating_quartile
FROM article
WHERE status = 'опубликована' AND rating IS NOT NULL
ORDER BY rating DESC;

-- 4. Место статьи по просмотрам внутри категории: RANK оставляет «дыры» при равенстве,
--    DENSE_RANK нет
SELECT category, title, views,
       RANK()       OVER (PARTITION BY category ORDER BY views DESC) AS rank_in_category,
       DENSE_RANK() OVER (PARTITION BY category ORDER BY views DESC) AS dense_rank_in_category
FROM article
WHERE status = 'опубликована';

-- 5. Накопительная доля просмотров: какие статьи дают первые 80 процентов трафика
SELECT title, views,
       ROUND(100.0 * SUM(views) OVER (ORDER BY views DESC, article_id)
                   / SUM(views) OVER (), 1) AS cumulative_share_pct
FROM article
WHERE status = 'опубликована'
ORDER BY views DESC, article_id;

-- 6. Динамика отзывов пользователя: оценка и предыдущая оценка (LAG)
SELECT user_id, review_date, article_id, rating,
       LAG(rating) OVER (PARTITION BY user_id ORDER BY review_date) AS previous_rating
FROM review
ORDER BY user_id, review_date;
