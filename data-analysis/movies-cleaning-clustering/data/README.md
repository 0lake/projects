# Данные

Файлы в репозиторий не входят.

- `data.csv` : исходный датасет (10 000 фильмов, 13 столбцов: `X, Movie.Name, Year.of.Release, Run.Time.in.minutes, Movie.Rating, Votes, MetaScore, Gross, Genre, Certification, Director, Stars, Description`), скачивался с Kaggle.
- `movies_clean.csv` : результат `r/01_clean_movies.R` (7 945 строк, без `X`), вход для Python-части.

Положите `data.csv` сюда и запустите R-скрипт, затем:

```bash
movies-clustering --csv data/movies_clean.csv
movies-clustering --csv data/movies_clean.csv --log
```
