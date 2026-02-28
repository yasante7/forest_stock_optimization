# regional analysis
# trying to see which regions lost the most forest
# this took a while to figure out the mapping...

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

os.chdir(r'H:\My Drive\Grad School\fall_26\AIMS\sample1')

# load regional loss data
regional = pd.read_csv('data/Location of tree cover loss in Ghana/treecover_loss_by_region__ha.csv')
regional_extent = pd.read_csv('data/Location of tree cover loss in Ghana/treecover_extent_2000_by_region__ha.csv')

print("Regional data loaded")
print(regional.head())

# get metadata for region names
meta = pd.read_csv('data/Location of tree cover loss in Ghana/adm1_metadata.csv')
print("\nRegion metadata:")
print(meta)

# merge to get region names
regional = regional.merge(meta[['adm1__id', 'name']], left_on='adm1', right_on='adm1__id', how='left')
regional_extent = regional_extent.merge(meta[['adm1__id', 'name']], left_on='adm1', right_on='adm1__id', how='left')

# aggregate loss by region (sum across all years)
regional_total = regional.groupby('name').agg({
    'umd_tree_cover_loss__ha': 'sum'
}).reset_index()
regional_total.columns = ['region', 'total_loss_ha']

# get initial extent
extent_2000 = regional_extent.groupby('name')['umd_tree_cover_extent_2000__ha'].sum().reset_index()
extent_2000.columns = ['region', 'extent_2000_ha']

# merge
regional_summary = regional_total.merge(extent_2000, on='region')

# calculate percentage loss
regional_summary['pct_loss'] = (regional_summary['total_loss_ha'] / regional_summary['extent_2000_ha']) * 100

# sort by total loss
regional_summary = regional_summary.sort_values('total_loss_ha', ascending=False)

print("\nRegional summary:")
print(regional_summary)

# Plot 5: Regional loss
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# absolute loss
ax1.barh(regional_summary['region'], regional_summary['total_loss_ha']/1000,
         color='firebrick', alpha=0.7)
ax1.set_xlabel('Total Loss (1000 ha)', fontsize=11)
ax1.set_title('Total Forest Loss by Region (2001-2024)', fontsize=12)
ax1.grid(axis='x', alpha=0.3)

# percentage loss
ax2.barh(regional_summary['region'], regional_summary['pct_loss'],
         color='darkgreen', alpha=0.7)
ax2.set_xlabel('% of 2000 Forest Extent', fontsize=11)
ax2.set_title('Percentage Forest Loss by Region', fontsize=12)
ax2.grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig('latex_manuscript/figures/fig5_regional.pdf', dpi=300, bbox_inches='tight')
print("\nSaved: fig5_regional.pdf")

# time series by top regions
top_regions = regional_summary.head(5)['region'].tolist()
regional_top = regional[regional['name'].isin(top_regions)]

fig, ax = plt.subplots(figsize=(12, 6))

for region in top_regions:
    data = regional_top[regional_top['name'] == region]
    ax.plot(data['umd_tree_cover_loss__year'],
            data['umd_tree_cover_loss__ha']/1000,
            marker='o', label=region, linewidth=2, markersize=4)

ax.set_xlabel('Year', fontsize=11)
ax.set_ylabel('Annual Loss (1000 ha)', fontsize=11)
ax.set_title('Forest Loss Trends in Top 5 Regions', fontsize=13, pad=15)
ax.legend(loc='best')
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('latex_manuscript/figures/fig6_regional_trends.pdf', dpi=300, bbox_inches='tight')
print("Saved: fig6_regional_trends.pdf")

# save regional summary table for latex
regional_summary_latex = regional_summary[['region', 'extent_2000_ha', 'total_loss_ha', 'pct_loss']].copy()
regional_summary_latex.columns = ['Region', 'Initial Extent (ha)', 'Total Loss (ha)', 'Loss (\\%)']

# format for latex table
with open('latex_manuscript/tables/table1_regional.tex', 'w') as f:
    f.write('\\begin{tabular}{lrrr}\n')
    f.write('\\toprule\n')
    f.write('Region & Initial Extent (ha) & Total Loss (ha) & Loss (\\%) \\\\\n')
    f.write('\\midrule\n')

    for _, row in regional_summary_latex.iterrows():
        loss_pct = row['Loss (\\%)']
        f.write(f"{row['Region']} & {row['Initial Extent (ha)']:,.0f} & {row['Total Loss (ha)']:,.0f} & {loss_pct:.1f} \\\\\n")

    f.write('\\bottomrule\n')
    f.write('\\end{tabular}\n')

print("\nRegional table saved to tables/table1_regional.tex")

# calculate some stats for the paper
print("\n--- Stats for manuscript ---")
top3_loss = regional_summary.head(3)['total_loss_ha'].sum()
total_loss_all = regional_summary['total_loss_ha'].sum()
top3_pct = (top3_loss / total_loss_all) * 100
print(f"Top 3 regions account for {top3_pct:.1f}% of total loss")

eastern = regional_summary[regional_summary['region'].str.contains('Eastern')]
if not eastern.empty:
    print(f"\nEastern region: {eastern['total_loss_ha'].iloc[0]:,.0f} ha ({eastern['pct_loss'].iloc[0]:.1f}%)")

print("\nRegional analysis complete!")
