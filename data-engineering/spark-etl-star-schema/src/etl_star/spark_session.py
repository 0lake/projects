"""SparkSession factory."""
from pyspark.sql import SparkSession

from .config import PACKAGES, Settings


def get_spark(settings: Settings, with_connectors: bool = True) -> SparkSession:
    builder = (
        SparkSession.builder.appName("etl_star")
        .master(settings.spark_master)
        .config("spark.sql.legacy.timeParserPolicy", "CORRECTED")
        .config("spark.sql.shuffle.partitions", "8")
    )
    if with_connectors:
        builder = builder.config("spark.jars.packages", PACKAGES)
    return builder.getOrCreate()
