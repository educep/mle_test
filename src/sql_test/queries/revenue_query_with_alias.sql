-- SQL query to find the total revenue (sales amount) day by day for the year 2019
-- The result is sorted by date and uses AS to name fields clearly

SELECT date AS transaction_date, SUM(prod_price * prod_qty) AS total_revenue
FROM TRANSACTIONS
-- WHERE date BETWEEN '2019-01-01' AND '2019-12-31'
--  For cross-database compatibility: BigQuery, PostgreSQL, SQLite3 (for quick testing)
WHERE date BETWEEN DATE('2019-01-01') AND DATE('2019-12-31') -- BIGQUERY
GROUP BY transaction_date
ORDER BY transaction_date;
