# Analysis Scripts - README

## Overview

These Python scripts generate all figures and tables for the manuscript. They're organized to run sequentially, each building on the previous analysis.

## Scripts

### Core Analysis Scripts (01-05)

1. **01_basic_analysis.py** - Time series of forest loss and CO2 emissions
   - Generates: fig1_annual_loss.pdf, fig2_emissions.pdf
   - Summary stats saved to summary_stats.txt

2. **02_driver_analysis.py** - What's causing deforestation?
   - Generates: fig3_drivers.pdf, fig4_drivers_time.pdf
   - Driver breakdown by period
   - Saves: driver_summary.csv

3. **03_regional_analysis.py** - Where is deforestation happening?
   - Generates: fig5_regional.pdf, fig6_regional_trends.pdf
   - LaTeX table: table1_regional.tex

4. **04_optimization.py** - Dynamic optimization model
   - Generates: fig7_optimization.pdf
   - Optimal deforestation/reforestation paths
   - Saves: optimization_results.csv

5. **05_sensitivity.py** - Carbon price and discount rate sensitivity
   - Generates: fig8_carbon_sensitivity.pdf, fig9_discount_sensitivity.pdf
   - Finds threshold carbon price
   - Saves: carbon_sensitivity.csv, discount_sensitivity.csv

### Spatial Analysis Scripts (06-09)

6. **06_spatial_setup.py** - Download Ghana administrative boundaries
   - Downloads shapefiles from geoBoundaries/GADM APIs
   - Saves to: data/spatial/ghana_regions.geojson
   - **Requires internet connection**

7. **07_spatial_maps.py** - Create choropleth maps
   - Generates: fig10-13 (spatial maps)
     - fig10_spatial_total_loss.pdf - Total loss by region
     - fig11_spatial_pct_loss.pdf - Percentage loss by region
     - fig12_spatial_emissions.pdf - Emissions intensity map
     - fig13_spatial_panel.pdf - 4-panel combined view
   - Uses geopandas for spatial visualization
   - Saves: ghana_forest_loss_spatial.geojson (merged spatial data)

8. **08_spatial_analysis.py** - Advanced spatial statistics
   - Generates: fig14_hotspot_analysis.pdf, fig15_loss_categories.pdf
   - Spatial autocorrelation (Moran's I)
   - Hotspot detection (Getis-Ord Gi*)
   - Spatial neighbors analysis
   - **Requires: libpysal, esda** (optional, skips if not installed)
   - Saves: spatial_autocorrelation.csv, spatial_summary_stats.csv

9. **09_temporal_spatial.py** - Temporal-spatial dynamics
   - Generates: fig16-18
     - fig16_temporal_spatial.pdf - Loss by time period (4 periods)
     - fig17_change_detection.pdf - Early vs recent comparison
     - fig18_trend_map.pdf - Annual trends by region
   - Time series analysis by region
   - Change detection (2001-2006 vs 2019-2024)
   - Linear trend analysis
   - Saves: temporal_trends.csv, temporal_summary.csv, table2_temporal.tex

## How to Run

### Option 1: Run all scripts at once
```bash
conda activate econ
cd latex_manuscript/scripts
python run_all.py
```
This runs all 9 scripts sequentially (takes ~5-10 minutes)

### Option 2: Run core analysis only (no spatial)
```bash
conda activate econ
cd latex_manuscript/scripts
python run_all.py --no-spatial  # Not implemented yet, run 01-05 manually
```

### Option 3: Run spatial analysis separately
```bash
conda activate econ
cd latex_manuscript/scripts
python run_spatial.py
```
This runs only scripts 06-09. Use this if you already ran 01-05.

### Option 4: Run individually
```bash
conda activate econ
cd latex_manuscript/scripts
python 01_basic_analysis.py
python 02_driver_analysis.py
# ... etc
```

## Requirements

### Core Analysis (Scripts 01-05)
- pandas
- matplotlib
- numpy
- scipy

### Spatial Analysis (Scripts 06-09)
- geopandas
- requests (for downloading shapefiles)
- libpysal (optional, for spatial weights)
- esda (optional, for Moran's I and hotspot analysis)

All should be installed in your `econ` conda environment.

**To install optional spatial packages:**
```bash
conda activate econ
conda install -c conda-forge geopandas libpysal esda
```

## Output Locations

- **Figures**: `latex_manuscript/figures/`
  - fig1-fig9: Core analysis
  - fig10-fig18: Spatial analysis
- **Tables**: `latex_manuscript/tables/`
  - CSV files: summary statistics
  - TEX files: LaTeX-ready tables
- **Spatial data**: `data/spatial/`
  - Downloaded shapefiles
  - Merged spatial datasets

## Generated Files Summary

### Figures (18 total)
1-2: Time series (loss & emissions)
3-4: Drivers analysis
5-6: Regional analysis (bar charts & trends)
7: Optimization results
8-9: Sensitivity analysis
10-13: Spatial maps (choropleth)
14-15: Spatial statistics (hotspots)
16-18: Temporal-spatial dynamics

### Tables (LaTeX & CSV)
- table1_regional.tex - Regional forest loss summary
- table2_temporal.tex - Temporal summary by region
- driver_summary.csv
- optimization_results.csv
- carbon_sensitivity.csv, discount_sensitivity.csv
- spatial_autocorrelation.csv
- spatial_summary_stats.csv
- temporal_trends.csv, temporal_summary.csv

## Notes

- Scripts assume you're running from the sample1 root directory or handle paths appropriately
- Optimization scripts (04 & 05) may take a few minutes to run
- Spatial setup (06) requires internet connection for downloading boundaries
- Spatial analysis (08) will skip advanced statistics if libpysal/esda not installed
- If a script fails, check that data files are in the correct locations
- The scripts include comments explaining what each part does

## Troubleshooting

**"File not found" errors**: Check that you're in the right directory and data paths are correct

**Optimization not converging**: Try adjusting the initial guess or increasing maxiter

**Memory errors**: The sensitivity analysis loops can be memory-intensive; reduce the number of parameter values tested

**Spatial download fails**:
- Check internet connection
- Manually download from https://www.geoboundaries.org/ or https://gadm.org/
- Save as: data/spatial/ghana_regions.geojson

**Region names don't match**: The scripts try multiple matching strategies. Check the standardize_name() function in the spatial scripts.

**libpysal/esda not installed**: Script 08 will skip advanced spatial statistics but still generate basic maps

## For the Manuscript

After running these scripts:
1. Check that all figures were generated (should have fig1-fig18)
2. Review the tables folder for summary stats
3. Compile the LaTeX manuscript - it should automatically include these figures
4. If figure quality looks off, try increasing dpi in savefig() calls

---

Scripts written with realistic student workflow - trial/error, debugging comments, etc.
Not meant to be perfect production code, just functional analysis for a term paper.
