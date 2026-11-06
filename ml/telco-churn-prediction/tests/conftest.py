"""Synthetic data with the same schema as the real dataset, so tests run offline."""

import numpy as np
import pandas as pd
import pytest


def make_synthetic(n: int = 600, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    contract = rng.choice(["Month-to-month", "One year", "Two year"], n, p=[0.55, 0.2, 0.25])
    tenure = rng.integers(0, 72, n)
    monthly = rng.uniform(20, 115, n).round(2)
    internet = rng.choice(["DSL", "Fiber optic", "No"], n, p=[0.35, 0.45, 0.2])

    risk = (
        0.9 * (contract == "Month-to-month")
        + 0.6 * (internet == "Fiber optic")
        - 0.03 * tenure
        + 0.01 * monthly
        - 0.8
    )
    churn = rng.random(n) < 1 / (1 + np.exp(-2.5 * risk))

    yes_no = lambda p: rng.choice(["Yes", "No"], n, p=[p, 1 - p])  # noqa: E731
    return pd.DataFrame(
        {
            "CustomerID": [f"C{i:05d}" for i in range(n)],
            "Gender": rng.choice(["Male", "Female"], n),
            "Senior Citizen": yes_no(0.16),
            "Partner": yes_no(0.5),
            "Dependents": yes_no(0.3),
            "Tenure Months": tenure,
            "Phone Service": yes_no(0.9),
            "Multiple Lines": rng.choice(["Yes", "No", "No phone service"], n),
            "Internet Service": internet,
            "Online Security": rng.choice(["Yes", "No", "No internet service"], n),
            "Online Backup": rng.choice(["Yes", "No", "No internet service"], n),
            "Device Protection": rng.choice(["Yes", "No", "No internet service"], n),
            "Tech Support": rng.choice(["Yes", "No", "No internet service"], n),
            "Streaming TV": rng.choice(["Yes", "No", "No internet service"], n),
            "Streaming Movies": rng.choice(["Yes", "No", "No internet service"], n),
            "Contract": contract,
            "Paperless Billing": yes_no(0.6),
            "Payment Method": rng.choice(
                ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"], n
            ),
            "Monthly Charges": monthly,
            "Total Charges": np.where(tenure == 0, " ", (tenure * monthly).round(2).astype(str)),
            "CLTV": rng.integers(2000, 6500, n),
            "Churn Label": np.where(churn, "Yes", "No"),
        }
    )


@pytest.fixture(scope="session")
def raw_df() -> pd.DataFrame:
    return make_synthetic()


@pytest.fixture(scope="session")
def data_file(tmp_path_factory, raw_df) -> str:
    path = tmp_path_factory.mktemp("data") / "synthetic.csv"
    raw_df.to_csv(path, index=False)
    return str(path)
