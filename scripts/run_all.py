# run all analysis scripts
# this will generate all figures and tables for the manuscript
# make sure you're in the econ conda environment!

import subprocess
import sys
import os

os.chdir(r'H:\My Drive\Grad School\fall_26\AIMS\sample1\latex_manuscript\scripts')

scripts = [
    '01_basic_analysis.py',
    '02_driver_analysis.py',
    '03_regional_analysis.py',
    '04_optimization.py',
    '05_sensitivity.py',
    '06_spatial_setup.py',
    '07_spatial_maps.py',
    '08_spatial_analysis.py',
    '09_temporal_spatial.py'
]

print("=" * 60)
print("Running all analysis scripts")
print("=" * 60)

for i, script in enumerate(scripts, 1):
    print(f"\n[{i}/{len(scripts)}] Running {script}...")
    print("-" * 60)

    try:
        result = subprocess.run([sys.executable, script],
                              capture_output=True,
                              text=True,
                              timeout=300)  # 5 min timeout per script

        print(result.stdout)

        if result.returncode != 0:
            print(f"ERROR in {script}:")
            print(result.stderr)
            print("\nStopping here. Fix the error and try again.")
            sys.exit(1)

    except subprocess.TimeoutExpired:
        print(f"ERROR: {script} took too long (>5 min). Check for infinite loops.")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR running {script}: {str(e)}")
        sys.exit(1)

print("\n" + "=" * 60)
print("All scripts completed successfully!")
print("=" * 60)
print("\nGenerated files:")
print("  Figures: latex_manuscript/figures/*.pdf")
print("  Tables: latex_manuscript/tables/*.csv, *.tex")
print("\nYou can now compile the LaTeX manuscript.")
