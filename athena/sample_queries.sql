-- Description: Revenue and sales analytics

-- Daily revenue
SELECT
    order_date,
    SUM(total_amount) AS total_revenue
FROM processed_orders
GROUP BY order_date
ORDER BY order_date;

-- --------------------------------------------

-- Top selling products
SELECT
    product,
    SUM(quantity) AS total_units
FROM processed_orders
GROUP BY product
ORDER BY total_units DESC;

-- --------------------------------------------

-- Average order value
SELECT
    AVG(total_amount) AS avg_order_value
FROM processed_orders;

