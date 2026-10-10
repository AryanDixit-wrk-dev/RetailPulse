-- Total sales
SELECT
    SUM(total_sales) AS total_sales
FROM fact_sales;


-- Total orders
SELECT
    COUNT(DISTINCT order_id) AS total_orders
FROM fact_sales;


-- Total quantity sold
SELECT
    SUM(quantity) AS total_quantity
FROM fact_sales;


-- Sales by product
SELECT
    p.product_name,
    SUM(f.quantity) AS total_quantity,
    SUM(f.total_sales) AS total_sales
FROM fact_sales f
JOIN dim_product p
    ON f.product_key = p.product_key
GROUP BY p.product_name
ORDER BY total_sales DESC;


-- Sales by category
SELECT
    c.category_name,
    SUM(f.quantity) AS total_quantity,
    SUM(f.total_sales) AS total_sales
FROM fact_sales f
JOIN dim_category c
    ON f.category_key = c.category_key
GROUP BY c.category_name
ORDER BY total_sales DESC;


-- Sales by date
SELECT
    d.full_date,
    SUM(f.quantity) AS total_quantity,
    SUM(f.total_sales) AS total_sales,
    COUNT(DISTINCT f.order_id) AS total_orders
FROM fact_sales f
JOIN dim_date d
    ON f.date_key = d.date_key
GROUP BY d.full_date
ORDER BY d.full_date;
