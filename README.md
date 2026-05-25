# Forest Management Under Carbon Constraints: A Dynamic Optimization Analysis for Ghana

This repository contains the complete LaTeX manuscript, data analysis scripts, and optimization results for a research study investigating optimal forest conservation strategies in Ghana. The project integrates historical tree cover loss data from Global Forest Watch (2001–2024) with a dynamic optimization framework to evaluate the trade-offs between agricultural expansion (predominantly cocoa) and ecosystem services.

## Project Objectives

1.  **Quantitative Assessment:** Document and analyze historical deforestation patterns in Ghana over the last two decades, disaggregating by driver and region.
2.  **Bio-Economic Modeling:** Develop a 100-year dynamic optimization model that accounts for logistic forest growth, carbon sequestration, amenity values, and agricultural opportunity costs.
3.  **Policy Simulation:** Identify optimal trajectories for deforestation and reforestation under various carbon pricing and discount rate scenarios.
4.  **Threshold Identification:** Determine the critical carbon price thresholds required to shift incentives toward total forest preservation.
5.  **Intervention Strategy:** Evaluate the cost-effectiveness of agricultural intensification as a primary lever for reducing land pressure.

## Methodology

### 1. Data Sources
*   **Global Forest Watch (GFW):** Annual tree cover loss and gain (2001–2024) at 30m resolution.
*   **Driver Classification:** Machine learning-based attribution (Curtis et al., 2018) identifies 89.7% of loss as commodity-driven agriculture (cocoa).
*   **Carbon Flux Model:** IPCC Tier 1 emission factors (average 410 Mg CO₂e/ha for clearing) and sequestration rates (1.5 Mg CO₂e/ha/year for regeneration).

### 2. Econometric & Analytical Framework
*   **Trend Analysis:** Decomposes annual loss into distinct phases: early acceleration (2001-2006), stabilization (2007-2015), and the recent surge (2016-2024).
*   **Regional Heterogeneity:** Analysis of high-pressure zones like the Eastern and Ashanti regions.

### 3. Dynamic Optimization Model
*   **Objective Function:** Maximize the Net Present Value (NPV) of net benefits:
    $$ \max \sum_{t=0}^{T-1} \frac{1}{(1+\delta)^t} [v_a X_t + aY_t - p_c e Y_t - c_r G_t + p_c s G_t] + \frac{V_T(X_T)}{(1+\delta)^T} $$
    Where $X_t$ is forest stock, $Y_t$ is deforestation, $G_t$ is reforestation, $p_c$ is carbon price, and $v_a$ is amenity value.
*   **State Dynamics:** Forest stock evolves via a logistic growth function $rX_t(1 - X_t/K)$ with natural regeneration parameters calibrated for West African secondary forests.
*   **Numerical Solution:** Solved using **Sequential Least Squares Programming (SLSQP)** via `scipy.optimize.minimize` in Python.

## Key Findings

### 1. The Optimality of Conservation
Under a 100-year horizon and baseline social discount rates (3%), **zero deforestation** emerges as the socially optimal path. Current historical rates (58,000 ha/year) destroy economic value equivalent to **$19.7 billion** in present-value terms compared to the optimal strategy.

### 2. Carbon Pricing Thresholds
*   A critical threshold exists at **$15–$18 per Mg CO₂e**. Above this price, optimal deforestation drops to zero as carbon penalties and sequestration rewards outweigh agricultural returns.
*   At low carbon prices ($10/Mg), agricultural opportunity costs dominate, making some level of clearing economically rational in the short term.

### 3. Agricultural Intensification
Closing just half of Ghana's cocoa yield gap (currently 500 kg/ha vs. a 2,200 kg/ha potential) would free up **600,000 hectares** for forest recovery. This represents the most cost-effective intervention, with a benefit-cost ratio exceeding **5:1**.

### 4. Implementation Gaps
*   Actual reforestation rates (11,500 ha/year) fall 96% short of the optimal initial target (264,000 ha/year).
*   Enforcement constraints (1 officer per 7,900 ha) and weak judicial deterrence currently undermine legal protection frameworks.

## Repository Structure

```
H:/My Drive/.../sample3/
├── manuscript.tex          # Main LaTeX document
├── sections/               # Chapter-wise TeX files (Intro, Lit, Results, etc.)
├── figures/                # Automated plots (Loss trends, Optimization paths)
├── tables/                 # Regression outputs and parameter summaries
└── scripts/                # Python analysis pipeline:
    ├── 01_basic_analysis.py    # Descriptive statistics
    ├── 02_driver_analysis.py   # Attribution modeling
    ├── 04_optimization.py      # Core SLSQP model execution
    └── 05_sensitivity.py       # Sensitivity testing for p_c and delta
```

### Analysis Pipeline
Requires Python 3.8+ with `numpy`, `scipy`, `pandas`, and `matplotlib`.
```bash
python scripts/run_all.py
```

---
