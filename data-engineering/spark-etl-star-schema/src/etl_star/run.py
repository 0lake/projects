"""CLI entry point.

    python -m etl_star.run --stage all --source "/data/mock_data*.csv"

Stages: staging (CSV -> PostgreSQL mock_data), star (mock_data -> star schema),
marts (star -> ClickHouse and MongoDB), all.
"""
import argparse
import logging

from .config import Settings
from .marts import build_marts, rating_sales_correlation
from .sinks import (read_raw_csv, read_staging, read_star, write_clickhouse, write_mongo,
                    write_staging, write_star)
from .spark_session import get_spark
from .star import build_star

log = logging.getLogger("etl_star")


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage", choices=["staging", "star", "marts", "all"], default="all")
    ap.add_argument("--source", default="/data/mock_data*.csv", help="glob of source CSV files")
    ap.add_argument("--skip-clickhouse", action="store_true")
    ap.add_argument("--skip-mongo", action="store_true")
    args = ap.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    s = Settings()
    spark = get_spark(s)
    spark.sparkContext.setLogLevel("WARN")

    if args.stage in ("staging", "all"):
        raw = read_raw_csv(spark, args.source)
        write_staging(raw, s)
        log.info("staging: %d rows loaded into PostgreSQL mock_data", raw.count())

    if args.stage in ("star", "all"):
        star = build_star(read_staging(spark, s))
        write_star(star, s)
        log.info("star: %s", {k: v.count() for k, v in star.items()})

    if args.stage in ("marts", "all"):
        star = read_star(spark, s)
        marts = build_marts(star)
        for name, df in marts.items():
            if not args.skip_clickhouse:
                write_clickhouse(df, name, s)
            if not args.skip_mongo:
                write_mongo(df, name, s)
            log.info("mart %s: %d rows written", name, df.count())
        log.info("corr(rating, units sold) = %.3f",
                 rating_sales_correlation(star["fact_sales"], star["dim_product"]))

    spark.stop()


if __name__ == "__main__":
    main()
