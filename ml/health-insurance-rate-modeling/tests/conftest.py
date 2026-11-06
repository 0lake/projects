import numpy as np
import pandas as pd
import pytest


def synthetic_rates(n_plans=300, seed=0) -> pd.DataFrame:
    """Rate.csv look-alike: rate depends on state, issuer and age, plus noise."""
    rng = np.random.default_rng(seed)
    states = ["AK", "TX", "NY", "FL", "OH", "WA"]
    state_base = dict(zip(states, [450, 280, 380, 300, 260, 330]))
    ages = ["0-20"] + [str(a) for a in range(21, 64)] + ["64 and over", "Family Option"]
    rows = []
    for p in range(n_plans):
        st = states[p % len(states)]
        issuer = 10000 + (p % 15)
        area = f"Rating Area {1 + p % 9}"
        year = 2014 + (p % 3)
        plan_factor = rng.uniform(0.8, 1.3)
        for age in ages:
            a = {"0-20": 20, "64 and over": 65, "Family Option": 35}.get(age) or int(age)
            rate = state_base[st] * plan_factor * (0.4 + a / 45) + rng.normal(0, 8)
            tob = rate * 1.2 if a > 20 else np.nan
            rows.append((year, st, issuer, f"PLAN{p}", area, "Tobacco User/Non-Tobacco User" if a > 20 else "No Preference",
                         age, round(max(rate, 1.0), 2), tob))
    df = pd.DataFrame(rows, columns=["BusinessYear", "StateCode", "IssuerId", "PlanId", "RatingAreaId", "Tobacco",
                                     "Age", "IndividualRate", "IndividualTobaccoRate"])
    df.loc[0, "IndividualRate"] = 1_000_000.0   # the kind of outlier found in the real file
    return df


@pytest.fixture(scope="session")
def rates_df():
    return synthetic_rates()


@pytest.fixture(scope="session")
def rates_csv(tmp_path_factory, rates_df):
    path = tmp_path_factory.mktemp("d") / "Rate.csv"
    rates_df.to_csv(path, index=False)
    return path
