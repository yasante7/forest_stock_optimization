# run spatial analysis scripts only
# Run this after the basic analyses (scripts 01-05) are complete

import subprocess
import sys
import os

os.chdir(r'H:\My Drive\Grad School\fall_26\AIMS\sample1\latex_manuscript\scripts')

spatial_scripts = [
    '06_spatial_setup.py',
    '07_spatial_maps.py',
    '08_spatial_analysis.py',
    '09_temporal_spatial.py'
]

print("=" * 60)
print("Running spatial analysis scripts")
print("=" * 60)
print("\nNote: This requires internet connection for downloading")
print("      Ghana's administrative boundaries from geoBoundaries/GADM")

for i, script in enumerate(spatial_scripts, 1):
    print(f"\n[{i}/{len(spatial_scripts)}] Running {script}...")
    print("-" * 60)

    try:
        result = subprocess.run([sys.executable, script],
                              capture_output=True,
                              text=True,
                              timeout=600)  # 10 min timeout for downloads

        print(result.stdout)

        if result.returncode != 0:
            print(f"ERROR in {script}:")
            print(result.stderr)

            # For spatial setup, provide helpful message
            if script == '06_spatial_setup.py':
                print("\nTIP: If download failed, you can manually download Ghana shapefiles from:")
                print("  - https://www.geoboundaries.org/")
                print("  - https://gadm.org/download_country.html")
                print("  Save as: data/spatial/ghana_regions.geojson")
                print("\nContinuing with remaining scripts...")
                continue  # Don't stop, try other scripts

            print("\nStopping here. Fix the error and try again.")
            sys.exit(1)

    except subprocess.TimeoutExpired:
        print(f"ERROR: {script} took too long (>10 min).")
        if script == '06_spatial_setup.py':
            print("This might be due to slow internet. Try running it manually.")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR running {script}: {str(e)}")
        sys.exit(1)

print("\n" + "=" * 60)
print("Spatial analysis complete!")
print("=" * 60)
print("\nGenerated files:")
print("  Spatial data: data/spatial/*.geojson")
print("  Figures: latex_manuscript/figures/fig10-18*.pdf")
print("  Tables: latex_manuscript/tables/spatial_*.csv, table2_temporal.tex")
