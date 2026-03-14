# ================================================
# PROJECT: Supply Chain Profitability Analysis
# SCRIPT 2: Análisis Pareto y Clasificación ABC
# AUTHOR: Eliana
# ================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

# ── 1. Cargar datos limpios ──────────────────────
df = pd.read_csv('data/processed/supply_chain_clean.csv')
print(f"✅ Datos cargados: {len(df)} SKUs")

# ── 2. Clasificación ABC ─────────────────────────
# Ordenar de mayor a menor ganancia
df_abc = df[df['gross_profit'] > 0].copy()
df_abc = df_abc.sort_values('gross_profit', ascending=False).reset_index(drop=True)

# Calcular acumulado
df_abc['cumulative_profit']  = df_abc['gross_profit'].cumsum()
df_abc['cumulative_pct']     = (
    df_abc['cumulative_profit'] / df_abc['gross_profit'].sum() * 100
).round(2)
df_abc['rank'] = df_abc.index + 1

# Clasificar A, B, C
def classify_abc(pct):
    if pct <= 80:
        return 'A'
    elif pct <= 95:
        return 'B'
    else:
        return 'C'

df_abc['abc_class'] = df_abc['cumulative_pct'].apply(classify_abc)

# ── 3. Resumen ABC ───────────────────────────────
print("\n" + "=" * 50)
print("RESUMEN CLASIFICACIÓN ABC:")
print("=" * 50)
resumen = df_abc.groupby('abc_class').agg(
    total_skus    = ('sku', 'count'),
    total_profit  = ('gross_profit', 'sum'),
    avg_margin    = ('profit_margin_pct', 'mean')
).round(2)
resumen['pct_skus'] = (resumen['total_skus'] / len(df_abc) * 100).round(1)
resumen['pct_profit'] = (resumen['total_profit'] / df_abc['gross_profit'].sum() * 100).round(1)
print(resumen)

# ── 4. Guardar resultado ─────────────────────────
df_abc.to_csv('data/processed/abc_analysis.csv', index=False)
print("\n✅ Guardado: data/processed/abc_analysis.csv")

# ── 5. Curva de Pareto ───────────────────────────
fig, ax1 = plt.subplots(figsize=(16, 7))

# Colores por clase ABC
colors = df_abc['abc_class'].map({'A': '#2ECC71', 'B': '#F39C12', 'C': '#E74C3C'})

# Barras de ganancia
bars = ax1.bar(
    df_abc['rank'],
    df_abc['gross_profit'],
    color=colors,
    alpha=0.85,
    width=0.8
)

ax1.set_xlabel('SKU Rank (Mayor a Menor Ganancia)', fontsize=12)
ax1.set_ylabel('Ganancia Bruta ($)', fontsize=12, color='#2C3E50')
ax1.tick_params(axis='y', labelcolor='#2C3E50')

# Línea acumulada
ax2 = ax1.twinx()
ax2.plot(
    df_abc['rank'],
    df_abc['cumulative_pct'],
    color='#2C3E50',
    linewidth=2.5,
    marker='o',
    markersize=3,
    label='% Acumulado'
)

# Líneas de referencia
ax2.axhline(80, color='#2ECC71', linestyle='--', alpha=0.7, linewidth=1.5)
ax2.axhline(95, color='#F39C12', linestyle='--', alpha=0.7, linewidth=1.5)
ax2.set_ylabel('Ganancia Acumulada (%)', fontsize=12, color='#2C3E50')
ax2.set_ylim(0, 105)

# Anotaciones
ax2.annotate('80%', xy=(1, 80), xytext=(5, 77),
             fontsize=10, color='#2ECC71', fontweight='bold')
ax2.annotate('95%', xy=(1, 95), xytext=(5, 92),
             fontsize=10, color='#F39C12', fontweight='bold')

# Leyenda
patch_a = mpatches.Patch(color='#2ECC71', label=f"Clase A — Top 80% ganancia")
patch_b = mpatches.Patch(color='#F39C12', label=f"Clase B — Siguiente 15%")
patch_c = mpatches.Patch(color='#E74C3C', label=f"Clase C — Último 5%")
ax1.legend(handles=[patch_a, patch_b, patch_c], loc='upper right', fontsize=10)

plt.title('Análisis Pareto — Rentabilidad por SKU\nSupply Chain Portfolio Project',
          fontsize=14, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig('outputs/charts/02_pareto_abc.png', dpi=150, bbox_inches='tight')
plt.show()
print("✅ Gráfica guardada: outputs/charts/02_pareto_abc.png")

# ── 6. Top 10 SKUs más rentables ─────────────────
print("\n" + "=" * 50)
print("TOP 10 SKUs MÁS RENTABLES:")
print("=" * 50)
top10 = df_abc[['rank','sku','product_type','supplier_name',
                'gross_profit','profit_margin_pct','abc_class']].head(10)
print(top10.to_string(index=False))