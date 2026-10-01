SELECT
    category,
    SUM(quantity) AS total_quantity,
    SUM(quantity * price) AS total_sales,
    COUNT(*) AS total_orders
FROM sales
GROUP BY category
ORDER BY total_sales DESC;