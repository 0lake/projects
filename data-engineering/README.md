# Data Engineering

Проекты про движение данных: загрузка, преобразование, хранение, проектирование баз данных и сбор из внешних источников.

<table>
  <tr>
    <td width="46%">
      <a href="./spark-etl-star-schema">
        <img src="spark-etl-star-schema/assets/banner.svg?v=11" alt="Spark ETL: звездообразная схема в PostgreSQL, витрины в ClickHouse и MongoDB" width="100%">
      </a>
    </td>
    <td>
      <h3><a href="./spark-etl-star-schema">Spark ETL: звездообразная схема в PostgreSQL, витрины в ClickHouse и MongoDB</a></h3>
      <p>Spark читает плоскую выгрузку, строит измерения и факты в PostgreSQL, считает 6 витрин и пишет их в ClickHouse и MongoDB. Docker Compose с healthcheck, секреты в .env, тесты на синтетических данных.</p>
      <p>
        <img src="https://img.shields.io/badge/Spark-E25A1C?style=flat-square&logo=apachespark&logoColor=white" alt="Spark">
        <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL">
        <img src="https://img.shields.io/badge/ClickHouse-FFCC01?style=flat-square" alt="ClickHouse">
        <img src="https://img.shields.io/badge/MongoDB-47A248?style=flat-square&logo=mongodb&logoColor=white" alt="MongoDB">
        <img src="https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white" alt="Docker">
      </p>
    </td>
  </tr>
</table>

<table>
  <tr>
    <td width="46%">
      <a href="./postgresql-article-search">
        <img src="postgresql-article-search/assets/banner.svg?v=11" alt="Article Search: полнотекстовый поиск, рейтинги и подписки на PostgreSQL" width="100%">
      </a>
    </td>
    <td>
      <h3><a href="./postgresql-article-search">Article Search: база данных сервиса поиска статей</a></h3>
      <p>Прикладная схема на PostgreSQL: полнотекстовый поиск на русском (GIN, 1,6 мс против 37 мс на 100 000 статей), цепочка триггеров для рейтингов, бизнес-правила в ограничениях, представления и оконные функции. Тесты на ASSERT и CI на живой базе.</p>
      <p>
        <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL">
        <img src="https://img.shields.io/badge/Full--text_search-F4A261?style=flat-square" alt="Full-text search">
        <img src="https://img.shields.io/badge/PL%2FpgSQL-336791?style=flat-square" alt="PL/pgSQL">
      </p>
    </td>
  </tr>
</table>

<table>
  <tr>
    <td width="46%">
      <a href="./web-scraping-goat-breeds">
        <img src="web-scraping-goat-breeds/assets/banner.svg?v=11" alt="Веб-скрейпинг: породы коз" width="100%">
      </a>
    </td>
    <td>
      <h3><a href="./web-scraping-goat-breeds">Веб-скрейпинг: породы коз</a></h3>
      <p>Парсер таблицы пород: retry-сессия, поиск столбцов по заголовкам, абсолютные ссылки, загрузка изображений и HTML-галерея. Тесты на фикстуре, CLI.</p>
      <p>
        <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
        <img src="https://img.shields.io/badge/BeautifulSoup-4B8BBE?style=flat-square" alt="BeautifulSoup">
        <img src="https://img.shields.io/badge/requests-2C5BB4?style=flat-square" alt="requests">
      </p>
    </td>
  </tr>
</table>

<table>
  <tr>
    <td width="46%">
      <a href="./postgresql-cave-schema">
        <img src="postgresql-cave-schema/assets/banner.svg?v=11" alt="Cave Schema: проектирование базы данных на PostgreSQL" width="100%">
      </a>
    </td>
    <td>
      <h3><a href="./postgresql-cave-schema">Cave Schema: проектирование базы данных на PostgreSQL</a></h3>
      <p>От текста до работающей схемы: инфологическая и даталогическая модели, ограничения целостности, нормализация до BCNF, триггер на PL/pgSQL с тестами и разбор планов запросов с индексами (10,5 мс до 1,1 мс). CI проверяет схему на живом PostgreSQL.</p>
      <p>
        <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL">
        <img src="https://img.shields.io/badge/PL%2FpgSQL-336791?style=flat-square" alt="PL/pgSQL">
        <img src="https://img.shields.io/badge/Mermaid-FF3670?style=flat-square&logo=mermaid&logoColor=white" alt="Mermaid">
      </p>
    </td>
  </tr>
</table>

[← Все проекты](../)
