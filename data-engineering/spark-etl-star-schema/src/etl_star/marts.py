"""Report marts built from the star schema. Pure DataFrame -> DataFrame functions."""
from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F


def _rank(df: DataFrame, order_col: str, rank_col: str, top: int) -> DataFrame:
    # The aggregated frame is small, so a global window is acceptable here.
    w = Window.orderBy(F.desc(order_col), F.asc(df.columns[0]))
    return df.withColumn(rank_col, F.row_number().over(w).cast("int")).filter(F.col(rank_col) <= top)


def product_sales(fact: DataFrame, product: DataFrame, top: int = 10) -> DataFrame:
    agg = (
        fact.join(product, "product_id")
        .groupBy("product_id", F.col("name").alias("product_name"), "category", "rating", "reviews")
        .agg(F.sum("total_price").alias("total_revenue"), F.sum("quantity").alias("total_quantity"))
        .select(
            "product_id", "product_name", "category",
            F.round("total_revenue", 2).cast("double").alias("total_revenue"),
            F.col("total_quantity").cast("long").alias("total_quantity"),
            F.col("rating").cast("double").alias("avg_rating"),
            F.col("reviews").cast("int").alias("total_reviews"),
        )
    )
    return _rank(agg, "total_revenue", "revenue_rank", top)


def store_sales(fact: DataFrame, store: DataFrame, top: int = 5) -> DataFrame:
    agg = (
        fact.join(store, "store_id")
        .groupBy("store_id", F.col("name").alias("store_name"), "city", "country")
        .agg(F.round(F.sum("total_price"), 2).cast("double").alias("total_revenue"),
             F.round(F.avg("total_price"), 2).cast("double").alias("avg_check"))
    )
    return _rank(agg, "total_revenue", "revenue_rank", top)


def time_sales(fact: DataFrame) -> DataFrame:
    monthly = (
        fact.withColumn("year", F.year("sale_date")).withColumn("month", F.month("sale_date"))
        .groupBy("year", "month")
        .agg(F.sum("total_price").alias("revenue"), F.avg("total_price").alias("avg_order"),
             F.count("*").alias("orders"))
    )
    w = Window.orderBy("year", "month")
    prev = F.lag("revenue").over(w)
    return monthly.select(
        F.col("year").cast("int"), F.col("month").cast("int"),
        F.format_string("%04d-%02d", "year", "month").alias("year_month"),
        F.round("revenue", 2).cast("double").alias("total_revenue"),
        F.round("avg_order", 2).cast("double").alias("avg_order_size"),
        F.col("orders").cast("long").alias("orders"),
        F.round((F.col("revenue") - prev) / prev * 100, 2).cast("double").alias("mom_growth_pct"),
    ).orderBy("year", "month")


def customer_sales(fact: DataFrame, customer: DataFrame, top: int = 10) -> DataFrame:
    agg = (
        fact.join(customer, "customer_id")
        .groupBy("customer_id", "first_name", "last_name", "country")
        .agg(F.round(F.sum("total_price"), 2).cast("double").alias("total_spent"),
             F.round(F.avg("total_price"), 2).cast("double").alias("avg_check"),
             F.count("*").cast("long").alias("orders"))
    )
    return _rank(agg, "total_spent", "spending_rank", top)


def supplier_sales(fact: DataFrame, product: DataFrame, supplier: DataFrame, top: int = 5) -> DataFrame:
    agg = (
        fact.join(product.select("product_id", "price", "supplier_id"), "product_id")
        .join(supplier, "supplier_id")
        .groupBy("supplier_id", F.col("name").alias("supplier_name"), "country")
        .agg(F.round(F.sum("total_price"), 2).cast("double").alias("total_revenue"),
             F.round(F.avg("price"), 2).cast("double").alias("avg_product_price"))
    )
    return _rank(agg, "total_revenue", "revenue_rank", top)


def product_quality(fact: DataFrame, product: DataFrame, top: int = 10) -> DataFrame:
    """Top/bottom products by rating and top by reviews, with units sold."""
    sold = fact.groupBy("product_id").agg(F.sum("quantity").alias("total_sold"))
    df = (
        product.join(sold, "product_id", "left")
        .select(
            "product_id", F.col("name").alias("product_name"), "category",
            F.col("rating").cast("double").alias("rating"),
            F.col("reviews").cast("int").alias("reviews"),
            F.coalesce("total_sold", F.lit(0)).cast("long").alias("total_sold"),
        )
        .dropna(subset=["rating", "reviews"])
    )
    tie = F.asc("product_id")
    ranked = (
        df.withColumn("rating_rank_desc", F.row_number().over(Window.orderBy(F.desc("rating"), tie)).cast("int"))
        .withColumn("rating_rank_asc", F.row_number().over(Window.orderBy(F.asc("rating"), tie)).cast("int"))
        .withColumn("reviews_rank", F.row_number().over(Window.orderBy(F.desc("reviews"), tie)).cast("int"))
    )
    return ranked.filter(
        (F.col("rating_rank_desc") <= top) | (F.col("rating_rank_asc") <= top) | (F.col("reviews_rank") <= top)
    )


def rating_sales_correlation(fact: DataFrame, product: DataFrame) -> float:
    """Pearson correlation between product rating and units sold, over all products."""
    sold = fact.groupBy("product_id").agg(F.sum("quantity").alias("sold"))
    df = product.join(sold, "product_id", "left").select(
        F.col("rating").cast("double").alias("rating"), F.coalesce("sold", F.lit(0)).cast("double").alias("sold"))
    return df.stat.corr("rating", "sold")


def build_marts(star: dict) -> dict:
    fact = star["fact_sales"]
    return {
        "mart_product_sales": product_sales(fact, star["dim_product"]),
        "mart_store_sales": store_sales(fact, star["dim_store"]),
        "mart_time_sales": time_sales(fact),
        "mart_customer_sales": customer_sales(fact, star["dim_customer"]),
        "mart_supplier_sales": supplier_sales(fact, star["dim_product"], star["dim_supplier"]),
        "mart_product_quality": product_quality(fact, star["dim_product"]),
    }
