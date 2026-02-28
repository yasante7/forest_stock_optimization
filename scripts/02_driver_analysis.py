# driver analysis - what's causing the deforestation?
# trying to figure out the main drivers of forest loss

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

os.chdir(r'H:\My Drive\Grad School\fall_26\AIMS\sample1')

# load driver data
drivers = pd.read_csv('data/Tree cover loss by dominant driver in Ghana/tree_cover_loss_by_driver.csv')

print("Driver data loaded")
print(drivers.head(10))
print("\nUnique drivers:", drivers['drivers_type'].unique())

# aggregate by driver type across all years
driver_totals = drivers.groupby('drivers_type').agg({
    'loss_area_ha': 'sum',
    'gross_carbon_emissions_Mg': 'sum'
}).reset_index()

# sort by area
driver_totals = driver_totals.sort_values('loss_area_ha', ascending=False)
print("\nTotal loss by driver:")
print(driver_totals)

# calculate percentages
total_area = driver_totals['loss_area_ha'].sum()
driver_totals['pct'] = (driver_totals['loss_area_ha'] / total_area) * 100

# Plot 3: Driver composition
fig, ax = plt.subplots(figsize=(10, 6))

# horizontal bar chart looks cleaner here
colors = ['#8B0000', '#CD5C5C', '#F08080', '#FFA07A', '#FFB6C1', '#FFE4E1', '#D3D3D3', '#A9A9A9']
bars = ax.barh(driver_totals['drivers_type'],
               driver_totals['loss_area_ha']/1000,
               color=colors[:len(driver_totals)])

ax.set_xlabel('Total Loss (1000 ha, 2001-2024)', fontsize=11)
ax.set_title('Drivers of Forest Loss in Ghana', fontsize=13, pad=15)
ax.grid(axis='x', alpha=0.3)

# add percentage labels on bars
for i, (bar, pct) in enumerate(zip(bars, driver_totals['pct'])):
    width = bar.get_width()
    ax.text(width + 5, bar.get_y() + bar.get_height()/2,
            f'{pct:.1f}%',
            ha='left', va='center', fontsize=9)

plt.tight_layout()
plt.savefig('latex_manuscript/figures/fig3_drivers.pdf', dpi=300, bbox_inches='tight')
print("\nSaved: fig3_drivers.pdf")

# Plot 4: Drivers over time - see if composition changed
# group by year and driver
yearly_drivers = drivers.groupby(['loss_year', 'drivers_type'])['loss_area_ha'].sum().reset_index()

# pivot for stacked area plot
driver_pivot = yearly_drivers.pivot(index='loss_year', columns='drivers_type', values='loss_area_ha')
driver_pivot = driver_pivot.fillna(0)

# only plot top 5 drivers to avoid clutter
top_drivers = driver_totals.head(5)['drivers_type'].tolist()
driver_pivot_top = driver_pivot[top_drivers]

fig, ax = plt.subplots(figsize=(12, 6))
driver_pivot_top.plot.area(ax=ax, alpha=0.7, stacked=True)

ax.set_xlabel('Year', fontsize=11)
ax.set_ylabel('Forest Loss (ha)', fontsize=11)
ax.set_title('Evolution of Deforestation Drivers Over Time (Top 5)', fontsize=13, pad=15)
ax.legend(title='Driver', bbox_to_anchor=(1.05, 1), loc='upper left')
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('latex_manuscript/figures/fig4_drivers_time.pdf', dpi=300, bbox_inches='tight')
print("Saved: fig4_drivers_time.pdf")

# Calculate driver shares by period
# split into three periods like in the paper
period1 = drivers[drivers['loss_year'] <= 2006]
period2 = drivers[(drivers['loss_year'] > 2006) & (drivers['loss_year'] <= 2015)]
period3 = drivers[drivers['loss_year'] > 2015]

def calc_shares(df):
    totals = df.groupby('drivers_type')['loss_area_ha'].sum()
    shares = (totals / totals.sum()) * 100
    return shares

shares1 = calc_shares(period1)
shares2 = calc_shares(period2)
shares3 = calc_shares(period3)

print("\nDriver shares by period:")
print("\n2001-2006:")
print(shares1.sort_values(ascending=False))
print("\n2007-2015:")
print(shares2.sort_values(ascending=False))
print("\n2016-2024:")
print(shares3.sort_values(ascending=False))

# emissions intensity by driver
driver_totals['emissions_per_ha'] = driver_totals['gross_carbon_emissions_Mg'] / driver_totals['loss_area_ha']
print("\nEmissions intensity by driver (Mg CO2e/ha):")
print(driver_totals[['drivers_type', 'emissions_per_ha']].sort_values('emissions_per_ha', ascending=False))

# save driver summary table
driver_totals[['drivers_type', 'loss_area_ha', 'pct', 'emissions_per_ha']].to_csv(
    'latex_manuscript/tables/driver_summary.csv', index=False)
print("\nDriver summary saved to tables/driver_summary.csv")

print("\nDone with driver analysis!")
