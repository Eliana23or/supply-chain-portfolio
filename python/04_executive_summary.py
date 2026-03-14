# ================================================
# PROJECT: Supply Chain Profitability Analysis
# SCRIPT 4: Executive Summary Dashboard
# AUTHOR: Eliana
# ================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import os

# ── 1. Cargar datos ──────────────────────────────
df = pd.read_csv('data/processed/inventory_risk_model.csv')
print(f"✅ Datos cargados: {len(df)} SKUs")

# ── 2. KPIs principales ──────────────────────────
total_revenue    = df['revenue_generated'].sum()
total_profit     = df['gross_profit'].sum()
avg_margin       = df['profit_margin_pct'].mean()
total_skus       = len(df)
high_risk_skus   = len(df[df['risk_tier'] == 'High Risk'])
class_a_skus     = len(df[df['abc_class'] == 'A'])
class_a_profit   = df[df['abc_class'] == 'A']['gross_profit'].sum()
class_a_pct      = class_a_profit / total_profit * 100

print("\n" + "=" * 50)
print("KPIs EJECUTIVOS:")
print("=" * 50)
print(f"Revenue Total:        ${total_revenue:,.0f}")
print(f"Ganancia Bruta Total: ${total_profit:,.0f}")
print(f"Margen Promedio:      {avg_margin:.1f}%")
print(f"SKUs Clase A:         {class_a_skus} SKUs = {class_a_pct:.1f}% de ganancia")
print(f"SKUs Alto Riesgo:     {high_risk_skus}")

# ── 3. Dashboard Ejecutivo ───────────────────────
fig = plt.figure(figsize=(20, 14))
fig.patch.set_facecolor('#F8F9FA')

gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.45, wspace=0.35)

# Colores
COLOR_DARK    = '#2C3E50'
COLOR_GREEN   = '#2ECC71'
COLOR_ORANGE  = '#F39C12'
COLOR_RED     = '#E74C3C'
COLOR_BLUE    = '#3498DB'

# ── KPI Cards (fila 1) ───────────────────────────
kpis = [
    ('Revenue Total',       f"${total_revenue/1000:.0f}K",    COLOR_BLUE),
    ('Ganancia Bruta',      f"${total_profit/1000:.0f}K",     COLOR_GREEN),
    ('Margen Promedio',     f"{avg_margin:.1f}%",             COLOR_DARK),
    (f'SKUs Clase A\n({class_a_pct:.0f}% ganancia)',
                            f"{class_a_skus} SKUs",           COLOR_GREEN),
    ('SKUs Alto Riesgo',    f"{high_risk_skus}",              COLOR_RED),
    ('Total SKUs',          f"{total_skus}",                  COLOR_DARK),
]

for i, (label, value, color) in enumerate(kpis):
    ax = fig.add_subplot(gs[0, i % 3]) if i < 3 else fig.add_subplot(gs[1, i % 3])
    ax.set_facecolor('white')
    ax.text(0.5, 0.65, value, transform=ax.transAxes,
            ha='center', va='center', fontsize=22,
            fontweight='bold', color=color)
    ax.text(0.5, 0.25, label, transform=ax.transAxes,
            ha='center', va='center', fontsize=10,
            color='#7F8C8D')
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_edgecolor('#E0E0E0')

# ── Pareto Chart (fila 2, span 2 columnas) ───────
ax_pareto = fig.add_subplot(gs[2, :2])
ax_pareto.set_facecolor('white')

df_abc = df[df['abc_class'].notna()].sort_values('gross_profit', ascending=False).reset_index(drop=True)
df_abc['rank'] = df_abc.index + 1
df_abc['cum_pct'] = df_abc['gross_profit'].cumsum() / df_abc['gross_profit'].sum() * 100

colors_abc = df_abc['abc_class'].map(
    {'A': COLOR_GREEN, 'B': COLOR_ORANGE, 'C': COLOR_RED}
)

ax_pareto.bar(df_abc['rank'], df_abc['gross_profit'],
              color=colors_abc, alpha=0.85, width=0.8)
ax_pareto.set_xlabel('SKU Rank', fontsize=10)
ax_pareto.set_ylabel('Ganancia Bruta ($)', fontsize=10)

ax2 = ax_pareto.twinx()
ax2.plot(df_abc['rank'], df_abc['cum_pct'],
         color=COLOR_DARK, linewidth=2.5)
ax2.axhline(80, color=COLOR_GREEN, linestyle='--', alpha=0.6)
ax2.axhline(95, color=COLOR_ORANGE, linestyle='--', alpha=0.6)
ax2.set_ylabel('% Acumulado', fontsize=10)
ax2.set_ylim(0, 105)

patch_a = mpatches.Patch(color=COLOR_GREEN,  label='Clase A')
patch_b = mpatches.Patch(color=COLOR_ORANGE, label='Clase B')
patch_c = mpatches.Patch(color=COLOR_RED,    label='Clase C')
ax_pareto.legend(handles=[patch_a, patch_b, patch_c],
                 loc='upper left', fontsize=9)
ax_pareto.set_title('Análisis Pareto — Rentabilidad por SKU',
                    fontsize=11, fontweight='bold', pad=10)

# ── Ganancia por Categoría (fila 2, col 3) ───────
ax_cat = fig.add_subplot(gs[2, 2])
ax_cat.set_facecolor('white')

cat_profit = df.groupby('product_type')['gross_profit'].sum().sort_values()
bars = ax_cat.barh(cat_profit.index, cat_profit.values,
                   color=[COLOR_BLUE, COLOR_RED, COLOR_GREEN],
                   alpha=0.85)

for bar, val in zip(bars, cat_profit.values):
    ax_cat.text(bar.get_width() + 500, bar.get_y() + bar.get_height()/2,
                f'${val/1000:.0f}K', va='center', fontsize=9, fontweight='bold')

ax_cat.set_xlabel('Ganancia Bruta ($)', fontsize=10)
ax_cat.set_title('Ganancia por Categoría',
                 fontsize=11, fontweight='bold', pad=10)
ax_cat.set_xlim(0, cat_profit.max() * 1.2)

# ── Título principal ─────────────────────────────
fig.suptitle(
    'Supply Chain Profitability & Inventory Optimization\nExecutive Summary Dashboard',
    fontsize=16, fontweight='bold', color=COLOR_DARK, y=1.01
)

plt.savefig('outputs/charts/04_executive_summary.png',
            dpi=150, bbox_inches='tight',
            facecolor=fig.get_facecolor())
plt.show()
print("✅ Gráfica guardada: outputs/charts/04_executive_summary.png")
