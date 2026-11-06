"""Connection settings, read from environment variables (see .env.example)."""
import os
from dataclasses import dataclass
from urllib.parse import quote_plus

PACKAGES = ",".join([
    "org.postgresql:postgresql:42.6.0",
    "ru.yandex.clickhouse:clickhouse-jdbc:0.3.2",
    "org.mongodb.spark:mongo-spark-connector_2.12:10.2.0",
])


def _env(name: str, default: str) -> str:
    return os.environ.get(name, default)


@dataclass(frozen=True)
class Settings:
    spark_master: str = _env("SPARK_MASTER", "local[*]")

    pg_host: str = _env("POSTGRES_HOST", "localhost")
    pg_port: str = _env("POSTGRES_PORT", "5434")
    pg_db: str = _env("POSTGRES_DB", "bigdata_lab")
    pg_user: str = _env("POSTGRES_USER", "etl_user")
    pg_password: str = _env("POSTGRES_PASSWORD", "")

    ch_host: str = _env("CLICKHOUSE_HOST", "localhost")
    ch_port: str = _env("CLICKHOUSE_PORT", "8124")
    ch_db: str = _env("CLICKHOUSE_DB", "lab")
    ch_user: str = _env("CLICKHOUSE_USER", "etl_user")
    ch_password: str = _env("CLICKHOUSE_PASSWORD", "")

    mongo_host: str = _env("MONGO_HOST", "localhost")
    mongo_port: str = _env("MONGO_PORT", "27018")
    mongo_db: str = _env("MONGO_DB", "bigdata_lab")
    mongo_user: str = _env("MONGO_INITDB_ROOT_USERNAME", "etl_user")
    mongo_password: str = _env("MONGO_INITDB_ROOT_PASSWORD", "")

    @property
    def pg_url(self) -> str:
        return f"jdbc:postgresql://{self.pg_host}:{self.pg_port}/{self.pg_db}"

    @property
    def pg_props(self) -> dict:
        return {"user": self.pg_user, "password": self.pg_password, "driver": "org.postgresql.Driver"}

    @property
    def ch_url(self) -> str:
        return f"jdbc:clickhouse://{self.ch_host}:{self.ch_port}/{self.ch_db}"

    @property
    def ch_props(self) -> dict:
        return {
            "user": self.ch_user,
            "password": self.ch_password,
            "driver": "ru.yandex.clickhouse.ClickHouseDriver",
        }

    @property
    def mongo_uri(self) -> str:
        user, pwd = quote_plus(self.mongo_user), quote_plus(self.mongo_password)
        return f"mongodb://{user}:{pwd}@{self.mongo_host}:{self.mongo_port}/?authSource=admin"
