# Машинное обучение

Проекты по построению и оценке моделей: от подготовки признаков до интерпретации результатов.

## Проекты

<table>
  <tr>
    <td width="46%">
      <a href="./telco-churn-prediction">
        <img src="telco-churn-prediction/assets/banner.svg?v=12" alt="Telco Churn" width="100%">
      </a>
    </td>
    <td>
      <h3><a href="./telco-churn-prediction">Telco Churn: прогноз оттока клиентов</a></h3>
      <p>Полный цикл: пайплайн на scikit-learn, выбор модели по PR-AUC, порог под целевой Recall, SHAP, CLI для обучения и скоринга, тесты и CI.</p>
      <p>
        <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
        <img src="https://img.shields.io/badge/scikit--learn-F7931E?style=flat-square&logo=scikit-learn&logoColor=white" alt="scikit-learn">
        <img src="https://img.shields.io/badge/SHAP-0B7285?style=flat-square" alt="SHAP">
      </p>
      <p><b>Результат на тесте:</b> Recall 0,81, Precision 0,54, ROC-AUC 0,855.</p>
    </td>
  </tr>
</table>

<table>
  <tr>
    <td width="46%">
      <a href="./arima-gdp-forecasting">
        <img src="arima-gdp-forecasting/assets/banner.svg?v=12" alt="ARIMA vs SARIMAX" width="100%">
      </a>
    </td>
    <td>
      <h3><a href="./arima-gdp-forecasting">Семейство ARIMA: прогноз ВВП США на sktime</a></h3>
      <p>Сравнение 7 моделей временных рядов: ARIMA, SARIMA, AutoARIMA, ARIMAX, SARIMAX и наивные базовые. Пакет с CLI, метриками, тестами и CI.</p>
      <p>
        <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
        <img src="https://img.shields.io/badge/sktime-0F6FC6?style=flat-square" alt="sktime">
        <img src="https://img.shields.io/badge/statsmodels-4A6FA5?style=flat-square" alt="statsmodels">
      </p>
      <p><b>Результат:</b> SARIMAX снижает RMSE более чем вдвое по сравнению с наивным прогнозом (1,13 против 2,45), но с честными оговорками про данные.</p>
    </td>
  </tr>
</table>

<table>
  <tr>
    <td width="46%">
      <a href="./health-insurance-rate-modeling">
        <img src="health-insurance-rate-modeling/assets/banner.svg?v=13" alt="Тарифы медстрахования: классификация и регрессия без утечки" width="100%">
      </a>
    </td>
    <td>
      <h3><a href="./health-insurance-rate-modeling">Тарифы медстрахования: классификация и регрессия без утечки</a></h3>
      <p>Разбор и исправление лабораторной с утечкой цели: разбиение по планам, пороги классов по train, baseline и ансамбль LR + RF. Тесты показывают, как выглядит утечка.</p>
      <p>
        <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
        <img src="https://img.shields.io/badge/scikit--learn-F7931E?style=flat-square&logo=scikit-learn&logoColor=white" alt="scikit--learn">
      </p>
    </td>
  </tr>
</table>

[← Все проекты](../)
