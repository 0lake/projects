-- Проверки: любой провал останавливает скрипт ошибкой.
-- Запуск: psql -v ON_ERROR_STOP=1 -f sql/06_tests.sql

BEGIN;

DO $$
DECLARE
    n INTEGER; r NUMERIC; s TEXT; ok BOOLEAN;
BEGIN
    -- Счётчики и рейтинги, посчитанные триггерами при загрузке
    SELECT total_articles INTO n FROM author WHERE name = 'Ли Вэй';
    ASSERT n = 5, 'у Ли Вэй 5 статей, получено ' || n;

    SELECT rating INTO r FROM article WHERE title LIKE 'Нейронные сети для%';
    ASSERT r = 4.67, 'рейтинг статьи 1 = (5+4+5)/3 = 4.67, получено ' || r;

    -- Рейтинг автора: среднее по его статьям
    SELECT rating INTO r FROM author WHERE name = 'Борис Миронов';
    ASSERT r = 3.50, 'рейтинг Миронова = (3.00+4.00)/2 = 3.50, получено ' || r;

    -- Цепочка триггеров: новый отзыв меняет рейтинг статьи и автора
    INSERT INTO review (user_id, article_id, rating) VALUES (1, 3, 5);
    SELECT rating INTO r FROM article WHERE article_id = 3;
    ASSERT r = 4.00, 'после отзыва рейтинг статьи 3 = (3+5)/2 = 4.00, получено ' || r;
    SELECT rating INTO r FROM author WHERE name = 'Борис Миронов';
    ASSERT r = 4.00, 'рейтинг автора обновился по цепочке, получено ' || r;

    -- Удаление отзыва возвращает рейтинг
    DELETE FROM review WHERE user_id = 1 AND article_id = 3;
    SELECT rating INTO r FROM article WHERE article_id = 3;
    ASSERT r = 3.00, 'рейтинг вернулся к 3.00, получено ' || r;

    -- Добавление и удаление авторства обновляет счётчик
    INSERT INTO article_author (author_id, article_id) VALUES (5, 1);
    SELECT total_articles INTO n FROM author WHERE name = 'Мария Лунд';
    ASSERT n = 2, 'после добавления авторства у Лунд 2 статьи, получено ' || n;
    DELETE FROM article_author WHERE author_id = 5 AND article_id = 1;
    SELECT total_articles INTO n FROM author WHERE name = 'Мария Лунд';
    ASSERT n = 1, 'после удаления снова 1, получено ' || n;

    -- Отзыв на черновик запрещён
    BEGIN
        INSERT INTO review (user_id, article_id, rating)
        SELECT 1, article_id, 5 FROM article WHERE status = 'черновик' LIMIT 1;
        RAISE EXCEPTION 'отзыв на черновик не должен проходить';
    EXCEPTION WHEN check_violation THEN NULL;
    END;

    -- Просрочка подписки деактивирует пользователя, оплата возвращает доступ
    UPDATE subscription SET status = 'не оплачена больше месяца' WHERE user_id = 4;
    SELECT status::TEXT INTO s FROM app_user WHERE user_id = 4;
    ASSERT s = 'деактивирован', 'пользователь должен быть деактивирован, получено ' || s;
    UPDATE subscription SET status = 'активна' WHERE user_id = 4;
    SELECT status::TEXT INTO s FROM app_user WHERE user_id = 4;
    ASSERT s = 'оффлайн', 'доступ должен вернуться, получено ' || s;

    -- Ограничения: возраст, email, телефон, Scopus ID, подписка
    BEGIN
        INSERT INTO app_user (nickname, email, phone_number, password_hash, age)
        VALUES ('kid', 'kid@mail.ru', '+79990000099', 'x', 17);
        RAISE EXCEPTION 'возраст 17 не должен проходить';
    EXCEPTION WHEN check_violation THEN NULL; END;
    BEGIN
        INSERT INTO app_user (nickname, email, phone_number, password_hash, age)
        VALUES ('bad', 'не-почта', '+79990000098', 'x', 30);
        RAISE EXCEPTION 'плохой email не должен проходить';
    EXCEPTION WHEN check_violation THEN NULL; END;
    BEGIN
        INSERT INTO app_user (nickname, email, phone_number, password_hash, age)
        VALUES ('bad2', 'ok@mail.ru', '8-999-000', 'x', 30);
        RAISE EXCEPTION 'плохой телефон не должен проходить';
    EXCEPTION WHEN check_violation THEN NULL; END;
    BEGIN
        INSERT INTO author (name, scopus_id) VALUES ('Тест', '123');
        RAISE EXCEPTION 'короткий Scopus ID не должен проходить';
    EXCEPTION WHEN check_violation THEN NULL; END;
    BEGIN
        INSERT INTO subscription (user_id, plan, price) VALUES (1, 'бесплатная', 100)
        ON CONFLICT DO NOTHING;
        RAISE EXCEPTION 'платная цена у бесплатного плана не должна проходить';
    EXCEPTION WHEN check_violation THEN NULL; WHEN unique_violation THEN NULL; END;
    BEGIN
        INSERT INTO review (user_id, article_id, rating) VALUES (4, 1, 4);
        RAISE EXCEPTION 'второй отзыв пользователя на ту же статью не должен проходить';
    EXCEPTION WHEN unique_violation THEN NULL; END;
    BEGIN
        INSERT INTO article (title, content, status, category)
        VALUES ('x', 'y', 'опубликована', 'наука');
        RAISE EXCEPTION 'опубликованная статья без даты не должна проходить';
    EXCEPTION WHEN check_violation THEN NULL; END;

    -- Функции
    ASSERT get_total_articles_count() = 12, 'всего статей 12';
    ASSERT get_total_articles_count(TRUE) = 10, 'опубликовано 10';
    ASSERT get_article_avg_rating(1) = 4.67, 'функция среднего рейтинга';
    ASSERT get_article_avg_rating(11) = 0, 'у статьи без отзывов 0';
    ASSERT (SELECT author_name FROM get_authors_article_count_by_category('наука') LIMIT 1) = 'Ли Вэй',
           'лидер по категории «наука» Ли Вэй';

    -- Просмотры считаются только у опубликованных статей
    SELECT views INTO n FROM article WHERE article_id = 1;
    ASSERT register_view(1) = n + 1, 'просмотр увеличивает счётчик';
    ASSERT register_view(11) IS NULL, 'у черновика просмотры не растут';

    -- Полнотекстовый поиск: морфология, исключения, фильтр категории, статусы
    ASSERT (SELECT article_id FROM search_articles('нейронная сеть')) = 1,
           'лемматизация: «нейронная сеть» находит «Нейронные сети»';
    SELECT COUNT(*) INTO n FROM search_articles('цены');
    ASSERT n = 2, 'словоформы «цен» и «цены» дают две статьи, получено ' || n;
    SELECT COUNT(*) INTO n FROM search_articles('поиск -нейронные');
    ASSERT n = 3, 'исключение слова: 3 статьи, получено ' || n;
    ASSERT (SELECT title FROM search_articles('поиск') LIMIT 1) LIKE 'Информационный поиск%',
           'заголовок весомее текста: на первом месте статья с «поиск» в заголовке';
    SELECT COUNT(*) INTO n FROM search_articles('поиск', 'наука');
    ASSERT n = 2, 'фильтр по категории: 2 статьи, получено ' || n;
    ASSERT NOT EXISTS (SELECT 1 FROM search_articles('метрики качества')), 'черновики в поиск не попадают';
    ASSERT NOT EXISTS (SELECT 1 FROM search_articles('ранние модели ранжирования')), 'архив в поиск не попадает';

    -- Представления
    ASSERT (SELECT COUNT(*) FROM category_rating_view) = 6, 'шесть категорий с опубликованными статьями';
    ASSERT (SELECT COUNT(*) FROM popular_articles) = 10, 'популярность по 10 статьям';
    ASSERT (SELECT author_name FROM top_authors LIMIT 1) = 'Анна Ковалёва',
           'при равенстве числа статей выше тот, у кого средний рейтинг больше';
    ASSERT (SELECT COUNT(*) FROM top_authors) = 5, 'в топе все пять авторов';
END $$;

ROLLBACK;
SELECT 'все проверки пройдены' AS result;
