-- SQL script to create the PRODUCT_NOMENCLATURE table
-- This table contains product metadata

CREATE TABLE PRODUCT_NOMENCLATURE (
    product_id INTEGER PRIMARY KEY,  -- Unique product identifier
    product_type TEXT NOT NULL,  -- Product type (DECO or MEUBLE)
    product_name TEXT NOT NULL  -- Name of the product
);

--Adding indexes for performance optimization
CREATE INDEX idx_product_nomenclature_product_type ON product_nomenclature(product_type);
CREATE INDEX idx_product_nomenclature_product_name ON product_nomenclature(product_name);

--Adding comments to the table: not available in sqlite3
-- COMMENT ON TABLE product_nomenclature IS 'This table contains product metadata';
-- COMMENT ON COLUMN product_nomenclature.product_id IS 'Unique product identifier';
-- COMMENT ON COLUMN product_nomenclature.product_type IS 'Product type (DECO or MEUBLE)';
-- COMMENT ON COLUMN product_nomenclature.product_name IS 'Name of the product';
