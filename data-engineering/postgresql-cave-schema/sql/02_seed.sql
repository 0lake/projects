-- Тестовые данные: сцена бегства через галерею в пещеру.

INSERT INTO location (name, coordinates) VALUES
    ('Галерея',        POINT(0, 0)),
    ('Вход в пещеру',  POINT(0, 40)),
    ('Зал пингвинов',  POINT(10, 90)),
    ('Туманный зал',   POINT(25, 120));

INSERT INTO cave (size, age, depth) VALUES (1000, 1000, 150);

INSERT INTO gallery (size, carving_technique, cave_id)
VALUES (200, 'Гнусная резьба', 1);

INSERT INTO human (name, age, gender, emotion, current_location) VALUES
    ('Ворчун',    30, 'м', 'Страх',  1),
    ('Скромник',  27, 'ж', 'Ужас',   1);

INSERT INTO penguin (habitat, population_size, behaviour, current_location) VALUES
    ('Антарктика', 13, 'Паническое поведение', 3),
    ('Антарктика',  7, 'Стайное поведение',    4);

INSERT INTO creature (name, speed, description, current_location) VALUES
    ('Тварь', 100, 'Мистическое, страшное, нагнетающее', 1);

INSERT INTO fog (visibility, density, duration_time) VALUES
    (10, 8, INTERVAL '2 minutes'),
    (25, 4, INTERVAL '45 seconds');

INSERT INTO explore (cave_id, human_id) VALUES (1, 1), (1, 2);
INSERT INTO chase   (creature_id, penguin_id, human_id) VALUES (1, 1, 1), (1, 1, 2);
INSERT INTO blur    (fog_id, penguin_id, human_id)      VALUES (1, 1, 1), (2, 2, 2);
