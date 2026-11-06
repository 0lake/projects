"""Readers and writers for PostgreSQL, ClickHouse and MongoDB."""
from pyspark.sql import DataFrame, SparkSession

from .config import Settings

# Write order matters because of foreign keys.
STAR_WRITE_ORDER = ["dim_pet", "dim_supplier", "dim_customer", "dim_seller", "dim_product", "dim_store", "fact_sales"]


def read_raw_csv(spark: SparkSession, pattern: str) -> DataFrame:
    """Read mock_data*.csv as strings; all files share one header."""
    return spark.read.option("header", True).option("multiLine", True).option("escape", '"').csv(pattern)


def write_staging(df: DataFrame, s: Settings) -> None:
    df.write.jdbc(s.pg_url, "mock_data", mode="overwrite", properties={**s.pg_props, "truncate": "true"})


def read_staging(spark: SparkSession, s: Settings) -> DataFrame:
    return spark.read.jdbc(s.pg_url, "mock_data", properties=s.pg_props)


def write_star(star: dict, s: Settings) -> None:
    """Load in FK order. overwrite+truncate keeps the DDL (keys, indexes) and makes reruns idempotent;
    cascadeTruncate lets PostgreSQL truncate tables that are referenced by foreign keys."""
    props = {**s.pg_props, "truncate": "true", "cascadeTruncate": "true"}
    for name in STAR_WRITE_ORDER:
        star[name].write.jdbc(s.pg_url, name, mode="overwrite", properties=props)


def read_star(spark: SparkSession, s: Settings) -> dict:
    return {name: spark.read.jdbc(s.pg_url, name, properties=s.pg_props) for name in STAR_WRITE_ORDER}


def write_clickhouse(df: DataFrame, table: str, s: Settings) -> None:
    df.write.jdbc(s.ch_url, table, mode="overwrite", properties={**s.ch_props, "truncate": "true"})


def write_mongo(df: DataFrame, collection: str, s: Settings) -> None:
    (df.write.format("mongodb").mode("overwrite")
       .option("connection.uri", s.mongo_uri)
       .option("database", s.mongo_db)
       .option("collection", collection)
       .save())
