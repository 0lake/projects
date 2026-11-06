-- Star schema in PostgreSQL. Surrogate keys are assigned by the Spark job
-- (deterministic row_number over the natural key), so plain INT keys are used
-- instead of SERIAL. Executed automatically on first container start.

-- Staging table: raw rows of mock_data*.csv, loaded as-is (strings).
CREATE TABLE IF NOT EXISTS mock_data (
    id                     TEXT,
    customer_first_name    TEXT, customer_last_name  TEXT, customer_age TEXT,
    customer_email         TEXT, customer_country    TEXT, customer_postal_code TEXT,
    customer_pet_type      TEXT, customer_pet_name   TEXT, customer_pet_breed TEXT,
    seller_first_name      TEXT, seller_last_name    TEXT, seller_email TEXT,
    seller_country         TEXT, seller_postal_code  TEXT,
    product_name           TEXT, product_category    TEXT, product_price TEXT,
    product_quantity       TEXT, sale_date           TEXT, sale_customer_id TEXT,
    sale_seller_id         TEXT, sale_product_id     TEXT, sale_quantity TEXT,
    sale_total_price       TEXT, store_name          TEXT, store_location TEXT,
    store_city             TEXT, store_state         TEXT, store_country TEXT,
    store_phone            TEXT, store_email         TEXT, pet_category TEXT,
    product_weight         TEXT, product_color       TEXT, product_size TEXT,
    product_brand          TEXT, product_material    TEXT, product_description TEXT,
    product_rating         TEXT, product_reviews     TEXT, product_release_date TEXT,
    product_expiry_date    TEXT, supplier_name       TEXT, supplier_contact TEXT,
    supplier_email         TEXT, supplier_phone      TEXT, supplier_address TEXT,
    supplier_city          TEXT, supplier_country    TEXT
);

-- Sub-dimension: pets
CREATE TABLE IF NOT EXISTS dim_pet (
    pet_id    INT PRIMARY KEY,
    pet_type  VARCHAR(50),
    pet_name  VARCHAR(50),
    pet_breed VARCHAR(50)
);

-- Dimension: customers
CREATE TABLE IF NOT EXISTS dim_customer (
    customer_id INT PRIMARY KEY,
    first_name  VARCHAR(50),
    last_name   VARCHAR(50),
    age         INT,
    email       VARCHAR(100) UNIQUE,
    country     VARCHAR(50),
    postal_code VARCHAR(20),
    pet_id      INT REFERENCES dim_pet (pet_id)
);

-- Dimension: sellers
CREATE TABLE IF NOT EXISTS dim_seller (
    seller_id   INT PRIMARY KEY,
    first_name  VARCHAR(50),
    last_name   VARCHAR(50),
    email       VARCHAR(100) UNIQUE,
    country     VARCHAR(50),
    postal_code VARCHAR(20)
);

-- Sub-dimension: suppliers
CREATE TABLE IF NOT EXISTS dim_supplier (
    supplier_id INT PRIMARY KEY,
    name        VARCHAR(100),
    contact     VARCHAR(100),
    email       VARCHAR(100) UNIQUE,
    phone       VARCHAR(30),
    address     VARCHAR(150),
    city        VARCHAR(50),
    country     VARCHAR(50)
);

-- Dimension: products
CREATE TABLE IF NOT EXISTS dim_product (
    product_id   INT PRIMARY KEY,
    name         VARCHAR(100),
    category     VARCHAR(50),
    price        NUMERIC(10, 2),
    weight       NUMERIC(10, 2),
    color        VARCHAR(30),
    size         VARCHAR(30),
    brand        VARCHAR(50),
    material     VARCHAR(50),
    description  TEXT,
    rating       NUMERIC(3, 2),
    reviews      INT,
    release_date DATE,
    expiry_date  DATE,
    supplier_id  INT REFERENCES dim_supplier (supplier_id)
);

-- Dimension: stores
CREATE TABLE IF NOT EXISTS dim_store (
    store_id INT PRIMARY KEY,
    name     VARCHAR(100),
    location VARCHAR(100),
    city     VARCHAR(50),
    state    VARCHAR(50),
    country  VARCHAR(50),
    phone    VARCHAR(30),
    email    VARCHAR(100)
);

-- Fact: sales
CREATE TABLE IF NOT EXISTS fact_sales (
    sale_id     INT PRIMARY KEY,
    sale_date   DATE,
    customer_id INT REFERENCES dim_customer (customer_id),
    seller_id   INT REFERENCES dim_seller (seller_id),
    product_id  INT REFERENCES dim_product (product_id),
    store_id    INT REFERENCES dim_store (store_id),
    quantity    INT,
    total_price NUMERIC(12, 2)
);

CREATE INDEX IF NOT EXISTS ix_fact_sales_date     ON fact_sales (sale_date);
CREATE INDEX IF NOT EXISTS ix_fact_sales_product  ON fact_sales (product_id);
CREATE INDEX IF NOT EXISTS ix_fact_sales_store    ON fact_sales (store_id);
CREATE INDEX IF NOT EXISTS ix_fact_sales_customer ON fact_sales (customer_id);
