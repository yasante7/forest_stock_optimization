# -*- coding: utf-8 -*-
"""
Forest loss analysis for Ghana
Created on: Feb 2026
@author: economics grad student

This script loads the forest loss data and makes some basic plots
Trying to get annual trends and regional breakdowns
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# set working directory to where data is
os.chdir(r'H:\My Drive\Grad School\fall_26\AIMS\sample1')

# load the main dataset - this has yearly tree cover loss
df = pd.read_csv('data/Tree cover loss in Ghana/treecover_loss__ha.csv')

# quick look at what we got
print("Data shape:", df.shape)
print("\nFirst few rows:")
print(df.head())
print("\nColumns:", df.columns.tolist())

# calculate some basic stats
total_loss = df['umd_tree_cover_loss__ha'].sum()
avg_annual = df['umd_tree_cover_loss__ha'].mean()
print(f"\nTotal forest loss 2001-2024: {total_loss:,.0f} ha")
print(f"Average annual loss: {avg_annual:,.0f} ha")

# Plot 1: Annual forest loss over time
# trying different figure sizes to see what looks good
fig, ax = plt.subplots(figsize=(10, 6))

# bar plot works better than line for this i think
ax.bar(df['umd_tree_cover_loss__year'],
       df['umd_tree_cover_loss__ha']/1000,  # convert to thousand ha
       color='darkred', alpha=0.7, edgecolor='black')

ax.set_xlabel('Year', fontsize=11)
ax.set_ylabel('Tree Cover Loss (1000 ha)', fontsize=11)
ax.set_title('Annual Tree Cover Loss in Ghana (2001-2024)', fontsize=13, pad=15)
ax.grid(axis='y', alpha=0.3)

# add a trend line maybe?
z = np.polyfit(df['umd_tree_cover_loss__year'], df['umd_tree_cover_loss__ha']/1000, 1)
p = np.poly1d(z)
ax.plot(df['umd_tree_cover_loss__year'], p(df['umd_tree_cover_loss__year']),
        "r--", linewidth=2, alpha=0.6, label=f'Trend')
ax.legend()

plt.tight_layout()
plt.savefig('latex_manuscript/figures/fig1_annual_loss.pdf', dpi=300, bbox_inches='tight')
print("\nSaved: fig1_annual_loss.pdf")
# plt.show()

# Plot 2: CO2 emissions alongside forest loss
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

# top panel - forest loss
ax1.bar(df['umd_tree_cover_loss__year'],
        df['umd_tree_cover_loss__ha']/1000,
        color='darkgreen', alpha=0.6)
ax1.set_ylabel('Forest Loss (1000 ha)', fontsize=11)
ax1.set_title('Forest Loss and Carbon Emissions in Ghana', fontsize=13, pad=15)
ax1.grid(axis='y', alpha=0.3)

# bottom panel - emissions
ax2.bar(df['umd_tree_cover_loss__year'],
        df['gfw_gross_emissions_co2e_all_gases__Mg']/1e6,  # convert to million Mg
        color='darkred', alpha=0.6)
ax2.set_xlabel('Year', fontsize=11)
ax2.set_ylabel('CO₂ Emissions (Million Mg)', fontsize=11)
ax2.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('latex_manuscript/figures/fig2_emissions.pdf', dpi=300, bbox_inches='tight')
print("Saved: fig2_emissions.pdf")

# Calculate emissions per hectare
df['emissions_per_ha'] = df['gfw_gross_emissions_co2e_all_gases__Mg'] / df['umd_tree_cover_loss__ha']
avg_emissions = df['emissions_per_ha'].mean()
print(f"\nAverage emissions per hectare: {avg_emissions:.1f} Mg CO2e/ha")

# identify the years with highest/lowest loss
max_year = df.loc[df['umd_tree_cover_loss__ha'].idxmax()]
min_year = df.loc[df['umd_tree_cover_loss__ha'].idxmin()]
print(f"\nHighest loss year: {max_year['umd_tree_cover_loss__year']} ({max_year['umd_tree_cover_loss__ha']:,.0f} ha)")
print(f"Lowest loss year: {min_year['umd_tree_cover_loss__year']} ({min_year['umd_tree_cover_loss__ha']:,.0f} ha)")

# Save summary stats to a text file for reference
with open('latex_manuscript/tables/summary_stats.txt', 'w') as f:
    f.write("Ghana Forest Loss Summary Statistics (2001-2024)\n")
    f.write("=" * 50 + "\n\n")
    f.write(f"Total forest loss: {total_loss:,.0f} ha\n")
    f.write(f"Average annual loss: {avg_annual:,.0f} ha\n")
    f.write(f"Standard deviation: {df['umd_tree_cover_loss__ha'].std():,.0f} ha\n")
    f.write(f"Max annual loss: {df['umd_tree_cover_loss__ha'].max():,.0f} ha (year {df.loc[df['umd_tree_cover_loss__ha'].idxmax(), 'umd_tree_cover_loss__year']:.0f})\n")
    f.write(f"Min annual loss: {df['umd_tree_cover_loss__ha'].min():,.0f} ha (year {df.loc[df['umd_tree_cover_loss__ha'].idxmin(), 'umd_tree_cover_loss__year']:.0f})\n")
    f.write(f"\nTotal CO2 emissions: {df['gfw_gross_emissions_co2e_all_gases__Mg'].sum()/1e6:.1f} Million Mg\n")
    f.write(f"Average emissions per ha: {avg_emissions:.1f} Mg CO2e/ha\n")

print("\nDone! Check the figures folder for outputs")
