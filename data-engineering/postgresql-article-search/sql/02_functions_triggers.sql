-- Функции и триггеры. Счётчики и рейтинги всегда пересчитываются по источнику
-- (COUNT и AVG), а не увеличиваются на единицу: так их нельзя рассинхронизировать
-- ни удалением, ни повторной загрузкой данных.

-- ---------- Функции ----------

-- Средний рейтинг статьи по отзывам пользователей (0, если отзывов нет)
CREATE OR REPLACE FUNCTION get_article_avg_rating(p_article_id INTEGER)
RETURNS NUMERIC AS $$
    SELECT COALESCE(ROUND(AVG(rating), 2), 0) FROM review WHERE article_id = p_article_id;
$$ LANGUAGE sql STABLE;

-- Авторы и число их опубликованных статей в категории
CREATE OR REPLACE FUNCTION get_authors_article_count_by_category(p_category article_category)
RETURNS TABLE (author_name VARCHAR, total_articles BIGINT) AS $$
    SELECT a.name, COUNT(*)
    FROM author a
    JOIN article_author aa ON aa.author_id = a.author_id
    JOIN article ar        ON ar.article_id = aa.article_id
    WHERE ar.category = p_category AND ar.status = 'опубликована'
    GROUP BY a.author_id, a.name
    ORDER BY COUNT(*) DESC, a.name;
$$ LANGUAGE sql STABLE;

-- Общее количество статей, по желанию только опубликованных
CREATE OR REPLACE FUNCTION get_total_articles_count(p_only_published BOOLEAN DEFAULT FALSE)
RETURNS INTEGER AS $$
    SELECT COUNT(*)::INTEGER FROM article
    WHERE NOT p_only_published OR status = 'опубликована';
$$ LANGUAGE sql STABLE;

-- Полнотекстовый поиск с морфологией русского языка.
-- Синтаксис запроса как в поисковиках: "нейронные сети" -обучение, OR, фразы.
CREATE OR REPLACE FUNCTION search_articles(
    p_query    TEXT,
    p_category article_category DEFAULT NULL,
    p_limit    INTEGER DEFAULT 20
) RETURNS TABLE (
    article_id INTEGER, title VARCHAR, category article_category,
    rating NUMERIC, views INTEGER, relevance REAL
) AS $$
    SELECT a.article_id, a.title, a.category, a.rating, a.views,
           ts_rank_cd(a.search_vector, q.tsq) AS relevance
    FROM article a, websearch_to_tsquery('russian', p_query) AS q(tsq)
    WHERE a.status = 'опубликована'
      AND a.search_vector @@ q.tsq
      AND (p_category IS NULL OR a.category = p_category)
    ORDER BY relevance DESC, a.rating DESC NULLS LAST, a.views DESC
    LIMIT p_limit;
$$ LANGUAGE sql STABLE;

-- Фиксация просмотра
CREATE OR REPLACE FUNCTION register_view(p_article_id INTEGER)
RETURNS INTEGER AS $$
    UPDATE article SET views = views + 1
    WHERE article_id = p_article_id AND status = 'опубликована'
    RETURNING views;
$$ LANGUAGE sql;

-- ---------- Триггеры ----------

-- Пересчёт числа статей и рейтинга автора
CREATE OR REPLACE FUNCTION refresh_author_stats(p_author_id INTEGER)
RETURNS VOID AS $$
    UPDATE author a
       SET total_articles = s.cnt,
           rating         = s.avg_rating
      FROM (SELECT COUNT(*)::INTEGER AS cnt,
                   ROUND(AVG(ar.rating), 2) AS avg_rating
              FROM article_author aa
              JOIN article ar ON ar.article_id = aa.article_id
             WHERE aa.author_id = p_author_id) s
     WHERE a.author_id = p_author_id;
$$ LANGUAGE sql;

-- 1. Изменился состав авторов статьи -> пересчитать автора
CREATE OR REPLACE FUNCTION trg_author_link_changed() RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP IN ('INSERT', 'UPDATE') THEN PERFORM refresh_author_stats(NEW.author_id); END IF;
    IF TG_OP IN ('DELETE', 'UPDATE') THEN PERFORM refresh_author_stats(OLD.author_id); END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER article_author_stats
    AFTER INSERT OR UPDATE OR DELETE ON article_author
    FOR EACH ROW EXECUTE FUNCTION trg_author_link_changed();

-- 2. Изменился отзыв -> пересчитать рейтинг статьи
CREATE OR REPLACE FUNCTION trg_review_changed() RETURNS TRIGGER AS $$
DECLARE
    aid INTEGER;
BEGIN
    FOR aid IN SELECT DISTINCT x FROM unnest(ARRAY[
                   CASE WHEN TG_OP <> 'INSERT' THEN OLD.article_id END,
                   CASE WHEN TG_OP <> 'DELETE' THEN NEW.article_id END]) AS x
               WHERE x IS NOT NULL
    LOOP
        UPDATE article
           SET rating = (SELECT ROUND(AVG(rating), 2) FROM review WHERE article_id = aid)
         WHERE article_id = aid;
    END LOOP;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER review_updates_rating
    AFTER INSERT OR UPDATE OR DELETE ON review
    FOR EACH ROW EXECUTE FUNCTION trg_review_changed();

-- 3. Изменился рейтинг статьи -> пересчитать её авторов (цепочка: отзыв, статья, автор)
CREATE OR REPLACE FUNCTION trg_article_rating_changed() RETURNS TRIGGER AS $$
DECLARE
    aid INTEGER;
BEGIN
    FOR aid IN SELECT author_id FROM article_author WHERE article_id = NEW.article_id LOOP
        PERFORM refresh_author_stats(aid);
    END LOOP;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER article_rating_to_authors
    AFTER UPDATE OF rating ON article
    FOR EACH ROW WHEN (OLD.rating IS DISTINCT FROM NEW.rating)
    EXECUTE FUNCTION trg_article_rating_changed();

-- 4. Отзыв можно оставить только на опубликованную статью
CREATE OR REPLACE FUNCTION trg_review_only_published() RETURNS TRIGGER AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM article
                    WHERE article_id = NEW.article_id AND status = 'опубликована') THEN
        RAISE EXCEPTION 'Отзыв возможен только на опубликованную статью (article_id = %)', NEW.article_id
            USING ERRCODE = 'check_violation';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER review_published_only
    BEFORE INSERT ON review
    FOR EACH ROW EXECUTE FUNCTION trg_review_only_published();

-- 5. Просрочка оплаты больше месяца деактивирует пользователя,
--    возврат к статусу «активна» возвращает доступ
CREATE OR REPLACE FUNCTION trg_subscription_status_changed() RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at := now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER subscription_touch
    BEFORE UPDATE ON subscription
    FOR EACH ROW EXECUTE FUNCTION trg_subscription_status_changed();

CREATE OR REPLACE FUNCTION trg_subscription_user_status() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'не оплачена больше месяца' THEN
        UPDATE app_user SET status = 'деактивирован' WHERE user_id = NEW.user_id;
    ELSIF NEW.status = 'активна' THEN
        UPDATE app_user SET status = 'оффлайн'
         WHERE user_id = NEW.user_id AND status = 'деактивирован';
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER subscription_user_status
    AFTER UPDATE OF status ON subscription
    FOR EACH ROW WHEN (OLD.status IS DISTINCT FROM NEW.status)
    EXECUTE FUNCTION trg_subscription_user_status();
