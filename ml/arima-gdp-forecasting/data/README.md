# Данные

Датасет не включён в репозиторий: [US Economic Indicators 1991-2023](https://www.kaggle.com/datasets/niranjankrishnan/us-economic-indicators-1991-2023) на Kaggle.

Два способа получить данные:

1. Скачать CSV вручную и запустить `arima-gdp --csv data/<файл>.csv`.
2. Поставить `pip install -e ".[kaggle]"` и запустить `arima-gdp --download` (нужен настроенный доступ к Kaggle API).

Из файла берутся строки `place_name == "United States"` и `frequency == "monthly"`.
