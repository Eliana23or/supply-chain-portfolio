-- ================================================
-- STEP 3: Create Profitability Fact Table
-- Calcula ganancia bruta y métricas de inventario
-- ================================================

DROP TABLE IF EXISTS sc_analytics.fact_profitability;

CREATE TABLE sc_analytics.fact_profitability AS
SELECT
    sku,
    product_type,
    supplier_name,
    location,
    price,
    number_of_products_sold,
    revenue_generated,
    manufacturing_costs,
    shipping_costs,
    costs                                               AS logistics_costs,
    stock_levels,

    -- Ganancia Bruta = Ingresos - Todos los costos
    (revenue_generated 
     - manufacturing_costs 
     - shipping_costs 
     - costs)                                           AS gross_profit,

    -- Margen de ganancia en porcentaje
    ROUND(
        (revenue_generated - manufacturing_costs 
         - shipping_costs - costs)
        / NULLIF(revenue_generated, 0) * 100, 2
    )                                                   AS profit_margin_pct,

    -- Ratio stock vs ventas (alto = inventario estancado)
    ROUND(
        stock_levels::NUMERIC
        / NULLIF(number_of_products_sold, 0), 4
    )                                                   AS stock_to_sales_ratio,

    defect_rates,
    inspection_results,
    transportation_modes,
    routes,
    shipping_carriers

FROM sc_analytics.stg_supply_chain;

-- Verificar resultado
SELECT COUNT(*) AS total_skus FROM sc_analytics.fact_profitability;
