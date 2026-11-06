-- Report marts in ClickHouse. Tables are created on first container start;
-- the Spark job truncates and refills them, so reruns are idempotent.
-- Tables and columns must exist beforehand because Spark appends over JDBC.

CREATE TABLE IF NOT EXISTS mart_product_sales
(
    product_id     Int32,
    product_name   String,
    category       String,
    total_revenue  Float64,
    total_quantity Int64,
    avg_rating     Float64,
    total_reviews  Int32,
    revenue_rank   Int32
) ENGINE = MergeTree ORDER BY (revenue_rank, product_id);

CREATE TABLE IF NOT EXISTS mart_store_sales
(
    store_id      Int32,
    store_name    String,
    city          String,
    country       String,
    total_revenue Float64,
    avg_check     Float64,
    revenue_rank  Int32
) ENGINE = MergeTree ORDER BY (revenue_rank, store_id);

CREATE TABLE IF NOT EXISTS mart_time_sales
(
    year             Int32,
    month            Int32,
    year_month       String,
    total_revenue    Float64,
    avg_order_size   Float64,
    orders           Int64,
    mom_growth_pct   Nullable(Float64)
) ENGINE = MergeTree ORDER BY (year, month);

CREATE TABLE IF NOT EXISTS mart_customer_sales
(
    customer_id   Int32,
    first_name    String,
    last_name     String,
    country       String,
    total_spent   Float64,
    avg_check     Float64,
    orders        Int64,
    spending_rank Int32
) ENGINE = MergeTree ORDER BY (spending_rank, customer_id);

CREATE TABLE IF NOT EXISTS mart_supplier_sales
(
    supplier_id       Int32,
    supplier_name     String,
    country           String,
    total_revenue     Float64,
    avg_product_price Float64,
    revenue_rank      Int32
) ENGINE = MergeTree ORDER BY (revenue_rank, supplier_id);

CREATE TABLE IF NOT EXISTS mart_product_quality
(
    product_id       Int32,
    product_name     String,
    category         String,
    rating           Float64,
    reviews          Int32,
    total_sold       Int64,
    rating_rank_desc Int32,
    rating_rank_asc  Int32,
    reviews_rank     Int32
) ENGINE = MergeTree ORDER BY (product_id);
