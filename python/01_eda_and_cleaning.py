# ================================================
# PROJECT: Supply Chain Profitability Analysis
# SCRIPT 1: EDA y Limpieza de Datos
# AUTHOR: Eliana Orozco
# ================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ── 1. Cargar datos ──────────────────────────────
print("=" * 50)
print("CARGANDO DATOS...")
print("=" * 50)

df = pd.read_csv('data/raw/supply_chain_data.csv')

print(f"Filas: {df.shape[0]}")
print(f"Columnas: {df.shape[1]}")
print(f"\nColumnas disponibles:\n{list(df.columns)}")

# ── 2. Revisión general ──────────────────────────
print("\n" + "=" * 50)
print("TIPOS DE DATOS:")
print("=" * 50)
print(df.dtypes)

print("\n" + "=" * 50)
print("VALORES NULOS:")
print("=" * 50)
print(df.isnull().sum())

# ── 3. Calcular métricas de rentabilidad ─────────
print("\n" + "=" * 50)
print("CALCULANDO MÉTRICAS...")
print("=" * 50)

df['gross_profit'] = (
    df['revenue_generated']
    - df['manufacturing_costs']
    - df['shipping_costs']
    - df['costs']
)

df['profit_margin_pct'] = (
    df['gross_profit'] / df['revenue_generated'] * 100
).round(2)

df['stock_to_sales_ratio'] = (
    df['stock_levels'] / df['number_of_products_sold'].replace(0, np.nan)
).round(4)

# ── 4. Estadísticas clave ────────────────────────
print("\n" + "=" * 50)
print("ESTADÍSTICAS DE RENTABILIDAD:")
print("=" * 50)
print(df[['gross_profit', 'profit_margin_pct', 'stock_to_sales_ratio']].describe().round(2))

print("\n" + "=" * 50)
print("RENTABILIDAD POR CATEGORÍA:")
print("=" * 50)
resumen = df.groupby('product_type').agg(
    total_skus        = ('sku', 'count'),
    total_revenue     = ('revenue_generated', 'sum'),
    total_profit      = ('gross_profit', 'sum'),
    avg_margin        = ('profit_margin_pct', 'mean'),
    avg_defect_rate   = ('defect_rates', 'mean')
).round(2)
print(resumen)

# ── 5. Guardar datos limpios ─────────────────────
os.makedirs('data/processed', exist_ok=True)
df.to_csv('data/processed/supply_chain_clean.csv', index=False)
print("\n✅ Archivo guardado: data/processed/supply_chain_clean.csv")

# ── 6. Gráfica: Distribución de Ganancia Bruta ───
os.makedirs('outputs/charts', exist_ok=True)

plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
sns.histplot(df['gross_profit'], bins=20, color='#2C3E50', kde=True)
plt.title('Distribución de Ganancia Bruta', fontweight='bold')
plt.xlabel('Ganancia Bruta ($)')
plt.ylabel('Frecuencia')

plt.subplot(1, 2, 2)
df.groupby('product_type')['gross_profit'].sum().sort_values().plot(
    kind='barh', color=['#2C3E50', '#E74C3C', '#3498DB']
)
plt.title('Ganancia Total por Categoría', fontweight='bold')
plt.xlabel('Ganancia Bruta Total ($)')

plt.tight_layout()
plt.savefig('outputs/charts/01_eda_overview.png', dpi=150, bbox_inches='tight')
plt.show()
print("✅ Gráfica guardada: outputs/charts/01_eda_overview.png")