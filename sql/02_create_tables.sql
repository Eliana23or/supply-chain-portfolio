-- ================================================
-- STEP 2: Create Staging Table
-- ================================================

CREATE TABLE IF NOT EXISTS sc_analytics.stg_supply_chain (
    product_type            VARCHAR(50),
    sku                     VARCHAR(20) PRIMARY KEY,
    price                   NUMERIC(10,2),
    availability            INTEGER,
    number_of_products_sold INTEGER,
    revenue_generated       NUMERIC(12,2),
    customer_demographics   VARCHAR(50),
    stock_levels            INTEGER,
    lead_times              INTEGER,
    order_quantities        INTEGER,
    shipping_times          INTEGER,
    shipping_carriers       VARCHAR(50),
    shipping_costs          NUMERIC(10,2),
    supplier_name           VARCHAR(50),
    location                VARCHAR(50),
    lead_time               INTEGER,
    production_volumes      INTEGER,
    manufacturing_lead_time INTEGER,
    manufacturing_costs     NUMERIC(10,2),
    inspection_results      VARCHAR(20),
    defect_rates            NUMERIC(6,4),
    transportation_modes    VARCHAR(20),
    routes                  VARCHAR(20),
    costs                   NUMERIC(10,2)
);
