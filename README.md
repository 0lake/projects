<div align="center">

<img src="assets/banner.svg" alt="Oleg Sadovnikov: business and product analytics, data analysis, ML" width="100%">

<br>

[![Telegram](https://img.shields.io/badge/Telegram-@ollogi-0b6fb8?style=flat-square&labelColor=b6ff3c&logo=telegram&logoColor=ffffff)](https://t.me/ollogi)
[![Resume](https://img.shields.io/badge/Resume-Google%20Drive-0b6fb8?style=flat-square&labelColor=b6ff3c&logo=googledrive&logoColor=031a33)](https://drive.google.com/drive/folders/1k8JxVXoA4IyDKNency-2qoXDov1iHgMl)
[![ITMO](https://img.shields.io/badge/ITMO-Business%20Informatics-0b6fb8?style=flat-square&labelColor=b6ff3c)](https://itmo.ru)

</div>

---

## Привет, я Олег

Учусь на 4 курсе бизнес-информатики в Университете ИТМО. Я бизнес-продуктовый аналитик: смотрю на продукт через экономику бизнеса, проверяю гипотезы на данных, пишу требования, проектирую API и планирую A/B-тесты. Здесь собраны мои проекты: бизнес-продуктовая аналитика, анализ данных, инженерия данных и машинное обучение.

## Проекты

<table>
  <tr>
    <td width="46%">
      <a href="./tbank-intensive">
        <img src="tbank-intensive/assets/banner.svg" alt="T-Travel Price Tracker" width="100%">
      </a>
    </td>
    <td>
      <h3><a href="./tbank-intensive">Т-Путешествия: трекер цен с учётом привилегий Т-Премиум</a></h3>
      <p>Интенсив Т-Банка. Как превратить трекер цены из инструмента поиска самого дешёвого билета в инструмент выбора самой выгодной поездки.</p>
      <p>
        <img src="https://img.shields.io/badge/PRD-FFDD2D?style=flat-square&labelColor=222222" alt="PRD">
        <img src="https://img.shields.io/badge/OpenAPI-6BA539?style=flat-square&logo=openapiinitiative&logoColor=white" alt="OpenAPI">
        <img src="https://img.shields.io/badge/A%2FB%20test-222222?style=flat-square" alt="A/B test">
        <img src="https://img.shields.io/badge/R-276DC3?style=flat-square&logo=r&logoColor=white" alt="R">
      </p>
      <p><b>Результат на данных:</b> Т-Премиум это 36% аудитории, средний чек выше на 48%, заказов на пользователя 7,53 против 4,38.</p>
    </td>
  </tr>
</table>

<table>
  <tr>
    <td width="46%">
      <a href="./ml/telco-churn-prediction">
        <img src="ml/telco-churn-prediction/assets/banner.svg" alt="Telco Churn" width="100%">
      </a>
    </td>
    <td>
      <h3><a href="./ml/telco-churn-prediction">Telco Churn: прогноз оттока клиентов</a></h3>
      <p>Полный цикл ML-проекта: пайплайн на scikit-learn, CLI для обучения и скоринга, SHAP, тесты и CI.</p>
      <p>
        <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
        <img src="https://img.shields.io/badge/scikit--learn-F7931E?style=flat-square&logo=scikit-learn&logoColor=white" alt="scikit-learn">
        <img src="https://img.shields.io/badge/SHAP-0B7285?style=flat-square" alt="SHAP">
      </p>
      <p><b>Результат на тесте:</b> находит 81% уходящих клиентов, из всех предупреждений верные 54%. Главный фактор оттока: помесячный контракт.</p>
    </td>
  </tr>
</table>

<table>
  <tr>
    <td width="46%">
      <a href="./data-analysis/resident-evil-network">
        <img src="data-analysis/resident-evil-network/assets/banner.svg" alt="Resident Evil Character Network" width="100%">
      </a>
    </td>
    <td>
      <h3><a href="./data-analysis/resident-evil-network">Сеть персонажей Resident Evil: как распадается вселенная</a></h3>
      <p>Сетевой анализ на R: 12 кумулятивных снимков франшизы, сообщества Louvain, центральности. Командный проект, моя часть: подготовка данных и построение сети.</p>
      <p>
        <img src="https://img.shields.io/badge/R-276DC3?style=flat-square&logo=r&logoColor=white" alt="R">
        <img src="https://img.shields.io/badge/igraph-1F77B4?style=flat-square" alt="igraph">
        <img src="https://img.shields.io/badge/visNetwork-E4572E?style=flat-square" alt="visNetwork">
      </p>
      <p><b>Результат:</b> сеть растёт с 5 до 51 персонажа, плотность падает с 0,70 до 0,11, сообществ становится 5. Главный хаб: Chris Redfield.</p>
    </td>
  </tr>
</table>

<table>
  <tr>
    <td width="46%">
      <a href="./ml/arima-gdp-forecasting">
        <img src="ml/arima-gdp-forecasting/assets/banner.svg" alt="ARIMA vs SARIMAX" width="100%">
      </a>
    </td>
    <td>
      <h3><a href="./ml/arima-gdp-forecasting">Семейство ARIMA: прогноз ВВП США на sktime</a></h3>
      <p>Экзаменационный проект ИТМО: сравнение 7 моделей временных рядов, пакет с CLI, тестами и CI.</p>
      <p>
        <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
        <img src="https://img.shields.io/badge/sktime-0F6FC6?style=flat-square" alt="sktime">
        <img src="https://img.shields.io/badge/statsmodels-4A6FA5?style=flat-square" alt="statsmodels">
      </p>
      <p><b>Результат:</b> SARIMAX даёт RMSE 1,13 против 2,45 у наивного прогноза; в README разобраны ограничения данных.</p>
    </td>
  </tr>
</table>

<table>
  <tr>
    <td width="46%">
      <a href="./data-engineering/spark-etl-star-schema">
        <img src="data-engineering/spark-etl-star-schema/assets/banner.svg" alt="Spark ETL: звездообразная схема в PostgreSQL, витрины в ClickHouse и MongoDB" width="100%">
      </a>
    </td>
    <td>
      <h3><a href="./data-engineering/spark-etl-star-schema">Spark ETL: звездообразная схема в PostgreSQL, витрины в ClickHouse и MongoDB</a></h3>
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
      <a href="./data-engineering/web-scraping-goat-breeds">
        <img src="data-engineering/web-scraping-goat-breeds/assets/banner.svg" alt="Веб-скрейпинг: породы коз" width="100%">
      </a>
    </td>
    <td>
      <h3><a href="./data-engineering/web-scraping-goat-breeds">Веб-скрейпинг: породы коз</a></h3>
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
      <a href="./data-analysis/movies-cleaning-clustering">
        <img src="data-analysis/movies-cleaning-clustering/assets/banner.svg" alt="Фильмы: очистка на R и сравнение алгоритмов кластеризации" width="100%">
      </a>
    </td>
    <td>
      <h3><a href="./data-analysis/movies-cleaning-clustering">Фильмы: очистка на R и сравнение алгоритмов кластеризации</a></h3>
      <p>Очистка на R, затем K-Means, MiniBatch, GMM и Ward с метриками качества, PCA и профилями кластеров. Вывод честный: структура в данных слабая, и это показано цифрами.</p>
      <p>
        <img src="https://img.shields.io/badge/R-276DC3?style=flat-square&logo=r&logoColor=white" alt="R">
        <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
        <img src="https://img.shields.io/badge/scikit--learn-F7931E?style=flat-square&logo=scikit-learn&logoColor=white" alt="scikit--learn">
      </p>
    </td>
  </tr>
</table>

<table>
  <tr>
    <td width="46%">
      <a href="./ml/health-insurance-rate-modeling">
        <img src="ml/health-insurance-rate-modeling/assets/banner.svg" alt="Тарифы медстрахования: классификация и регрессия без утечки" width="100%">
      </a>
    </td>
    <td>
      <h3><a href="./ml/health-insurance-rate-modeling">Тарифы медстрахования: классификация и регрессия без утечки</a></h3>
      <p>Разбор и исправление лабораторной с утечкой цели: разбиение по планам, пороги классов по train, baseline и ансамбль LR + RF. Тесты показывают, как выглядит утечка.</p>
      <p>
        <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
        <img src="https://img.shields.io/badge/scikit--learn-F7931E?style=flat-square&logo=scikit-learn&logoColor=white" alt="scikit--learn">
      </p>
    </td>
  </tr>
</table>

| Раздел | О чем |
|---|---|
| [tbank-intensive](./tbank-intensive) | Бизнес-продуктовая и системная аналитика: анализ данных, CustDev, PRD, API, A/B-тест |
| [data-analysis](./data-analysis) | Исследование данных, сетевой анализ, визуализация |
| [data-engineering](./data-engineering) | ETL на Spark, PostgreSQL, ClickHouse, MongoDB, веб-скрейпинг |
| [ml](./ml) | Классификация, временные ряды, оценка и интерпретация моделей |

## Инструменты

![Python](https://img.shields.io/badge/Python-0b6fb8?style=flat-square&labelColor=031a33&logo=python&logoColor=ffffff)
![pandas](https://img.shields.io/badge/pandas-0b6fb8?style=flat-square&labelColor=031a33&logo=pandas&logoColor=ffffff)
![scikit-learn](https://img.shields.io/badge/scikit--learn-0b6fb8?style=flat-square&labelColor=031a33&logo=scikit-learn&logoColor=ffffff)
![sktime](https://img.shields.io/badge/sktime-0b6fb8?style=flat-square&labelColor=031a33)
![statsmodels](https://img.shields.io/badge/statsmodels-0b6fb8?style=flat-square&labelColor=031a33)
![SHAP](https://img.shields.io/badge/SHAP-0b6fb8?style=flat-square&labelColor=031a33)
![Jupyter](https://img.shields.io/badge/Jupyter-0b6fb8?style=flat-square&labelColor=031a33&logo=jupyter&logoColor=ffffff)
![Spark](https://img.shields.io/badge/Spark-0b6fb8?style=flat-square&labelColor=031a33&logo=apachespark&logoColor=ffffff)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-0b6fb8?style=flat-square&labelColor=031a33&logo=postgresql&logoColor=ffffff)
![ClickHouse](https://img.shields.io/badge/ClickHouse-0b6fb8?style=flat-square&labelColor=031a33)
![MongoDB](https://img.shields.io/badge/MongoDB-0b6fb8?style=flat-square&labelColor=031a33&logo=mongodb&logoColor=ffffff)
![Docker](https://img.shields.io/badge/Docker-0b6fb8?style=flat-square&labelColor=031a33&logo=docker&logoColor=ffffff)
![R](https://img.shields.io/badge/R-0b6fb8?style=flat-square&labelColor=031a33&logo=r&logoColor=ffffff)
![igraph](https://img.shields.io/badge/igraph-0b6fb8?style=flat-square&labelColor=031a33)
![ggplot2](https://img.shields.io/badge/ggplot2-0b6fb8?style=flat-square&labelColor=031a33)
![dplyr](https://img.shields.io/badge/dplyr-0b6fb8?style=flat-square&labelColor=031a33)
![OpenAPI](https://img.shields.io/badge/OpenAPI-0b6fb8?style=flat-square&labelColor=031a33&logo=openapiinitiative&logoColor=ffffff)
![Git](https://img.shields.io/badge/Git-0b6fb8?style=flat-square&labelColor=031a33&logo=git&logoColor=ffffff)

## Структура

```text
projects/
├── tbank-intensive/     # проект с интенсива Т-Банка
├── data-engineering/    # ETL и сбор данных
│   ├── spark-etl-star-schema/
│   └── web-scraping-goat-breeds/
├── data-analysis/       # анализ данных
│   ├── resident-evil-network/
│   └── movies-cleaning-clustering/
├── ml/                  # машинное обучение
│   ├── telco-churn-prediction/
│   ├── arima-gdp-forecasting/
│   └── health-insurance-rate-modeling/
├── _template/           # шаблон для нового проекта
└── README.md
```

## Связаться

Лучше всего писать в [Telegram](https://t.me/ollogi). Резюме лежит [здесь](https://drive.google.com/drive/folders/1k8JxVXoA4IyDKNency-2qoXDov1iHgMl).
