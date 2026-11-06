-- Индексы под фильтры и условия соединения.
-- B-tree вместо hash: он покрывает равенство и диапазоны, не требует
-- отдельной логики для сортировки и одинаково надёжен во всех версиях.
CREATE INDEX idx_people_last_name   ON people   (last_name);
CREATE INDEX idx_sessions_date_person ON sessions (session_on, person_id);
CREATE INDEX idx_sessions_person    ON sessions (person_id);
CREATE INDEX idx_records_person     ON records  (person_id);
ANALYZE;
