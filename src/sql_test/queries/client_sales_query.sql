-- SQL query to determine per client the sales for MEUBLE and DECO products
-- from January 1, 2019, to December 31, 2019
--
-- We use an INNER JOIN to ensure that only transactions with valid product IDs
-- that exist in the PRODUCT_NOMENCLATURE table are included. This maintains
-- data integrity by excluding transactions with missing or invalid product references.

SELECT
    t.client_id AS client_id,
    SUM(CASE WHEN pn.product_type = 'MEUBLE' THEN t.prod_price * t.prod_qty ELSE 0 END) AS sales_meuble,
    SUM(CASE WHEN pn.product_type = 'DECO' THEN t.prod_price * t.prod_qty ELSE 0 END) AS sales_deco
FROM
    TRANSACTIONS t
INNER JOIN
    PRODUCT_NOMENCLATURE pn ON t.prod_id = pn.product_id
WHERE
    t.date BETWEEN DATE('2019-01-01') AND DATE('2019-12-31')
GROUP BY
    t.client_id
ORDER BY
    t.client_id;
