import pandas as pd
import numpy as np

# Cargar CSV original
df = pd.read_csv('data/raw/supply_chain_data.csv')

# Redondear columnas numéricas
cols_redondear = [
    'price', 'revenue_generated', 'shipping_costs',
    'manufacturing_costs', 'costs', 'defect_rates'
]
for col in cols_redondear:
    df[col] = df[col].round(2)

# Calcular métricas
df['gross_profit'] = (
    df['revenue_generated']
    - df['manufacturing_costs']
    - df['shipping_costs']
    - df['costs']
).round(2)

df['profit_margin_pct'] = (
    df['gross_profit'] / df['revenue_generated'] * 100
).round(2)

df['stock_to_sales_ratio'] = (
    df['stock_levels'] / df['number_of_products_sold'].replace(0, 1)
).round(2)

# ── Clasificación ABC ────────────────────────────
df_sorted = df[df['gross_profit'] > 0].sort_values(
    'gross_profit', ascending=False
).reset_index(drop=True)

df_sorted['cumulative_pct'] = (
    df_sorted['gross_profit'].cumsum() / df_sorted['gross_profit'].sum() * 100
).round(2)

def classify_abc(pct):
    if pct <= 80:
        return 'A'
    elif pct <= 95:
        return 'B'
    else:
        return 'C'

df_sorted['abc_class'] = df_sorted['cumulative_pct'].apply(classify_abc)
df = df.merge(df_sorted[['sku', 'abc_class']], on='sku', how='left')
df['abc_class'] = df['abc_class'].fillna('C')

# ── Score de Riesgo ──────────────────────────────
def normalize(series):
    return (series - series.min()) / (series.max() - series.min())

df['score_stock']      = normalize(df['stock_to_sales_ratio'].fillna(0))
df['score_defect']     = normalize(df['defect_rates'].fillna(0))
df['score_inspection'] = df['inspection_results'].map(
    {'Fail': 1.0, 'Pending': 0.5, 'Pass': 0.0}
).fillna(0.5)

df['obsolescence_score'] = (
    df['score_stock']      * 0.50 +
    df['score_defect']     * 0.30 +
    df['score_inspection'] * 0.20
).round(3)

df['risk_tier'] = pd.cut(
    df['obsolescence_score'],
    bins=[0, 0.33, 0.66, 1.01],
    labels=['Low Risk', 'Medium Risk', 'High Risk']
).astype(str)

# Limpiar columnas de score intermedias
df = df.drop(columns=['score_stock', 'score_defect', 'score_inspection'])

# Guardar
df.to_csv('data/processed/powerbi_data.csv', index=False)
print("✅ Archivo guardado con todas las columnas")
print(f"Columnas: {list(df.columns)}")
print(f"\nDistribución ABC:\n{df['abc_class'].value_counts()}")
print(f"\nDistribución Risk:\n{df['risk_tier'].value_counts()}")