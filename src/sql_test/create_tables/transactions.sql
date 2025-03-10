-- SQL script to create the TRANSACTIONS table
-- Renamed to TRANSACTIONS to avoid conflict with the TRANSACTION table in the sql_test/create_tables/transactions.sql file
-- This table contains transactional data

CREATE TABLE TRANSACTIONS
 (
    transaction_id INTEGER PRIMARY KEY, -- Unique identifier for the transaction
    date DATE NOT NULL,  -- The date when the order was placed
    order_id INTEGER NOT NULL,  -- Unique identifier for the order
    client_id INTEGER NOT NULL,  -- Unique identifier for the client
    prod_id INTEGER NOT NULL,  -- Unique identifier for the purchased product
    prod_price REAL NOT NULL CHECK (prod_price >= 0), -- Unit price of the product
    prod_qty INTEGER NOT NULL CHECK (prod_qty > 0), -- Quantity of the product purchased
    FOREIGN KEY (prod_id) REFERENCES PRODUCT_NOMENCLATURE(product_id)  -- Foreign key reference
);

-- Adding indexes for performance optimization
CREATE INDEX idx_transactions_date ON TRANSACTIONS(date);
CREATE INDEX idx_transactions_order_id ON transactions(order_id);
CREATE INDEX idx_transactions_client_id ON transactions(client_id);
CREATE INDEX idx_transactions_prod_id ON transactions(prod_id);

-- Adding comments to the table: not available in sqlite3
-- COMMENT ON TABLE transactions IS 'This table contains transactional data';
-- COMMENT ON COLUMN transactions.transaction_id IS 'Unique identifier for the transaction';
-- COMMENT ON COLUMN transactions.date IS 'The date when the order was placed';
-- COMMENT ON COLUMN transactions.order_id IS 'Unique identifier for the order';
-- COMMENT ON COLUMN transactions.client_id IS 'Unique identifier for the client';
-- COMMENT ON COLUMN transactions.prod_id IS 'Unique identifier for the purchased product';
-- COMMENT ON COLUMN transactions.prod_price IS 'Unit price of the product';
-- COMMENT ON COLUMN transactions.prod_qty IS 'Quantity of the product purchased';
