"""Fitting the seven forecasters. ARIMA, SARIMA and AutoARIMA go through sktime;
ARIMAX and SARIMAX use statsmodels SARIMAX because they need exogenous regressors."""
import pandas as pd
from sktime.forecasting.arima import ARIMA, AutoARIMA
from sktime.forecasting.base import ForecastingHorizon
from sktime.forecasting.naive import NaiveForecaster
from statsmodels.tsa.statespace.sarimax import SARIMAX

from .config import Config


def _sktime_forecast(forecaster, y_train, fh) -> pd.Series:
    return forecaster.fit(y_train).predict(fh)


def _sarimax_forecast(order, seasonal_order, y_train, X_train, X_test, index) -> pd.Series:
    fit = SARIMAX(
        endog=y_train.values, exog=X_train.values, order=order, seasonal_order=seasonal_order,
        enforce_stationarity=False, enforce_invertibility=False,
    ).fit(disp=False, maxiter=200)
    return pd.Series(fit.forecast(steps=len(index), exog=X_test.values), index=index)


def fit_all(y_train, y_test, X_train, X_test, cfg: Config):
    """Return (predictions, info). predictions: name -> Series on the test index."""
    fh = ForecastingHorizon(y_test.index, is_relative=False)
    p = {}
    p["Naive"] = _sktime_forecast(NaiveForecaster(strategy="last"), y_train, fh)
    p["Seasonal naive"] = _sktime_forecast(
        NaiveForecaster(strategy="last", sp=cfg.seasonal_period), y_train, fh)
    p["ARIMA"] = _sktime_forecast(
        ARIMA(order=cfg.arima_order, suppress_warnings=True), y_train, fh)
    p["SARIMA"] = _sktime_forecast(
        ARIMA(order=cfg.sarima_order, seasonal_order=cfg.sarima_seasonal_order,
              suppress_warnings=True), y_train, fh)
    auto = AutoARIMA(seasonal=True, sp=cfg.seasonal_period, stepwise=True,
                     suppress_warnings=True, error_action="ignore")
    p["AutoARIMA"] = _sktime_forecast(auto, y_train, fh)
    p["ARIMAX"] = _sarimax_forecast(
        cfg.arima_order, (0, 0, 0, 0), y_train, X_train, X_test, y_test.index)
    p["SARIMAX"] = _sarimax_forecast(
        cfg.sarima_order, cfg.sarima_seasonal_order, y_train, X_train, X_test, y_test.index)
    params = auto.get_fitted_params()
    info = {"autoarima_order": params.get("order"), "autoarima_seasonal_order": params.get("seasonal_order")}
    return p, info
