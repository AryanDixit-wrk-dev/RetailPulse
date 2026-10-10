CREATE TABLE IF NOT EXISTS dim_category (
    category_key BIGSERIAL PRIMARY KEY,
    category_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS dim_product (
    product_key BIGSERIAL PRIMARY KEY,
    product_name TEXT NOT NULL UNIQUE,
    category_key BIGINT NOT NULL REFERENCES dim_category(category_key)
);

CREATE TABLE IF NOT EXISTS dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name TEXT NOT NULL,
    quarter INTEGER NOT NULL,
    day INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_sales (
    sales_key BIGSERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL UNIQUE,
    date_key INTEGER NOT NULL REFERENCES dim_date(date_key),
    product_key BIGINT NOT NULL REFERENCES dim_product(product_key),
    category_key BIGINT NOT NULL REFERENCES dim_category(category_key),
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(12, 2) NOT NULL,
    total_sales NUMERIC(14, 2) NOT NULL,
    pipeline_run_id BIGINT REFERENCES pipeline_runs(run_id)
);