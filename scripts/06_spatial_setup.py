# Spatial Setup - Download Ghana boundaries
# This script downloads Ghana's administrative boundaries
# and prepares spatial data for visualization

import geopandas as gpd
import pandas as pd
import os
import requests
import json

os.chdir(r'H:\My Drive\Grad School\fall_26\AIMS\sample1')

print("=" * 60)
print("Setting up spatial data for Ghana")
print("=" * 60)

# Create directory for spatial data
os.makedirs('data/spatial', exist_ok=True)

# Method 1: Use Natural Earth data (direct download)
print("\nDownloading country boundary...")
try:
    url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
    world = gpd.read_file(url)
    ghana_country = world[world.NAME == 'Ghana'].copy()
    ghana_country.to_file('data/spatial/ghana_country.geojson', driver='GeoJSON')
    print(f"[OK] Saved country boundary: {ghana_country.shape[0]} feature")
except Exception as e:
    print(f"[ERROR] Error downloading country boundary: {e}")

# Method 2: Try to get admin boundaries from geoBoundaries API
print("\nAttempting to download administrative regions...")
try:
    # geoBoundaries API for Ghana admin level 1 (regions)
    url = "https://www.geoboundaries.org/api/current/gbOpen/GHA/ADM1/"
    response = requests.get(url, timeout=30)

    if response.status_code == 200:
        data = response.json()
        geojson_url = data.get('gjDownloadURL')

        if geojson_url:
            print(f"  Downloading from: {geojson_url}")
            gdf = gpd.read_file(geojson_url)

            # Save the data
            gdf.to_file('data/spatial/ghana_regions.geojson', driver='GeoJSON')
            print(f"[OK] Saved regional boundaries: {len(gdf)} regions")
            print(f"  Columns: {gdf.columns.tolist()}")
            print(f"\nRegion names in shapefile:")
            if 'shapeName' in gdf.columns:
                print(gdf[['shapeName']].sort_values('shapeName'))
            elif 'NAME_1' in gdf.columns:
                print(gdf[['NAME_1']].sort_values('NAME_1'))
        else:
            print("[ERROR] No download URL found in API response")
    else:
        print(f"[ERROR] API request failed with status code: {response.status_code}")

except Exception as e:
    print(f"[ERROR] Error downloading regional boundaries: {e}")
    print("  You may need to download manually from:")
    print("  https://www.geoboundaries.org/downloadCGAZ.html")

# Alternative: GADM data
print("\nTrying alternative source (GADM)...")
try:
    gadm_url = "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_GHA_1.json"
    print(f"  Downloading from GADM: {gadm_url}")
    gdf_gadm = gpd.read_file(gadm_url)
    gdf_gadm.to_file('data/spatial/ghana_regions_gadm.geojson', driver='GeoJSON')
    print(f"[OK] Saved GADM boundaries: {len(gdf_gadm)} regions")
    print(f"  Columns: {gdf_gadm.columns.tolist()}")
    if 'NAME_1' in gdf_gadm.columns:
        print(f"\nGADM region names:")
        print(gdf_gadm[['NAME_1']].sort_values('NAME_1'))
except Exception as e:
    print(f"[ERROR] Error downloading GADM data: {e}")

print("\n" + "=" * 60)
print("Spatial setup complete!")
print("=" * 60)
print("\nNext steps:")
print("  1. Check data/spatial/ folder for downloaded files")
print("  2. Run 07_spatial_maps.py to create spatial visualizations")
print("  3. Run 08_spatial_analysis.py for spatial statistics")
