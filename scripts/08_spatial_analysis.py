# Spatial Statistics and Hotspot Analysis
# Advanced spatial analysis including spatial autocorrelation and clustering

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from scipy import stats

os.chdir(r'H:\My Drive\Grad School\fall_26\AIMS\sample1')

print("=" * 60)
print("Spatial Statistics and Hotspot Analysis")
print("=" * 60)

# Load the merged spatial data
if not os.path.exists('data/spatial/ghana_forest_loss_spatial.geojson'):
    print("ERROR: Merged spatial data not found!")
    print("Please run 07_spatial_maps.py first")
    exit(1)

gdf = gpd.read_file('data/spatial/ghana_forest_loss_spatial.geojson')
print(f"\nLoaded spatial data: {len(gdf)} regions")

# Remove regions with missing data for analysis
gdf_analysis = gdf[gdf['total_loss_ha'].notna()].copy()
print(f"Regions with complete data: {len(gdf_analysis)}")

if len(gdf_analysis) < 3:
    print("ERROR: Not enough regions with data for spatial analysis")
    exit(1)

# ============================================================
# 1. Spatial Neighbors Analysis
# ============================================================
print("\n" + "-" * 60)
print("Computing spatial neighbors...")
print("-" * 60)

# Create spatial weights matrix (queen contiguity)
try:
    from libpysal.weights import Queen
    w = Queen.from_dataframe(gdf_analysis)
    print(f"\nSpatial weights matrix created:")
    print(f"  Number of regions: {w.n}")
    print(f"  Average neighbors per region: {w.mean_neighbors:.2f}")
    print(f"  Min neighbors: {min(w.cardinalities.values())}")
    print(f"  Max neighbors: {max(w.cardinalities.values())}")

    # Print neighbor relationships
    print("\nNeighbor relationships:")
    for idx, neighbors in w.neighbors.items():
        region_name = gdf_analysis.iloc[idx]['region']
        neighbor_names = [gdf_analysis.iloc[n]['region'] for n in neighbors]
        print(f"  {region_name}: {len(neighbors)} neighbors - {', '.join(neighbor_names)}")

    has_spatial_weights = True
except ImportError:
    print("WARNING: libpysal not installed. Skipping spatial autocorrelation analysis.")
    print("Install with: conda install -c conda-forge libpysal")
    has_spatial_weights = False
except Exception as e:
    print(f"WARNING: Could not create spatial weights: {e}")
    has_spatial_weights = False

# ============================================================
# 2. Moran's I (Global Spatial Autocorrelation)
# ============================================================
if has_spatial_weights:
    print("\n" + "-" * 60)
    print("Computing Moran's I (spatial autocorrelation)...")
    print("-" * 60)

    try:
        from esda.moran import Moran

        # Calculate Moran's I for different variables
        variables = {
            'total_loss_ha': 'Total Forest Loss',
            'pct_loss': 'Percentage Loss',
            'emissions_per_ha': 'Emissions Intensity'
        }

        morans_results = []

        for var, var_name in variables.items():
            moran = Moran(gdf_analysis[var], w)
            morans_results.append({
                'Variable': var_name,
                'Moran_I': moran.I,
                'Expected_I': moran.EI,
                'p_value': moran.p_sim,
                'z_score': moran.z_sim
            })

            interpretation = "Clustered" if moran.I > moran.EI and moran.p_sim < 0.05 else \
                           "Dispersed" if moran.I < moran.EI and moran.p_sim < 0.05 else \
                           "Random"

            print(f"\n{var_name}:")
            print(f"  Moran's I: {moran.I:.4f}")
            print(f"  Expected I: {moran.EI:.4f}")
            print(f"  p-value: {moran.p_sim:.4f}")
            print(f"  z-score: {moran.z_sim:.4f}")
            print(f"  Interpretation: {interpretation} pattern")

        # Save Moran's I results
        morans_df = pd.DataFrame(morans_results)
        morans_df.to_csv('latex_manuscript/tables/spatial_autocorrelation.csv', index=False)
        print("\n[OK] Saved Moran's I results to tables/spatial_autocorrelation.csv")

    except ImportError:
        print("WARNING: esda not installed. Skipping Moran's I calculation.")
        print("Install with: conda install -c conda-forge esda")
    except Exception as e:
        print(f"WARNING: Could not calculate Moran's I: {e}")

# ============================================================
# 3. Hotspot Analysis (Getis-Ord Gi*)
# ============================================================
if has_spatial_weights:
    print("\n" + "-" * 60)
    print("Computing Getis-Ord Gi* (hotspot analysis)...")
    print("-" * 60)

    try:
        from esda.getisord import G_Local

        # Calculate local G* for total loss
        y = gdf_analysis['total_loss_ha'].values
        w.transform = 'r'  # Row standardization

        lg = G_Local(y, w)

        # Add results to dataframe
        gdf_analysis['g_star'] = lg.Zs
        gdf_analysis['g_star_pval'] = lg.p_sim

        # Classify hotspots
        def classify_hotspot(z, p):
            if p > 0.05:
                return 'Not significant'
            elif z > 1.96:
                return 'Hot spot (high loss)'
            elif z < -1.96:
                return 'Cold spot (low loss)'
            else:
                return 'Not significant'

        gdf_analysis['hotspot_class'] = [classify_hotspot(z, p) for z, p in
                                          zip(gdf_analysis['g_star'], gdf_analysis['g_star_pval'])]

        print("\nHotspot Classification:")
        print(gdf_analysis[['region', 'total_loss_ha', 'g_star', 'hotspot_class']].to_string())

        # Create hotspot map
        fig, ax = plt.subplots(1, 1, figsize=(12, 10))

        # Define colors for hotspot classes
        color_map = {
            'Hot spot (high loss)': '#d7191c',
            'Cold spot (low loss)': '#2c7bb6',
            'Not significant': '#ffffbf'
        }

        gdf_analysis['color'] = gdf_analysis['hotspot_class'].map(color_map)

        gdf_analysis.plot(ax=ax, color=gdf_analysis['color'],
                         edgecolor='black', linewidth=0.5)

        # Add labels
        for idx, row in gdf_analysis.iterrows():
            centroid = row.geometry.centroid
            ax.text(centroid.x, centroid.y, row['region'],
                   fontsize=7, ha='center', va='center',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                            alpha=0.7, edgecolor='none'))

        # Create legend
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor=color, label=label)
                          for label, color in color_map.items()
                          if label in gdf_analysis['hotspot_class'].values]

        ax.legend(handles=legend_elements, loc='lower left', title='Hotspot Classification',
                 frameon=True, fancybox=True, shadow=True)

        ax.set_title('Spatial Hotspot Analysis: Forest Loss in Ghana\n(Getis-Ord Gi*, p < 0.05)',
                    fontsize=14, fontweight='bold', pad=20)
        ax.axis('off')

        plt.tight_layout()
        plt.savefig('latex_manuscript/figures/fig14_hotspot_analysis.pdf', dpi=300, bbox_inches='tight')
        print("\n[OK] Saved: fig14_hotspot_analysis.pdf")
        plt.close()

    except ImportError:
        print("WARNING: esda not installed. Skipping hotspot analysis.")
    except Exception as e:
        print(f"WARNING: Could not complete hotspot analysis: {e}")

# ============================================================
# 4. Distance-based Analysis
# ============================================================
print("\n" + "-" * 60)
print("Distance-based spatial analysis...")
print("-" * 60)

# Calculate centroids
gdf_analysis['centroid'] = gdf_analysis.geometry.centroid

# Calculate distance matrix
print("\nCalculating pairwise distances between regions...")
n_regions = len(gdf_analysis)
distance_matrix = np.zeros((n_regions, n_regions))

for i in range(n_regions):
    for j in range(n_regions):
        if i != j:
            dist = gdf_analysis.iloc[i]['centroid'].distance(gdf_analysis.iloc[j]['centroid'])
            distance_matrix[i, j] = dist / 1000  # Convert to km

# Find nearest neighbors
print("\nNearest neighbor analysis:")
for i, row in gdf_analysis.iterrows():
    distances = distance_matrix[gdf_analysis.index.get_loc(i)]
    distances[distances == 0] = np.inf  # Exclude self
    nearest_idx = np.argmin(distances)
    nearest_region = gdf_analysis.iloc[nearest_idx]['region']
    nearest_dist = distances[nearest_idx]
    print(f"  {row['region']}: nearest to {nearest_region} ({nearest_dist:.1f} km)")

# ============================================================
# 5. Summary Statistics by Spatial Location
# ============================================================
print("\n" + "-" * 60)
print("Regional statistics summary...")
print("-" * 60)

# Calculate summary statistics
summary_stats = gdf_analysis[['region', 'total_loss_ha', 'pct_loss',
                               'total_emissions_Mg', 'emissions_per_ha']].copy()

# Add area
summary_stats['area_km2'] = gdf_analysis.geometry.area / 1e6  # Convert to km²

# Calculate percentiles
summary_stats['loss_percentile'] = summary_stats['total_loss_ha'].rank(pct=True) * 100

# Classify regions by loss intensity
def classify_loss(pct):
    if pct > 30:
        return 'Very High Loss'
    elif pct > 20:
        return 'High Loss'
    elif pct > 10:
        return 'Moderate Loss'
    else:
        return 'Low Loss'

summary_stats['loss_category'] = summary_stats['pct_loss'].apply(classify_loss)

print("\nRegional Classification:")
print(summary_stats[['region', 'pct_loss', 'loss_category', 'loss_percentile']].sort_values('pct_loss', ascending=False).to_string())

# Save summary
summary_stats.to_csv('latex_manuscript/tables/spatial_summary_stats.csv', index=False)
print("\n[OK] Saved spatial summary statistics")

# ============================================================
# 6. Visualization: Loss Categories Map
# ============================================================
print("\nCreating loss category map...")

fig, ax = plt.subplots(1, 1, figsize=(12, 10))

category_colors = {
    'Very High Loss': '#a50026',
    'High Loss': '#f46d43',
    'Moderate Loss': '#fee090',
    'Low Loss': '#74add1'
}

gdf_analysis['cat_color'] = gdf_analysis['pct_loss'].apply(lambda x: category_colors[classify_loss(x)])

gdf_analysis.plot(ax=ax, color=gdf_analysis['cat_color'],
                 edgecolor='black', linewidth=0.8)

# Add labels with percentage
for idx, row in gdf_analysis.iterrows():
    centroid = row.geometry.centroid
    label = f"{row['region']}\n({row['pct_loss']:.1f}%)"
    ax.text(centroid.x, centroid.y, label,
           fontsize=7, ha='center', va='center',
           bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                    alpha=0.8, edgecolor='none'))

# Legend
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor=color, label=label)
                  for label, color in category_colors.items()]
ax.legend(handles=legend_elements, loc='lower left',
         title='Forest Loss Intensity', frameon=True,
         fancybox=True, shadow=True)

ax.set_title('Forest Loss Intensity Classification\nGhana Regions (2001-2024)',
            fontsize=14, fontweight='bold', pad=20)
ax.axis('off')

plt.tight_layout()
plt.savefig('latex_manuscript/figures/fig15_loss_categories.pdf', dpi=300, bbox_inches='tight')
print("[OK] Saved: fig15_loss_categories.pdf")
plt.close()

print("\n" + "=" * 60)
print("Spatial analysis complete!")
print("=" * 60)
print("\nGenerated files:")
print("  - Figures: fig14_hotspot_analysis.pdf, fig15_loss_categories.pdf")
print("  - Tables: spatial_autocorrelation.csv, spatial_summary_stats.csv")
