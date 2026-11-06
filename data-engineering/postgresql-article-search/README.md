<div align="center">

<img src="assets/banner.svg" alt="Article Search: полнотекстовый поиск, рейтинги и подписки на PostgreSQL" width="100%">

<br>

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![PL/pgSQL](https://img.shields.io/badge/PL%2FpgSQL-336791?style=for-the-badge)
![Full-text search](https://img.shields.io/badge/Full--text_search-GIN-F4A261?style=for-the-badge)
![Tests](https://github.com/0lake/projects/actions/workflows/postgresql-article-search-ci.yml/badge.svg)

</div>

# Article Search: база данных сервиса поиска статей

Реляционная база для сервиса, где можно искать научные, журналистские и другие статьи, оценивать их, оставлять отзывы, вести избранное и подписки. Проект проходит путь от описания предметной области и моделей до работающего полнотекстового поиска на русском языке, триггеров, представлений и аналитики на оконных функциях.

Это второй проект по базам данных в портфолио. Первый, [Cave Schema](../postgresql-cave-schema), про нормализацию и индексы. Здесь акцент на прикладной схеме: поиск, рейтинги, бизнес-правила в базе.

## Содержание

1. [Предметная область](#предметная-область)
2. [Инфологическая модель](#инфологическая-модель)
3. [Даталогическая модель](#даталогическая-модель)
4. [Бизнес-правила в самой базе](#бизнес-правила-в-самой-базе)
5. [Полнотекстовый поиск](#полнотекстовый-поиск)
6. [Представления и аналитика](#представления-и-аналитика)
7. [Как запустить](#как-запустить)
8. [Структура](#структура)

## Предметная область

Сервис хранит статьи и авторов, учитывает просмотры и оценки, считает рейтинг и популярность, показывает выдачу по запросу.

| Бизнес-процесс | Как реализован |
|---|---|
| Регистрация и личный кабинет | `app_user`, проверки email, телефона, возраста; подписка в `subscription` |
| Поиск по ключевым словам, категориям, авторам | `search_articles()` на `tsvector` и GIN, фильтр по категории, теги |
| Избранное, отзыв, оценка | `favorite`, `review` с оценкой от 1 до 5 |
| Загрузка статей авторами | `article`, `article_author`, статусы «черновик», «опубликована», «архив» |
| Обновление рейтинга от действий пользователей | цепочка триггеров: отзыв, статья, автор |
| Анализ популярности | представления и оконные функции |

## Инфологическая модель

Сущности, их атрибуты и связи без привязки к СУБД. Жёлтым выделены связи, у которых есть собственные атрибуты (отзыв несёт оценку и дату).

```mermaid
%%{init: {"theme": "base", "flowchart": {"curve": "basis", "nodeSpacing": 50, "rankSpacing": 80}, "themeVariables": {"fontFamily": "Inter, Segoe UI, sans-serif", "fontSize": "15px", "lineColor": "#6b7f99", "primaryTextColor": "#0f1b2d"}}}%%
flowchart LR
    classDef entity fill:#e8f1fb,stroke:#2f5d8a,stroke-width:2px,color:#0f1b2d
    classDef assoc fill:#fff4d6,stroke:#b8860b,stroke-width:2px,color:#4a3500

    USER["<b>User</b><br/>nickname<br/>email<br/>phone_number<br/>age<br/>status<br/>role"]:::entity
    SUB["<b>Subscription</b><br/>plan<br/>price<br/>terms<br/>status"]:::entity
    AUTH["<b>Author</b><br/>name<br/>description<br/>nationality<br/>scopus_id<br/>total_articles<br/>rating"]:::entity
    ART["<b>Article</b><br/>title<br/>content<br/>publication_date<br/>views<br/>status<br/>category<br/>rating"]:::entity
    TAG["<b>Tag</b><br/>name<br/>colour<br/>description"]:::entity
    REV{{"<b>Review</b><br/>rating, content,<br/>date"}}:::assoc
    FAV{{"<b>Favorite</b>"}}:::assoc
    SRCH["<b>SearchQuery</b><br/>query_text<br/>searched_at"]:::entity

    USER -- "1 : 0..1" --- SUB
    USER -- "1 : 0..1" --- AUTH
    AUTH -- "N : M (авторство)" --- ART
    ART -- "N : M" --- TAG
    USER -- "1" --- REV
    REV -- "N" --- ART
    USER -- "1" --- FAV
    FAV -- "N" --- ART
    USER -- "1 : N" --- SRCH
```

## Даталогическая модель

Реализация в PostgreSQL: типы данных, ключи, ограничения. Исходная учебная модель при реализации была доработана: теги вынесены в справочник, подписка привязана к пользователю, отзыв получил оценку. Таблица всех изменений с причинами: [`docs/design.md`](docs/design.md).

```mermaid
%%{init: {"theme": "base", "themeVariables": {"fontFamily": "Inter, Segoe UI, sans-serif", "fontSize": "14px", "primaryColor": "#e8f1fb", "primaryBorderColor": "#2f5d8a", "primaryTextColor": "#0f1b2d", "lineColor": "#6b7f99"}}}%%
erDiagram
    app_user {
        SERIAL user_id PK
        VARCHAR_30 nickname "UNIQUE"
        VARCHAR_254 email "UNIQUE, regex"
        VARCHAR_16 phone_number "UNIQUE, E164"
        VARCHAR_255 password_hash
        INTEGER age "CHECK 18..120"
        user_status status
        user_role role
        TIMESTAMPTZ created_at
    }
    subscription {
        SERIAL subscription_id PK
        INTEGER user_id FK "UNIQUE"
        subscription_plan plan
        INTEGER price "CHECK >= 0"
        VARCHAR_100 terms
        subscription_status status
        TIMESTAMPTZ updated_at
    }
    author {
        SERIAL author_id PK
        VARCHAR_50 name
        VARCHAR_500 description
        INTEGER user_id FK "UNIQUE, NULL"
        CHAR_2 nationality "ISO 3166"
        INTEGER total_articles "trigger"
        NUMERIC_3_2 rating "trigger"
        VARCHAR_11 scopus_id "UNIQUE, 11 digits"
    }
    article {
        SERIAL article_id PK
        VARCHAR_200 title
        TEXT content
        DATE publication_date
        INTEGER size "GENERATED"
        INTEGER views "CHECK >= 0"
        article_status status
        article_category category
        VARCHAR_11 scopus_id "UNIQUE"
        NUMERIC_3_2 rating "trigger"
        TSVECTOR search_vector "GENERATED, GIN"
    }
    article_author {
        INTEGER author_id PK, FK
        INTEGER article_id PK, FK
    }
    tag {
        SERIAL tag_id PK
        VARCHAR_20 name "UNIQUE"
        VARCHAR_7 colour "#RRGGBB"
        VARCHAR_100 description
    }
    article_tag {
        INTEGER article_id PK, FK
        INTEGER tag_id PK, FK
    }
    review {
        SERIAL review_id PK
        INTEGER user_id FK
        INTEGER article_id FK
        SMALLINT rating "CHECK 1..5"
        VARCHAR_400 content
        DATE review_date
    }
    favorite {
        INTEGER user_id PK, FK
        INTEGER article_id PK, FK
        TIMESTAMPTZ added_at
    }
    search_query {
        SERIAL search_id PK
        INTEGER user_id FK
        VARCHAR_200 query_text
        TIMESTAMPTZ searched_at
    }

    app_user ||--o| subscription  : "owns"
    app_user ||--o| author        : "is"
    author   ||--o{ article_author : ""
    article  ||--o{ article_author : ""
    article  ||--o{ article_tag    : ""
    tag      ||--o{ article_tag    : ""
    app_user ||--o{ review         : "writes"
    article  ||--o{ review         : ""
    app_user ||--o{ favorite       : ""
    article  ||--o{ favorite       : ""
    app_user ||--o{ search_query   : "makes"
```

Исходники диаграмм: [`docs/infological.mmd`](docs/infological.mmd), [`docs/datalogical.mmd`](docs/datalogical.mmd). Знак подчёркивания в типах (`VARCHAR_30`) нужен только синтаксису Mermaid, в SQL это `VARCHAR(30)`.

## Бизнес-правила в самой базе

Правила, которые нельзя нарушить из приложения, обходом или ручным запросом:

| Правило | Механизм |
|---|---|
| Пользователю не меньше 18 лет | `CHECK (age BETWEEN 18 AND 120)` |
| Email, телефон (E.164), Scopus ID (11 цифр) корректны | `CHECK` с регулярными выражениями |
| Бесплатный тариф стоит 0 | `CHECK (plan <> 'бесплатная' OR price = 0)` |
| Опубликованная статья имеет дату публикации | `CHECK` |
| Один отзыв пользователя на статью | `UNIQUE (user_id, article_id)` |
| Отзыв только на опубликованную статью | триггер `review_published_only` |
| Рейтинг статьи равен среднему по отзывам | триггер `review_updates_rating` |
| Рейтинг и число статей автора всегда актуальны | триггеры `article_rating_to_authors`, `article_author_stats` |
| Просрочка оплаты больше месяца деактивирует пользователя | триггер `subscription_user_status` |

Счётчики и рейтинги пересчитываются по источнику, а не увеличиваются на единицу, поэтому не расходятся с данными при удалении, правке и повторной загрузке. Разбор триггеров: [`docs/design.md`](docs/design.md#триггеры).

## Полнотекстовый поиск

```sql
-- фраза, исключение слова, фильтр по категории
SELECT title, category, rating, relevance
FROM search_articles('поиск -нейронные', 'наука');
```

- `tsvector` строится из заголовка (вес A) и текста (вес B), по нему GIN-индекс;
- запрос разбирается как в поисковиках: фразы в кавычках, `OR`, минус для исключения;
- ранжирование `ts_rank_cd`, затем рейтинг и просмотры;
- русская морфология: «цены» находит «цен».

На 100 000 статей запрос по редкому слову: **1,6 мс с GIN-индексом и 37 мс без него**, около 23 раз быстрее ([`benchmark/results.txt`](benchmark/results.txt)). Поиск использует стемминг, а не семантику, и синонимы не находит, подробнее в [`docs/design.md`](docs/design.md#полнотекстовый-поиск).

## Представления и аналитика

| Объект | Назначение |
|---|---|
| `category_rating_view` | средний рейтинг, число статей и просмотры по категориям |
| `active_users_subscriptions` | пользователи онлайн с тарифом и статусом оплаты |
| `popular_articles` | популярность как рейтинг, умноженный на логарифм просмотров |
| `top_authors` (материализованное) | авторы по числу статей и среднему рейтингу |

Оконные функции ([`sql/05_analytics.sql`](sql/05_analytics.sql)): `MAX() OVER` по автору и по категории, отставание статьи от лучшей в категории, `NTILE(4)` по рейтингу, `RANK` и `DENSE_RANK` по просмотрам, накопительная доля трафика, `LAG` по оценкам пользователя.

## Как запустить

Нужен PostgreSQL 14 или новее.

```bash
createdb articles
psql -d articles -v ON_ERROR_STOP=1 -f sql/01_schema.sql
psql -d articles -v ON_ERROR_STOP=1 -f sql/02_functions_triggers.sql
psql -d articles -v ON_ERROR_STOP=1 -f sql/03_views.sql
psql -d articles -v ON_ERROR_STOP=1 -f sql/04_seed.sql
psql -d articles -f sql/05_analytics.sql                  # оконные функции
psql -d articles -v ON_ERROR_STOP=1 -f sql/06_tests.sql   # проверки

# бенчмарк поиска: отдельная база, добавляет 100 000 статей
createdb bench
psql -d bench -f sql/01_schema.sql -f sql/02_functions_triggers.sql -f benchmark/search_benchmark.sql
```

Скрипты идемпотентны. Те же шаги выполняет CI на каждый пуш. Проверки в `sql/06_tests.sql` написаны на `ASSERT`: цепочка триггеров, все ограничения, функции, поиск (морфология, исключения, фильтр, статусы) и представления.

## Структура

```
postgresql-article-search/
├── sql/
│   ├── 01_schema.sql              # типы, таблицы, ограничения, индексы
│   ├── 02_functions_triggers.sql  # функции, поиск, триггеры
│   ├── 03_views.sql               # представления и материализованное
│   ├── 04_seed.sql                # демонстрационные данные
│   ├── 05_analytics.sql           # оконные функции
│   └── 06_tests.sql               # ASSERT-проверки
├── benchmark/
│   ├── search_benchmark.sql       # GIN против Seq Scan на 100 000 статей
│   └── results.txt
├── docs/
│   ├── design.md                  # что изменено в модели и почему
│   ├── infological.mmd
│   └── datalogical.mmd
└── assets/banner.svg
```

[← Data Engineering](../) · [← Все проекты](../../)
