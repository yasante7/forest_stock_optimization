# Spatial Mapping - Create choropleth maps of forest loss
# This script creates spatial visualizations of forest loss by region

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import os

os.chdir(r'H:\My Drive\Grad School\fall_26\AIMS\sample1')

print("=" * 60)
print("Creating spatial maps of forest loss")
print("=" * 60)

# Check which spatial files exist
spatial_files = []
if os.path.exists('data/spatial/ghana_regions.geojson'):
    spatial_files.append(('geoBoundaries', 'data/spatial/ghana_regions.geojson'))
if os.path.exists('data/spatial/ghana_regions_gadm.geojson'):
    spatial_files.append(('GADM', 'data/spatial/ghana_regions_gadm.geojson'))

if not spatial_files:
    print("ERROR: No spatial files found!")
    print("Please run 06_spatial_setup.py first")
    exit(1)

# Use the first available spatial file
source, spatial_file = spatial_files[0]
print(f"\nUsing {source} data: {spatial_file}")

# Load spatial data
gdf = gpd.read_file(spatial_file)
print(f"Loaded {len(gdf)} regions")
print(f"CRS: {gdf.crs}")
print(f"Columns: {gdf.columns.tolist()}")

# Identify the name column
name_col = None
for col in ['shapeName', 'NAME_1', 'name', 'ADMIN1', 'ADM1_EN']:
    if col in gdf.columns:
        name_col = col
        break

if name_col is None:
    print("ERROR: Could not identify region name column")
    print(f"Available columns: {gdf.columns.tolist()}")
    exit(1)

print(f"\nUsing '{name_col}' as region name column")
print(f"Regions in shapefile:\n{gdf[name_col].sort_values().tolist()}")

# Load forest loss data by region
regional = pd.read_csv('data/Location of tree cover loss in Ghana/treecover_loss_by_region__ha.csv')
regional_extent = pd.read_csv('data/Location of tree cover loss in Ghana/treecover_extent_2000_by_region__ha.csv')
meta = pd.read_csv('data/Location of tree cover loss in Ghana/adm1_metadata.csv')

# Merge with metadata
regional = regional.merge(meta[['adm1__id', 'name']], left_on='adm1', right_on='adm1__id', how='left')
regional_extent = regional_extent.merge(meta[['adm1__id', 'name']], left_on='adm1', right_on='adm1__id', how='left')

# Aggregate by region
regional_total = regional.groupby('name').agg({
    'umd_tree_cover_loss__ha': 'sum',
    'gfw_gross_emissions_co2e_all_gases__Mg': 'sum'
}).reset_index()
regional_total.columns = ['region', 'total_loss_ha', 'total_emissions_Mg']

extent_2000 = regional_extent.groupby('name')['umd_tree_cover_extent_2000__ha'].sum().reset_index()
extent_2000.columns = ['region', 'extent_2000_ha']

# Merge
regional_summary = regional_total.merge(extent_2000, on='region')
regional_summary['pct_loss'] = (regional_summary['total_loss_ha'] / regional_summary['extent_2000_ha']) * 100
regional_summary['emissions_per_ha'] = regional_summary['total_emissions_Mg'] / regional_summary['total_loss_ha']

print(f"\nForest loss data loaded for {len(regional_summary)} regions:")
print(regional_summary[['region', 'total_loss_ha', 'pct_loss']].to_string())

# Create standardized region name for matching
def standardize_name(name):
    """Standardize region names for matching"""
    name = str(name).strip().lower()
    # Remove common suffixes/prefixes
    name = name.replace(' region', '').replace('region', '')
    name = name.replace(' province', '').replace('province', '')
    return name.strip()

regional_summary['region_std'] = regional_summary['region'].apply(standardize_name)
gdf['region_std'] = gdf[name_col].apply(standardize_name)

print("\nStandardized names for matching:")
print("From data:", sorted(regional_summary['region_std'].tolist()))
print("From shapefile:", sorted(gdf['region_std'].tolist()))

# Merge spatial data with forest loss data
gdf_merged = gdf.merge(regional_summary, on='region_std', how='left')

print(f"\nMerge results:")
print(f"  Total regions in shapefile: {len(gdf)}")
print(f"  Regions matched with data: {gdf_merged['total_loss_ha'].notna().sum()}")
print(f"  Regions without data: {gdf_merged['total_loss_ha'].isna().sum()}")

if gdf_merged['total_loss_ha'].isna().all():
    print("\nWARNING: No regions matched! Trying alternative matching...")
    # Try direct matching without standardization
    gdf_merged = gdf.merge(regional_summary, left_on=name_col, right_on='region', how='left')
    print(f"  Alternative match - Regions with data: {gdf_merged['total_loss_ha'].notna().sum()}")

# Ensure we're in a good CRS for plotting
if gdf_merged.crs.is_geographic:
    print(f"\nReprojecting to UTM Zone 30N (EPSG:32630) for Ghana")
    gdf_merged = gdf_merged.to_crs(epsg=32630)

# Create figure directory
os.makedirs('latex_manuscript/figures', exist_ok=True)

# ============================================================
# Map 1: Total Forest Loss (hectares)
# ============================================================
print("\nCreating Map 1: Total Forest Loss...")

fig, ax = plt.subplots(1, 1, figsize=(12, 10))

# Plot the map
gdf_merged.plot(
    column='total_loss_ha',
    ax=ax,
    legend=True,
    cmap='YlOrRd',
    edgecolor='black',
    linewidth=0.5,
    missing_kwds={
        "color": "lightgrey",
        "edgecolor": "black",
        "hatch": "///",
        "label": "No data"
    },
    legend_kwds={
        'label': "Total Forest Loss (ha, 2001-2024)",
        'orientation': "horizontal",
        'shrink': 0.8,
        'pad': 0.05,
        'format': '%.0f'
    }
)

# Add region labels
for idx, row in gdf_merged.iterrows():
    centroid = row.geometry.centroid
    region_name = row['region'] if pd.notna(row.get('region')) else row[name_col]
    ax.text(centroid.x, centroid.y, region_name,
            fontsize=7, ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7, edgecolor='none'))

ax.set_title('Total Forest Loss by Region in Ghana (2001-2024)',
             fontsize=14, fontweight='bold', pad=20)
ax.axis('off')

plt.tight_layout()
plt.savefig('latex_manuscript/figures/fig10_spatial_total_loss.pdf', dpi=300, bbox_inches='tight')
print("[OK] Saved: fig10_spatial_total_loss.pdf")
plt.close()

# ============================================================
# Map 2: Percentage Forest Loss
# ============================================================
print("Creating Map 2: Percentage Forest Loss...")

fig, ax = plt.subplots(1, 1, figsize=(12, 10))

gdf_merged.plot(
    column='pct_loss',
    ax=ax,
    legend=True,
    cmap='RdYlGn_r',
    edgecolor='black',
    linewidth=0.5,
    missing_kwds={
        "color": "lightgrey",
        "edgecolor": "black",
        "hatch": "///",
        "label": "No data"
    },
    legend_kwds={
        'label': "Percentage of 2000 Forest Extent Lost (%)",
        'orientation': "horizontal",
        'shrink': 0.8,
        'pad': 0.05,
        'format': '%.1f%%'
    }
)

# Add region labels with loss percentage
for idx, row in gdf_merged.iterrows():
    centroid = row.geometry.centroid
    region_name = row['region'] if pd.notna(row.get('region')) else row[name_col]
    if pd.notna(row.get('pct_loss')):
        label = f"{region_name}\n({row['pct_loss']:.1f}%)"
    else:
        label = region_name
    ax.text(centroid.x, centroid.y, label,
            fontsize=7, ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7, edgecolor='none'))

ax.set_title('Percentage Forest Loss by Region (2001-2024)',
             fontsize=14, fontweight='bold', pad=20)
ax.axis('off')

plt.tight_layout()
plt.savefig('latex_manuscript/figures/fig11_spatial_pct_loss.pdf', dpi=300, bbox_inches='tight')
print("[OK] Saved: fig11_spatial_pct_loss.pdf")
plt.close()

# ============================================================
# Map 3: Carbon Emissions per Hectare
# ============================================================
print("Creating Map 3: Emissions Intensity...")

fig, ax = plt.subplots(1, 1, figsize=(12, 10))

gdf_merged.plot(
    column='emissions_per_ha',
    ax=ax,
    legend=True,
    cmap='plasma',
    edgecolor='black',
    linewidth=0.5,
    missing_kwds={
        "color": "lightgrey",
        "edgecolor": "black",
        "hatch": "///",
        "label": "No data"
    },
    legend_kwds={
        'label': "Carbon Emissions Intensity (Mg CO₂e/ha)",
        'orientation': "horizontal",
        'shrink': 0.8,
        'pad': 0.05,
        'format': '%.0f'
    }
)

# Add region labels
for idx, row in gdf_merged.iterrows():
    centroid = row.geometry.centroid
    region_name = row['region'] if pd.notna(row.get('region')) else row[name_col]
    if pd.notna(row.get('emissions_per_ha')):
        label = f"{region_name}\n{row['emissions_per_ha']:.0f} Mg/ha"
    else:
        label = region_name
    ax.text(centroid.x, centroid.y, label,
            fontsize=6, ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7, edgecolor='none'))

ax.set_title('Carbon Emissions Intensity by Region',
             fontsize=14, fontweight='bold', pad=20)
ax.axis('off')

plt.tight_layout()
plt.savefig('latex_manuscript/figures/fig12_spatial_emissions.pdf', dpi=300, bbox_inches='tight')
print("[OK] Saved: fig12_spatial_emissions.pdf")
plt.close()

# ============================================================
# Map 4: Combined view (2x2 panel)
# ============================================================
print("Creating Map 4: Combined panel...")

fig, axes = plt.subplots(2, 2, figsize=(16, 14))
axes = axes.flatten()

# Panel 1: Total loss
gdf_merged.plot(column='total_loss_ha', ax=axes[0], legend=True,
                cmap='YlOrRd', edgecolor='black', linewidth=0.3,
                legend_kwds={'label': "Total Loss (ha)", 'shrink': 0.6})
axes[0].set_title('(a) Total Forest Loss (ha)', fontsize=11, fontweight='bold')
axes[0].axis('off')

# Panel 2: Percentage loss
gdf_merged.plot(column='pct_loss', ax=axes[1], legend=True,
                cmap='RdYlGn_r', edgecolor='black', linewidth=0.3,
                legend_kwds={'label': "Loss (%)", 'shrink': 0.6})
axes[1].set_title('(b) Percentage Loss', fontsize=11, fontweight='bold')
axes[1].axis('off')

# Panel 3: Total emissions
gdf_merged.plot(column='total_emissions_Mg', ax=axes[2], legend=True,
                cmap='Reds', edgecolor='black', linewidth=0.3,
                legend_kwds={'label': "Emissions (Mg CO₂e)", 'shrink': 0.6, 'format': '%.2e'})
axes[2].set_title('(c) Total Carbon Emissions', fontsize=11, fontweight='bold')
axes[2].axis('off')

# Panel 4: Emissions intensity
gdf_merged.plot(column='emissions_per_ha', ax=axes[3], legend=True,
                cmap='plasma', edgecolor='black', linewidth=0.3,
                legend_kwds={'label': "Mg CO₂e/ha", 'shrink': 0.6})
axes[3].set_title('(d) Emissions Intensity', fontsize=11, fontweight='bold')
axes[3].axis('off')

plt.suptitle('Spatial Distribution of Forest Loss and Emissions in Ghana (2001-2024)',
             fontsize=15, fontweight='bold', y=0.98)
plt.tight_layout()
plt.savefig('latex_manuscript/figures/fig13_spatial_panel.pdf', dpi=300, bbox_inches='tight')
print("[OK] Saved: fig13_spatial_panel.pdf")
plt.close()

# Save merged spatial data for further analysis
gdf_merged.to_file('data/spatial/ghana_forest_loss_spatial.geojson', driver='GeoJSON')
print("\n[OK] Saved merged spatial data: ghana_forest_loss_spatial.geojson")

print("\n" + "=" * 60)
print("Spatial mapping complete!")
print("=" * 60)
print(f"\nGenerated {4} maps in latex_manuscript/figures/")
