# Additional optimization visualizations for manuscript
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

os.chdir(r'H:\My Drive\Grad School\fall_26\AIMS\sample1')

# Load optimization results
results = pd.read_csv('latex_manuscript/tables/optimization_results.csv')

# Create BAU projection for comparison
years = results['year'].values
T = len(years)
X0 = 6.2e6
BAU_deforest = 58000  # ha/year
BAU_reforest = 11500  # ha/year

# BAU trajectory
X_BAU = np.zeros(T)
X_BAU[0] = X0
for t in range(1, T):
    X_BAU[t] = X_BAU[t-1] - BAU_deforest + BAU_reforest

# Optimal trajectory
X_opt = results['forest_stock_ha'].values

# Figure 1: BAU vs Optimal Comparison
fig, ax = plt.subplots(1, 1, figsize=(12, 6))

ax.plot(years, X_opt/1e6, 'b-', linewidth=2.5, label='Optimal Path', marker='o',
        markersize=4, markevery=10)
ax.plot(years, X_BAU/1e6, 'r--', linewidth=2.5, label='Business-as-Usual', marker='s',
        markersize=4, markevery=10)
ax.axhline(5.5, color='green', linestyle=':', linewidth=2, label='NDC Target (5.5 M ha)')
ax.axhline(2.0, color='orange', linestyle=':', linewidth=2, label='Critical Threshold (2.0 M ha)')

# Add shaded regions
ax.fill_between(years, 0, 2.0, alpha=0.1, color='red', label='Ecological collapse zone')
ax.fill_between(years, 2.0, 5.5, alpha=0.1, color='orange')

ax.set_xlabel('Year', fontsize=13)
ax.set_ylabel('Forest Stock (million ha)', fontsize=13)
ax.set_title('Optimal vs. Business-as-Usual Forest Trajectories', fontsize=14, fontweight='bold')
ax.legend(loc='right', frameon=True, fontsize=10)
ax.grid(True, alpha=0.3)
ax.set_xlim(2024, 2124)
ax.set_ylim(0, 10)

plt.tight_layout()
plt.savefig('latex_manuscript/figures/fig8_comparison.pdf', dpi=300, bbox_inches='tight')
plt.savefig('latex_manuscript/figures/fig8_comparison.png', dpi=300, bbox_inches='tight')
print("Saved: fig8_comparison.pdf and .png")

# Figure 2: Key Metrics Over Time (4-panel)
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Panel A: Deforestation comparison
ax = axes[0, 0]
ax.plot(years, results['deforestation_ha']/1000, 'b-', linewidth=2, label='Optimal')
ax.axhline(58, color='red', linestyle='--', linewidth=2, label='Historical (2020-24)')
ax.set_ylabel('Deforestation (1000 ha/year)', fontsize=11)
ax.set_title('A. Deforestation Rates', fontsize=12, fontweight='bold')
ax.legend()
ax.grid(alpha=0.3)

# Panel B: Reforestation comparison
ax = axes[0, 1]
ax.plot(years, results['reforestation_ha']/1000, 'g-', linewidth=2, label='Optimal')
ax.axhline(11.5, color='gray', linestyle='--', linewidth=2, label='Historical avg')
ax.set_ylabel('Reforestation (1000 ha/year)', fontsize=11)
ax.set_title('B. Reforestation Rates', fontsize=12, fontweight='bold')
ax.legend()
ax.grid(alpha=0.3)

# Panel C: Net change
ax = axes[1, 0]
ax.plot(years, results['net_change_ha']/1000, 'purple', linewidth=2)
ax.axhline(0, color='black', linestyle='-', linewidth=0.8)
ax.fill_between(years, 0, results['net_change_ha']/1000, where=(results['net_change_ha']>0),
                alpha=0.3, color='green', label='Net gain')
ax.fill_between(years, results['net_change_ha']/1000, 0, where=(results['net_change_ha']<0),
                alpha=0.3, color='red', label='Net loss')
ax.set_ylabel('Net Change (1000 ha/year)', fontsize=11)
ax.set_xlabel('Year', fontsize=11)
ax.set_title('C. Net Forest Change', fontsize=12, fontweight='bold')
ax.legend()
ax.grid(alpha=0.3)

# Panel D: Cumulative change
ax = axes[1, 1]
cumulative_opt = np.cumsum(results['net_change_ha'].values) / 1e6
cumulative_bau = np.cumsum([-BAU_deforest + BAU_reforest] * T) / 1e6
ax.plot(years, cumulative_opt, 'b-', linewidth=2.5, label='Optimal')
ax.plot(years, cumulative_bau, 'r--', linewidth=2.5, label='Business-as-Usual')
ax.axhline(0, color='black', linestyle='-', linewidth=0.8)
ax.set_ylabel('Cumulative Change (million ha)', fontsize=11)
ax.set_xlabel('Year', fontsize=11)
ax.set_title('D. Cumulative Forest Change from 2024', fontsize=12, fontweight='bold')
ax.legend()
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('latex_manuscript/figures/fig9_metrics.pdf', dpi=300, bbox_inches='tight')
plt.savefig('latex_manuscript/figures/fig9_metrics.png', dpi=300, bbox_inches='tight')
print("Saved: fig9_metrics.pdf and .png")

# Summary statistics for key years
key_years = [2024, 2050, 2074, 2100, 2124]
comparison_data = []

for year in key_years:
    if year in years:
        idx = np.where(years == year)[0][0]
        comparison_data.append({
            'Year': year,
            'Optimal_Stock_Mha': f"{X_opt[idx]/1e6:.2f}",
            'BAU_Stock_Mha': f"{X_BAU[idx]/1e6:.2f}",
            'Difference_Mha': f"{(X_opt[idx] - X_BAU[idx])/1e6:.2f}",
            'Optimal_Deforest_kha': f"{results.iloc[idx]['deforestation_ha']/1000:.2f}",
            'Optimal_Reforest_kha': f"{results.iloc[idx]['reforestation_ha']/1000:.2f}"
        })

comparison_df = pd.DataFrame(comparison_data)
comparison_df.to_csv('latex_manuscript/tables/table3_comparison_key_years.csv', index=False)
print("Saved: table3_comparison_key_years.csv")

print("\n=== Key Years Comparison ===")
print(comparison_df.to_string(index=False))

print("\n✓ All additional visualizations complete!")
