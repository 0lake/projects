import random
from datetime import date, timedelta

import pytest
from pyspark.sql import SparkSession

from etl_star.sinks import read_raw_csv  # noqa: F401  (import check)

COLUMNS = [
    "id", "customer_first_name", "customer_last_name", "customer_age", "customer_email", "customer_country",
    "customer_postal_code", "customer_pet_type", "customer_pet_name", "customer_pet_breed",
    "seller_first_name", "seller_last_name", "seller_email", "seller_country", "seller_postal_code",
    "product_name", "product_category", "product_price", "product_quantity", "sale_date",
    "sale_customer_id", "sale_seller_id", "sale_product_id", "sale_quantity", "sale_total_price",
    "store_name", "store_location", "store_city", "store_state", "store_country", "store_phone", "store_email",
    "pet_category", "product_weight", "product_color", "product_size", "product_brand", "product_material",
    "product_description", "product_rating", "product_reviews", "product_release_date", "product_expiry_date",
    "supplier_name", "supplier_contact", "supplier_email", "supplier_phone", "supplier_address",
    "supplier_city", "supplier_country",
]


def make_rows(n=300, seed=7):
    rnd = random.Random(seed)
    customers = [(f"C{i}", f"Last{i}", 20 + i, f"c{i}@mail.test", rnd.choice(["USA", "Brazil", "China"]),
                  f"{10000 + i}", rnd.choice(["Dog", "Cat", "Bird"]), f"Pet{i % 5}", rnd.choice(["A", "B"]))
                 for i in range(25)]
    sellers = [(f"S{i}", f"SL{i}", f"s{i}@shop.test", rnd.choice(["USA", "Spain"]), f"{20000 + i}") for i in range(8)]
    suppliers = [(f"Sup{i}", f"Contact{i}", f"sup{i}@sup.test", f"+1{i:07d}", f"Addr {i}", f"City{i}",
                  rnd.choice(["China", "Russia"])) for i in range(5)]
    products = []
    for i in range(20):
        sup = suppliers[i % len(suppliers)]
        products.append((f"Product{i}", rnd.choice(["Food", "Toy", "Cage"]), round(rnd.uniform(5, 90), 2),
                         round(rnd.uniform(0.2, 5), 2), "red", "M", f"Brand{i % 4}", "metal", f"desc {i}",
                         round(rnd.uniform(1, 5), 1), rnd.randint(1, 1000), "1/15/2020", "12/31/2030", sup))
    stores = [(f"Store{i}", f"Loc{i}", f"Town{i}", "CA", rnd.choice(["USA", "China"]), f"+7{i:07d}",
               f"st{i}@store.test") for i in range(6)]
    start, rows = date(2021, 1, 1), []
    for k in range(n):
        c, s, p, st = rnd.choice(customers), rnd.choice(sellers), rnd.choice(products), rnd.choice(stores)
        qty = rnd.randint(1, 5)
        d = start + timedelta(days=rnd.randint(0, 364))
        sup = p[13]
        rows.append((
            str(k + 1), c[0], c[1], str(c[2]), c[3], c[4], c[5], c[6], c[7], c[8],
            s[0], s[1], s[2], s[3], s[4],
            p[0], p[1], str(p[2]), "100", f"{d.month}/{d.day}/{d.year}", "1", "1", "1", str(qty),
            f"{qty * p[2]:.2f}", st[0], st[1], st[2], st[3], st[4], st[5], st[6],
            "Dogs", str(p[3]), p[4], p[5], p[6], p[7], p[8], str(p[9]), str(p[10]), p[11], p[12],
            sup[0], sup[1], sup[2], sup[3], sup[4], sup[5], sup[6],
        ))
    return rows


@pytest.fixture(scope="session")
def spark():
    s = (SparkSession.builder.master("local[2]").appName("tests")
         .config("spark.sql.shuffle.partitions", "2")
         .config("spark.sql.legacy.timeParserPolicy", "CORRECTED")
         .config("spark.ui.enabled", "false").getOrCreate())
    yield s
    s.stop()


@pytest.fixture(scope="session")
def raw(spark):
    return spark.createDataFrame(make_rows(), COLUMNS)
