# Данные

Файл `Rate.csv` из датасета [Health Insurance Marketplace](https://www.kaggle.com/datasets/hhs/health-insurance-marketplace) (HHS, около 12.7 млн строк) в репозиторий не включен из-за размера и лицензии.

1. Скачайте датасет с Kaggle и положите `Rate.csv` в эту папку.
2. Запуск: `insurance-rates --csv data/Rate.csv --sample 300000`.

Используются только столбцы: `BusinessYear, StateCode, IssuerId, PlanId, RatingAreaId, Tobacco, Age, IndividualRate, IndividualTobaccoRate`.
