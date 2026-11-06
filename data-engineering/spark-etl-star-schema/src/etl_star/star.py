"""Build the star schema from the raw mock_data rows.

Pure DataFrame -> DataFrame functions, so the logic is testable without any database.
Dimensions are deduplicated by natural keys, and every dimension row gets a deterministic
surrogate key (row_number over the natural key).
"""
from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

# target column -> source column in mock_data
PET = {"pet_type": "customer_pet_type", "pet_name": "customer_pet_name", "pet_breed": "customer_pet_breed"}
CUSTOMER = {
    "first_name": "customer_first_name", "last_name": "customer_last_name", "age": "customer_age",
    "email": "customer_email", "country": "customer_country", "postal_code": "customer_postal_code",
}
SELLER = {
    "first_name": "seller_first_name", "last_name": "seller_last_name", "email": "seller_email",
    "country": "seller_country", "postal_code": "seller_postal_code",
}
SUPPLIER = {
    "name": "supplier_name", "contact": "supplier_contact", "email": "supplier_email",
    "phone": "supplier_phone", "address": "supplier_address", "city": "supplier_city",
    "country": "supplier_country",
}
PRODUCT = {
    "name": "product_name", "category": "product_category", "price": "product_price",
    "weight": "product_weight", "color": "product_color", "size": "product_size",
    "brand": "product_brand", "material": "product_material", "description": "product_description",
    "rating": "product_rating", "reviews": "product_reviews",
    "release_date": "product_release_date", "expiry_date": "product_expiry_date",
}
STORE = {
    "name": "store_name", "location": "store_location", "city": "store_city", "state": "store_state",
    "country": "store_country", "phone": "store_phone", "email": "store_email",
}

# Natural keys (source column names)
PET_KEY = list(PET.values())
CUSTOMER_KEY = ["customer_email"]
SELLER_KEY = ["seller_email"]
SUPPLIER_KEY = ["supplier_email"]
PRODUCT_KEY = list(PRODUCT.values()) + ["supplier_email"]
STORE_KEY = ["store_name", "store_location", "store_city", "store_state", "store_country", "store_email"]

DATE_FORMATS = ("M/d/yyyy", "yyyy-MM-dd", "d.M.yyyy")


def _parse_date(col: str):
    return F.coalesce(*[F.to_date(F.col(col), fmt) for fmt in DATE_FORMATS])


def typed(raw: DataFrame) -> DataFrame:
    """Cast the all-string raw rows to proper types and add a stable row number."""
    df = (
        raw
        .withColumn("customer_age", F.col("customer_age").cast("int"))
        .withColumn("product_price", F.col("product_price").cast("decimal(10,2)"))
        .withColumn("product_weight", F.col("product_weight").cast("decimal(10,2)"))
        .withColumn("product_rating", F.col("product_rating").cast("decimal(3,2)"))
        .withColumn("product_reviews", F.col("product_reviews").cast("int"))
        .withColumn("product_release_date", _parse_date("product_release_date"))
        .withColumn("product_expiry_date", _parse_date("product_expiry_date"))
        .withColumn("sale_date", _parse_date("sale_date"))
        .withColumn("sale_quantity", F.col("sale_quantity").cast("int"))
        .withColumn("sale_total_price", F.col("sale_total_price").cast("decimal(12,2)"))
    )
    return df.dropna(subset=["sale_date", "sale_quantity", "sale_total_price"])


def _dimension(base: DataFrame, id_col: str, mapping: dict, key: list) -> DataFrame:
    """Distinct rows by natural key + surrogate id. Returns source-named columns + id."""
    cols = list(dict.fromkeys(list(mapping.values()) + key))
    dedup = base.select(*cols).dropDuplicates(key)
    # Global window: fine for a lab-sized dimension. For billions of rows use hash keys.
    return dedup.withColumn(id_col, F.row_number().over(Window.orderBy(*key)))


def _final(dim: DataFrame, id_col: str, mapping: dict, extra: list = ()) -> DataFrame:
    return dim.select(id_col, *[F.col(src).alias(tgt) for tgt, src in mapping.items()], *extra)


def _attach_id(left: DataFrame, dim: DataFrame, key: list, id_col: str) -> DataFrame:
    """Null-safe join of dimension id onto the base rows."""
    right = dim.select(*key, id_col).alias("r")
    cond = None
    for c in key:
        e = F.col(f"l.{c}").eqNullSafe(F.col(f"r.{c}"))
        cond = e if cond is None else cond & e
    return left.alias("l").join(right, cond, "left").select("l.*", f"r.{id_col}")


def build_star(raw: DataFrame) -> dict:
    """Return dict of DataFrames: dim_pet, dim_customer, dim_seller, dim_supplier,
    dim_product, dim_store, fact_sales."""
    base = typed(raw).withColumn("_row", F.row_number().over(Window.orderBy("id", "sale_date")))

    pet = _dimension(base, "pet_id", PET, PET_KEY)
    customer = _attach_id(_dimension(base, "customer_id", CUSTOMER, CUSTOMER_KEY).join(
        base.select(*CUSTOMER_KEY, *PET_KEY).dropDuplicates(CUSTOMER_KEY), CUSTOMER_KEY, "left"),
        pet, PET_KEY, "pet_id")
    seller = _dimension(base, "seller_id", SELLER, SELLER_KEY)
    supplier = _dimension(base, "supplier_id", SUPPLIER, SUPPLIER_KEY)
    product = _attach_id(_dimension(base, "product_id", PRODUCT, PRODUCT_KEY),
                         supplier, SUPPLIER_KEY, "supplier_id")
    store = _dimension(base, "store_id", STORE, STORE_KEY)

    fact = base
    for dim, key, id_col in [
        (customer, CUSTOMER_KEY, "customer_id"),
        (seller, SELLER_KEY, "seller_id"),
        (product, PRODUCT_KEY, "product_id"),
        (store, STORE_KEY, "store_id"),
    ]:
        fact = _attach_id(fact, dim, key, id_col)

    fact_sales = fact.select(
        F.col("_row").alias("sale_id"), "sale_date", "customer_id", "seller_id", "product_id",
        "store_id", F.col("sale_quantity").alias("quantity"), F.col("sale_total_price").alias("total_price"),
    )
    return {
        "dim_pet": _final(pet, "pet_id", PET),
        "dim_customer": _final(customer, "customer_id", CUSTOMER, ["pet_id"]),
        "dim_seller": _final(seller, "seller_id", SELLER),
        "dim_supplier": _final(supplier, "supplier_id", SUPPLIER),
        "dim_product": _final(product, "product_id", PRODUCT, ["supplier_id"]),
        "dim_store": _final(store, "store_id", STORE),
        "fact_sales": fact_sales,
    }
