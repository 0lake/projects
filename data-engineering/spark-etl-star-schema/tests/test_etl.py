import pytest
from pyspark.sql import functions as F

from etl_star.marts import build_marts, rating_sales_correlation
from etl_star.star import build_star


@pytest.fixture(scope="module")
def star(raw):
    s = build_star(raw)
    for df in s.values():
        df.cache()
    return s


def test_fact_keeps_every_sale_and_revenue(raw, star):
    fact = star["fact_sales"]
    assert fact.count() == raw.count()
    src_total = raw.select(F.sum(F.col("sale_total_price").cast("decimal(12,2)"))).first()[0]
    assert fact.select(F.sum("total_price")).first()[0] == src_total


def test_dimensions_are_deduplicated_by_natural_key(star):
    assert star["dim_customer"].count() == star["dim_customer"].select("email").distinct().count() == 25
    assert star["dim_seller"].count() == 8
    assert star["dim_supplier"].count() == 5
    assert star["dim_product"].count() == 20


def test_surrogate_keys_unique_and_foreign_keys_resolve(star):
    for dim, key in [("dim_customer", "customer_id"), ("dim_product", "product_id"),
                     ("dim_store", "store_id"), ("dim_seller", "seller_id")]:
        d = star[dim]
        assert d.count() == d.select(key).distinct().count()
    fact = star["fact_sales"]
    for dim, key in [("dim_customer", "customer_id"), ("dim_product", "product_id"),
                     ("dim_store", "store_id"), ("dim_seller", "seller_id")]:
        assert fact.filter(F.col(key).isNull()).count() == 0
        assert fact.join(star[dim], key, "left_anti").count() == 0
    assert star["dim_product"].join(star["dim_supplier"], "supplier_id", "left_anti").count() == 0
    assert star["dim_customer"].join(star["dim_pet"], "pet_id", "left_anti").count() == 0


def test_marts_shape_and_ranking(star):
    marts = build_marts(star)
    assert marts["mart_product_sales"].count() == 10
    assert marts["mart_store_sales"].count() == 5
    assert marts["mart_customer_sales"].count() == 10
    assert marts["mart_supplier_sales"].count() == 5
    revenue = [r[0] for r in marts["mart_product_sales"].orderBy("revenue_rank").select("total_revenue").collect()]
    assert revenue == sorted(revenue, reverse=True)


def test_time_mart_sums_to_total_revenue(star):
    time = build_marts(star)["mart_time_sales"]
    total = star["fact_sales"].select(F.sum("total_price").cast("double")).first()[0]
    assert time.select(F.sum("total_revenue")).first()[0] == pytest.approx(total, rel=1e-6)
    assert time.count() == 12
    assert time.orderBy("year", "month").first()["mom_growth_pct"] is None


def test_quality_mart_and_correlation(star):
    q = build_marts(star)["mart_product_quality"]
    assert q.count() >= 10
    assert q.filter(F.col("rating_rank_desc") == 1).count() == 1
    assert -1.0 <= rating_sales_correlation(star["fact_sales"], star["dim_product"]) <= 1.0
