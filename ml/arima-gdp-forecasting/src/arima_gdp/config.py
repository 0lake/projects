"""Experiment configuration: columns, split and model orders."""
from dataclasses import dataclass, field

KAGGLE_DATASET = "niranjankrishnan/us-economic-indicators-1991-2023"

TARGET = "Gross domestic product, constant prices"
EXOG = [
    "Inflation, average consumer prices",
    "Unemployment rate",
    "GSPC.Close",
    "Volume of imports of goods and services",
    "Volume of exports of goods and services",
    "Current account balance",
]


@dataclass(frozen=True)
class Config:
    test_size: float = 0.2
    seasonal_period: int = 12
    arima_order: tuple = (1, 1, 1)
    # Orders found by AutoARIMA on the training part in the original experiment
    sarima_order: tuple = (0, 1, 0)
    sarima_seasonal_order: tuple = (0, 0, 2, 12)
    target: str = TARGET
    exog: list = field(default_factory=lambda: list(EXOG))
