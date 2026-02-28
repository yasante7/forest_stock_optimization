# Temporal-Spatial Analysis - Forest loss trends over time by region
# Combines time series with spatial visualization

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import Normalize
import numpy as np
import os

os.chdir(r'H:\My Drive\Grad School\fall_26\AIMS\sample1')

print("=" * 60)
print("Temporal-Spatial Analysis")
print("=" * 60)

# Load spatial baseline
if not os.path.exists('data/spatial/ghana_forest_loss_spatial.geojson'):
    print("ERROR: Merged spatial data not found!")
    print("Please run 07_spatial_maps.py first")
    exit(1)

gdf_base = gpd.read_file('data/spatial/ghana_forest_loss_spatial.geojson')
print(f"\nLoaded base spatial data: {len(gdf_base)} regions")

# Load temporal data
regional = pd.read_csv('data/Location of tree cover loss in Ghana/treecover_loss_by_region__ha.csv')
meta = pd.read_csv('data/Location of tree cover loss in Ghana/adm1_metadata.csv')

# Merge with metadata
regional = regional.merge(meta[['adm1__id', 'name']], left_on='adm1', right_on='adm1__id', how='left')

print(f"\nTemporal data loaded: {len(regional)} observations")
print(f"Years: {regional['umd_tree_cover_loss__year'].min()} to {regional['umd_tree_cover_loss__year'].max()}")
print(f"Regions: {regional['name'].nunique()}")

# ============================================================
# 1. Time periods analysis
# ============================================================
print("\n" + "-" * 60)
print("Analyzing forest loss by time period...")
print("-" * 60)

# Define periods
def assign_period(year):
    if year <= 2006:
        return '2001-2006'
    elif year <= 2012:
        return '2007-2012'
    elif year <= 2018:
        return '2013-2018'
    else:
        return '2019-2024'

regional['period'] = regional['umd_tree_cover_loss__year'].apply(assign_period)

# Aggregate by region and period
period_summary = regional.groupby(['name', 'period']).agg({
    'umd_tree_cover_loss__ha': 'sum',
    'gfw_gross_emissions_co2e_all_gases__Mg': 'sum'
}).reset_index()
period_summary.columns = ['region', 'period', 'loss_ha', 'emissions_Mg']

print("\nLoss by period (top 5 regions):")
top_regions = regional.groupby('name')['umd_tree_cover_loss__ha'].sum().nlargest(5).index
for region in top_regions:
    region_data = period_summary[period_summary['region'] == region]
    print(f"\n{region}:")
    for _, row in region_data.iterrows():
        print(f"  {row['period']}: {row['loss_ha']:,.0f} ha")

# ============================================================
# 2. Create maps for each time period
# ============================================================
print("\n" + "-" * 60)
print("Creating period-based spatial maps...")
print("-" * 60)

# Standardize names for matching
def standardize_name(name):
    return str(name).strip().lower().replace(' region', '').replace('region', '').strip()

period_summary['region_std'] = period_summary['region'].apply(standardize_name)
gdf_base['region_std'] = gdf_base['region'].apply(standardize_name)

periods = ['2001-2006', '2007-2012', '2013-2018', '2019-2024']

# Create a 2x2 panel of maps
fig, axes = plt.subplots(2, 2, figsize=(16, 14))
axes = axes.flatten()

# Calculate global min/max for consistent color scale
vmin = period_summary['loss_ha'].min()
vmax = period_summary['loss_ha'].max()

for idx, period in enumerate(periods):
    ax = axes[idx]

    # Get data for this period
    period_data = period_summary[period_summary['period'] == period]

    # Merge with spatial data
    gdf_period = gdf_base.merge(period_data[['region_std', 'loss_ha', 'emissions_Mg']],
                                 on='region_std', how='left')

    # Plot
    gdf_period.plot(
        column='loss_ha',
        ax=ax,
        cmap='YlOrRd',
        edgecolor='black',
        linewidth=0.5,
        vmin=vmin,
        vmax=vmax,
        legend=True,
        missing_kwds={"color": "lightgrey", "edgecolor": "black"},
        legend_kwds={'label': "Loss (ha)", 'shrink': 0.7}
    )

    # Add region labels for top losers in this period
    gdf_period_sorted = gdf_period.sort_values('loss_ha', ascending=False)
    for i, row in gdf_period_sorted.head(3).iterrows():
        if pd.notna(row['loss_ha']):
            centroid = row.geometry.centroid
            label = f"{row['region']}\n{row['loss_ha']/1000:.1f}k ha"
            ax.text(centroid.x, centroid.y, label,
                   fontsize=7, ha='center', va='center',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow',
                            alpha=0.7, edgecolor='black', linewidth=0.5))

    ax.set_title(f'Period {period}', fontsize=12, fontweight='bold')
    ax.axis('off')

plt.suptitle('Forest Loss by Time Period: Ghana Regions',
             fontsize=15, fontweight='bold', y=0.98)
plt.tight_layout()
plt.savefig('latex_manuscript/figures/fig16_temporal_spatial.pdf', dpi=300, bbox_inches='tight')
print("[OK] Saved: fig16_temporal_spatial.pdf")
plt.close()

# ============================================================
# 3. Change detection: compare early vs recent periods
# ============================================================
print("\n" + "-" * 60)
print("Change detection analysis...")
print("-" * 60)

# Early period (2001-2006) vs Recent period (2019-2024)
early = period_summary[period_summary['period'] == '2001-2006'][['region', 'loss_ha']].copy()
early.columns = ['region', 'early_loss']

recent = period_summary[period_summary['period'] == '2019-2024'][['region', 'loss_ha']].copy()
recent.columns = ['region', 'recent_loss']

change = early.merge(recent, on='region')
change['absolute_change'] = change['recent_loss'] - change['early_loss']
change['percent_change'] = ((change['recent_loss'] - change['early_loss']) / change['early_loss']) * 100

print("\nChange in forest loss (2001-2006 vs 2019-2024):")
print(change.sort_values('absolute_change', ascending=False).to_string())

# Create change map
change['region_std'] = change['region'].apply(standardize_name)
gdf_change = gdf_base.merge(change[['region_std', 'absolute_change', 'percent_change']],
                            on='region_std', how='left')

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))

# Absolute change
gdf_change.plot(
    column='absolute_change',
    ax=ax1,
    cmap='RdYlGn_r',
    edgecolor='black',
    linewidth=0.5,
    legend=True,
    missing_kwds={"color": "lightgrey"},
    legend_kwds={'label': "Change in Loss (ha/period)", 'shrink': 0.8}
)

# Add labels
for idx, row in gdf_change.iterrows():
    if pd.notna(row.get('absolute_change')):
        centroid = row.geometry.centroid
        change_val = row['absolute_change']
        sign = '+' if change_val > 0 else ''
        ax1.text(centroid.x, centroid.y, f"{sign}{change_val/1000:.1f}k",
                fontsize=8, ha='center', va='center',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                         alpha=0.7, edgecolor='none'))

ax1.set_title('Change in Forest Loss\n(2019-2024 vs 2001-2006)',
             fontsize=12, fontweight='bold')
ax1.axis('off')

# Percent change
gdf_change.plot(
    column='percent_change',
    ax=ax2,
    cmap='RdYlGn_r',
    edgecolor='black',
    linewidth=0.5,
    legend=True,
    missing_kwds={"color": "lightgrey"},
    legend_kwds={'label': "Percent Change (%)", 'shrink': 0.8}
)

# Add labels
for idx, row in gdf_change.iterrows():
    if pd.notna(row.get('percent_change')):
        centroid = row.geometry.centroid
        pct = row['percent_change']
        sign = '+' if pct > 0 else ''
        ax2.text(centroid.x, centroid.y, f"{sign}{pct:.0f}%",
                fontsize=8, ha='center', va='center',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                         alpha=0.7, edgecolor='none'))

ax2.set_title('Percentage Change in Forest Loss\n(2019-2024 vs 2001-2006)',
             fontsize=12, fontweight='bold')
ax2.axis('off')

plt.tight_layout()
plt.savefig('latex_manuscript/figures/fig17_change_detection.pdf', dpi=300, bbox_inches='tight')
print("[OK] Saved: fig17_change_detection.pdf")
plt.close()

# ============================================================
# 4. Annual trend analysis by region
# ============================================================
print("\n" + "-" * 60)
print("Computing annual trends...")
print("-" * 60)

# Calculate trends using linear regression
from scipy import stats as scipy_stats

trends = []
for region in regional['name'].unique():
    region_data = regional[regional['name'] == region].sort_values('umd_tree_cover_loss__year')

    if len(region_data) > 3:  # Need at least 4 points for trend
        years = region_data['umd_tree_cover_loss__year'].values
        loss = region_data['umd_tree_cover_loss__ha'].values

        # Linear regression
        slope, intercept, r_value, p_value, std_err = scipy_stats.linregress(years, loss)

        trends.append({
            'region': region,
            'slope': slope,
            'intercept': intercept,
            'r_squared': r_value**2,
            'p_value': p_value,
            'trend': 'Increasing' if slope > 0 and p_value < 0.05 else
                    'Decreasing' if slope < 0 and p_value < 0.05 else
                    'No significant trend'
        })

trends_df = pd.DataFrame(trends)
print("\nTrend analysis results:")
print(trends_df.sort_values('slope', ascending=False).to_string())

# Save trends
trends_df.to_csv('latex_manuscript/tables/temporal_trends.csv', index=False)
print("\n[OK] Saved temporal trends analysis")

# Create trend map
trends_df['region_std'] = trends_df['region'].apply(standardize_name)
gdf_trends = gdf_base.merge(trends_df[['region_std', 'slope', 'trend']],
                            on='region_std', how='left')

fig, ax = plt.subplots(1, 1, figsize=(12, 10))

# Color by trend direction
trend_colors = {
    'Increasing': '#d7191c',
    'Decreasing': '#2c7bb6',
    'No significant trend': '#ffffbf'
}

gdf_trends['color'] = gdf_trends['trend'].map(trend_colors)
# Fill NaN values with grey for regions without trend data
gdf_trends['color'] = gdf_trends['color'].fillna('#cccccc')

gdf_trends.plot(ax=ax, color=gdf_trends['color'],
               edgecolor='black', linewidth=0.8)

# Add labels
for idx, row in gdf_trends.iterrows():
    if pd.notna(row.get('slope')):
        centroid = row.geometry.centroid
        label = f"{row['region']}\n{row['slope']:.0f} ha/yr"
        ax.text(centroid.x, centroid.y, label,
               fontsize=7, ha='center', va='center',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                        alpha=0.8, edgecolor='none'))

# Legend
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor=color, label=label)
                  for label, color in trend_colors.items()
                  if label in gdf_trends['trend'].values]
ax.legend(handles=legend_elements, loc='lower left',
         title='Deforestation Trend (2001-2024)',
         frameon=True, fancybox=True, shadow=True)

ax.set_title('Annual Deforestation Trends by Region\n(Linear regression, p < 0.05)',
            fontsize=14, fontweight='bold', pad=20)
ax.axis('off')

plt.tight_layout()
plt.savefig('latex_manuscript/figures/fig18_trend_map.pdf', dpi=300, bbox_inches='tight')
print("[OK] Saved: fig18_trend_map.pdf")
plt.close()

# ============================================================
# 5. Summary statistics table
# ============================================================
print("\n" + "-" * 60)
print("Generating summary table...")
print("-" * 60)

summary_table = []
for region in regional['name'].unique():
    region_data = regional[regional['name'] == region]

    total_loss = region_data['umd_tree_cover_loss__ha'].sum()
    avg_annual = region_data['umd_tree_cover_loss__ha'].mean()
    peak_year = region_data.loc[region_data['umd_tree_cover_loss__ha'].idxmax(), 'umd_tree_cover_loss__year']
    peak_loss = region_data['umd_tree_cover_loss__ha'].max()

    summary_table.append({
        'Region': region,
        'Total Loss (ha)': total_loss,
        'Avg Annual Loss (ha)': avg_annual,
        'Peak Year': int(peak_year),
        'Peak Loss (ha)': peak_loss
    })

summary_df = pd.DataFrame(summary_table)
summary_df = summary_df.sort_values('Total Loss (ha)', ascending=False)

print("\nTemporal summary by region:")
print(summary_df.to_string())

# Save summary
summary_df.to_csv('latex_manuscript/tables/temporal_summary.csv', index=False)
print("\n[OK] Saved temporal summary table")

# Create LaTeX table
with open('latex_manuscript/tables/table2_temporal.tex', 'w') as f:
    f.write('\\begin{tabular}{lrrrr}\n')
    f.write('\\toprule\n')
    f.write('Region & Total Loss (ha) & Avg Annual (ha) & Peak Year & Peak Loss (ha) \\\\\n')
    f.write('\\midrule\n')

    for _, row in summary_df.iterrows():
        f.write(f"{row['Region']} & {row['Total Loss (ha)']:,.0f} & "
               f"{row['Avg Annual Loss (ha)']:,.0f} & {row['Peak Year']:.0f} & "
               f"{row['Peak Loss (ha)']:,.0f} \\\\\n")

    f.write('\\bottomrule\n')
    f.write('\\end{tabular}\n')

print("[OK] Saved LaTeX table: table2_temporal.tex")

print("\n" + "=" * 60)
print("Temporal-spatial analysis complete!")
print("=" * 60)
print("\nGenerated files:")
print("  Figures:")
print("    - fig16_temporal_spatial.pdf (4-period comparison)")
print("    - fig17_change_detection.pdf (early vs recent)")
print("    - fig18_trend_map.pdf (annual trends)")
print("  Tables:")
print("    - temporal_trends.csv (regression results)")
print("    - temporal_summary.csv (regional statistics)")
print("    - table2_temporal.tex (LaTeX formatted)")
