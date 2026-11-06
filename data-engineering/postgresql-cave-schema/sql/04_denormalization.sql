-- Контролируемая денормализация: пещера и галерея читаются почти всегда вместе.
-- Вместо физического слияния таблиц (теряем 3NF и целостность) строим
-- материализованное представление: схема остаётся нормализованной,
-- чтение идёт без JOIN.

DROP MATERIALIZED VIEW IF EXISTS cave_gallery_mv;

CREATE MATERIALIZED VIEW cave_gallery_mv AS
SELECT c.cave_id,
       c.size  AS cave_size,
       c.age   AS cave_age,
       c.depth AS cave_depth,
       g.gallery_id,
       g.size  AS gallery_size,
       g.carving_technique
FROM cave c
LEFT JOIN gallery g ON g.cave_id = c.cave_id;

CREATE UNIQUE INDEX idx_cave_gallery_mv ON cave_gallery_mv (cave_id);

-- Обновление после изменения cave или gallery:
-- REFRESH MATERIALIZED VIEW CONCURRENTLY cave_gallery_mv;
