# ================================================
# PROJECT: Supply Chain Profitability Analysis
# SCRIPT 3: Modelo de Riesgo de Inventario Obsoleto
# AUTHOR: Eliana
# ================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import os

# ── 1. Cargar datos ──────────────────────────────
df = pd.read_csv('data/processed/supply_chain_clean.csv')
df_abc = pd.read_csv('data/processed/abc_analysis.csv')

# Merge para tener clase ABC junto con datos completos
df = df.merge(
    df_abc[['sku', 'abc_class', 'rank', 'cumulative_pct']],
    on='sku',
    how='left'
)
print(f"✅ Datos cargados: {len(df)} SKUs")

# ── 2. Score de Riesgo de Obsolescencia ──────────
# Tres factores:
# - stock_to_sales_ratio: stock alto vs ventas bajas = inventario estancado
# - defect_rates: productos con defectos pierden valor
# - inspection_results: falló inspección = riesgo de devolución

# Normalizar cada factor entre 0 y 1
def normalize(series):
    return (series - series.min()) / (series.max() - series.min())

df['score_stock']  = normalize(df['stock_to_sales_ratio'].fillna(0))
df['score_defect'] = normalize(df['defect_rates'].fillna(0))
df['score_inspection'] = df['inspection_results'].map(
    {'Fail': 1.0, 'Pending': 0.5, 'Pass': 0.0}
).fillna(0.5)

# Score compuesto con pesos
df['obsolescence_score'] = (
    df['score_stock']       * 0.50 +  # Mayor peso: inventario estancado
    df['score_defect']      * 0.30 +  # Segundo: defectos
    df['score_inspection']  * 0.20    # Tercero: inspección
).round(3)

# Clasificar en tiers de riesgo
df['risk_tier'] = pd.cut(
    df['obsolescence_score'],
    bins=[0, 0.33, 0.66, 1.01],
    labels=['Low Risk', 'Medium Risk', 'High Risk']
)

# ── 3. Resumen de Riesgo ─────────────────────────
print("\n" + "=" * 50)
print("DISTRIBUCIÓN DE RIESGO:")
print("=" * 50)
print(df['risk_tier'].value_counts())

print("\n" + "=" * 50)
print("SKUs DE ALTO RIESGO:")
print("=" * 50)
high_risk = df[df['risk_tier'] == 'High Risk'][
    ['sku', 'product_type', 'supplier_name',
     'stock_levels', 'number_of_products_sold',
     'stock_to_sales_ratio', 'defect_rates',
     'inspection_results', 'gross_profit',
     'abc_class', 'obsolescence_score']
].sort_values('obsolescence_score', ascending=False)
print(high_risk.to_string(index=False))

# ── 4. El hallazgo clave: ABC vs Riesgo ──────────
print("\n" + "=" * 50)
print("CRUCE ABC vs RIESGO (el insight más importante):")
print("=" * 50)
cruce = pd.crosstab(
    df['abc_class'].fillna('Sin clasificar'),
    df['risk_tier'],
    margins=True
)
print(cruce)

# ── 5. Guardar resultados ────────────────────────
df.to_csv('data/processed/inventory_risk_model.csv', index=False)
print("\n✅ Guardado: data/processed/inventory_risk_model.csv")

# ── 6. Gráfica 1: Scatter ABC vs Riesgo ──────────
fig, axes = plt.subplots(1, 2, figsize=(16, 7))

# Colores por clase ABC
abc_colors = {'A': '#2ECC71', 'B': '#F39C12', 'C': '#E74C3C'}
risk_colors = {'Low Risk': '#2ECC71', 'Medium Risk': '#F39C12', 'High Risk': '#E74C3C'}

# Scatter: Stock vs Ganancia, coloreado por riesgo
scatter_colors = df['risk_tier'].map(risk_colors).fillna('#95A5A6')
scatter = axes[0].scatter(
    df['stock_to_sales_ratio'],
    df['gross_profit'],
    c=scatter_colors,
    s=df['defect_rates'] * 30,
    alpha=0.7,
    edgecolors='white',
    linewidth=0.5
)
axes[0].set_xlabel('Stock-to-Sales Ratio\n(Mayor = más inventario estancado)', fontsize=11)
axes[0].set_ylabel('Ganancia Bruta ($)', fontsize=11)
axes[0].set_title('Riesgo de Inventario\n(Tamaño = tasa de defectos)', fontsize=12, fontweight='bold')

patch_h = mpatches.Patch(color='#E74C3C', label='High Risk')
patch_m = mpatches.Patch(color='#F39C12', label='Medium Risk')
patch_l = mpatches.Patch(color='#2ECC71', label='Low Risk')
axes[0].legend(handles=[patch_h, patch_m, patch_l], fontsize=10)

# Barras: Top 15 SKUs por obsolescence score
top15 = df.nlargest(15, 'obsolescence_score')
bar_colors = top15['risk_tier'].map(risk_colors).fillna('#95A5A6')
bars = axes[1].barh(
    top15['sku'],
    top15['obsolescence_score'],
    color=bar_colors,
    alpha=0.85
)
axes[1].set_xlabel('Obsolescence Score (0-1)', fontsize=11)
axes[1].set_title('Top 15 SKUs con Mayor\nRiesgo de Obsolescencia', fontsize=12, fontweight='bold')
axes[1].invert_yaxis()

# Agregar etiqueta de clase ABC
for i, (_, row) in enumerate(top15.iterrows()):
    abc = row['abc_class'] if pd.notna(row['abc_class']) else '?'
    axes[1].text(
        row['obsolescence_score'] + 0.005, i,
        f"[{abc}]",
        va='center', fontsize=9, fontweight='bold',
        color=abc_colors.get(abc, '#95A5A6')
    )

plt.suptitle('Inventory Risk Model — Supply Chain Portfolio',
             fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('outputs/charts/03_inventory_risk.png', dpi=150, bbox_inches='tight')
plt.show()
print("✅ Gráfica guardada: outputs/charts/03_inventory_risk.png")