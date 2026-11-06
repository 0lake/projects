-- Запрос 1: люди с фамилией Петров и их сессии за конкретную дату.
-- Исходная формулировка использует LEFT JOIN, но условие по sessions в WHERE
-- отбрасывает строки без пары, поэтому результат равен INNER JOIN.
EXPLAIN (ANALYZE, BUFFERS)
SELECT p.last_name, s.study_year
FROM people p
LEFT JOIN sessions s ON p.id = s.person_id
WHERE p.last_name = 'Петров'
  AND s.session_on = DATE '2004-01-17';

-- Запрос 2: три таблицы, три фильтра.
EXPLAIN (ANALYZE, BUFFERS)
SELECT p.first_name, r.person_id, s.session_on
FROM people p
LEFT JOIN records  r ON p.id = r.person_id
LEFT JOIN sessions s ON p.id = s.person_id
WHERE p.last_name = 'Афанасьев'
  AND r.id = 149007
  AND s.session_on = DATE '2004-01-17';
