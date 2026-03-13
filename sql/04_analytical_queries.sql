-- ================================================
-- STEP 4: Analytical Queries
-- Pareto Analysis + Inventory Risk
-- ================================================


-- ── QUERY 1: Análisis Pareto ABC ─────────────────
-- Clasifica SKUs por contribución a la ganancia total

WITH profit_ranked AS (
    SELECT
        sku,
        product_type,
        supplier_name,
        gross_profit,
        profit_margin_pct,
        SUM(gross_profit) OVER ()                       AS total_profit,
        SUM(gross_profit) OVER (
            ORDER BY gross_profit DESC
            ROWS UNBOUNDED PRECEDING
        )                                               AS cumulative_profit,
        ROW_NUMBER() OVER (
            ORDER BY gross_profit DESC
        )                                               AS rank
    FROM sc_analytics.fact_profitability
    WHERE gross_profit > 0
),
pareto AS (
    SELECT *,
        ROUND(
            cumulative_profit / total_profit * 100, 2
        )                                               AS cumulative_pct,
        CASE
            WHEN cumulative_profit / total_profit <= 0.80 
                THEN 'A - Top 80%'
            WHEN cumulative_profit / total_profit <= 0.95 
                THEN 'B - Mid 15%'
            ELSE 'C - Tail 5%'
        END                                             AS abc_class
    FROM profit_ranked
)
SELECT * FROM pareto ORDER BY rank;


-- ── QUERY 2: Riesgo de Inventario Obsoleto ───────
-- Identifica SKUs con stock alto, ventas bajas y defectos

SELECT
    sku,
    product_type,
    supplier_name,
    stock_levels,
    number_of_products_sold,
    stock_to_sales_ratio,
    defect_rates,
    inspection_results,
    gross_profit,
    profit_margin_pct,
    CASE
        WHEN stock_to_sales_ratio > 0.5
         AND defect_rates > 3.0
            THEN 'HIGH RISK - Liquidate'
        WHEN stock_to_sales_ratio > 0.3
         AND inspection_results = 'Fail'
            THEN 'MEDIUM RISK - Review'
        ELSE 'LOW RISK - Monitor'
    END                                                 AS inventory_risk
FROM sc_analytics.fact_profitability
ORDER BY stock_to_sales_ratio DESC;


-- ── QUERY 3: Resumen por Categoría ───────────────

SELECT
    product_type,
    COUNT(sku)                                          AS total_skus,
    ROUND(SUM(revenue_generated), 2)                    AS total_revenue,
    ROUND(SUM(gross_profit), 2)                         AS total_gross_profit,
    ROUND(AVG(profit_margin_pct), 2)                    AS avg_margin_pct,
    ROUND(AVG(defect_rates), 4)                         AS avg_defect_rate
FROM sc_analytics.fact_profitability
GROUP BY product_type
ORDER BY total_gross_profit DESC;


-- ── QUERY 4: Resumen por Proveedor ───────────────

SELECT
    supplier_name,
    COUNT(sku)                                          AS total_skus,
    ROUND(AVG(defect_rates), 4)                         AS avg_defect_rate,
    COUNT(CASE WHEN inspection_results = 'Fail' 
               THEN 1 END)                              AS failed_inspections,
    ROUND(SUM(gross_profit), 2)                         AS total_gross_profit,
    ROUND(AVG(profit_margin_pct), 2)                    AS avg_margin_pct
FROM sc_analytics.fact_profitability
GROUP BY supplier_name
ORDER BY failed_inspections DESC;
