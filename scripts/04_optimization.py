# optimization model
# implementing the dynamic forest management model
# based on the equations in model.tex
# this took forever to get right...

import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import pandas as pd
import os

os.chdir(r'H:\My Drive\Grad School\fall_26\AIMS\sample1')

# Model parameters (from methodology section)
T = 100  # time horizon (extended to 100 years)
delta = 0.03  # discount rate
r = 0.05  # forest growth rate
K = 9.5e6  # carrying capacity (ha)
X0 = 6.2e6  # initial forest stock (ha) - from 2024 data

# economic parameters
p_c = 20  # carbon price (USD/Mg CO2e)
a = 400  # agricultural revenue (USD/ha/year)
c_r = 2000  # reforestation cost (USD/ha)
v_a = 164  # amenity value (USD/ha/year)
e = 410  # emissions per ha (Mg CO2e/ha)
s = 1.5  # sequestration rate (Mg CO2e/ha/year)

print("Model parameters:")
print(f"Time horizon: {T} years")
print(f"Initial forest: {X0/1e6:.2f} million ha")
print(f"Carbon price: ${p_c}/Mg")
print(f"Discount rate: {delta*100}%")

# Forest dynamics function
def forest_dynamics(X, Y, G):
    """Calculate next period forest stock"""
    natural_growth = r * X * (1 - X/K)
    X_next = X + natural_growth - Y + G
    return max(0, X_next)  # can't be negative

# Objective function
def objective(vars):
    """
    Calculate negative PV of net benefits (we minimize this)
    vars = [Y0, G0, Y1, G1, ..., Y_{T-1}, G_{T-1}]
    """
    Y = vars[0::2]  # deforestation (even indices)
    G = vars[1::2]  # reforestation (odd indices)

    # track forest stock
    X = np.zeros(T+1)
    X[0] = X0

    pv = 0
    for t in range(T):
        # period benefits
        amenity = v_a * X[t]
        ag_revenue = a * Y[t]
        carbon_cost = p_c * e * Y[t]
        reforest_cost = c_r * G[t]
        carbon_benefit = p_c * s * G[t]

        net_benefit = amenity + ag_revenue - carbon_cost - reforest_cost + carbon_benefit
        pv += net_benefit / ((1 + delta)**t)

        # update forest stock
        X[t+1] = forest_dynamics(X[t], Y[t], G[t])

    # terminal value
    V_T = (v_a + p_c * s / delta) * X[T]
    pv += V_T / ((1 + delta)**T)

    return -pv  # negative because we're minimizing

# Constraints
def make_constraints(X0, T):
    constraints = []

    # forest dynamics and non-negativity
    def forest_constraint(vars):
        Y = vars[0::2]
        G = vars[1::2]
        X = np.zeros(T+1)
        X[0] = X0

        violations = []
        for t in range(T):
            X[t+1] = forest_dynamics(X[t], Y[t], G[t])
            # check constraints
            violations.append(X[t] - Y[t])  # can't deforest more than exists
            violations.append(K - X[t] - G[t])  # can't exceed capacity
            violations.append(X[t+1])  # forest must be non-negative

        return np.array(violations)

    constraints.append({'type': 'ineq', 'fun': forest_constraint})

    return constraints

# Bounds for variables
# Y and G must be non-negative
bounds = []
for t in range(T):
    bounds.append((0, X0))  # Y_t bounds (rough upper bound)
    bounds.append((0, K))   # G_t bounds

# Initial guess - start with recent trends
# historical average around 50k ha/year loss, 10k ha/year gain
Y_init = np.full(T, 50000)
G_init = np.full(T, 10000)
x0 = np.zeros(2*T)
x0[0::2] = Y_init
x0[1::2] = G_init

print("\nSolving optimization problem...")
print("This might take a minute...")

# Solve
result = minimize(
    objective,
    x0,
    method='SLSQP',
    bounds=bounds,
    constraints=make_constraints(X0, T),
    options={'maxiter': 500, 'disp': True, 'ftol': 1e-9}
)

if result.success:
    print("\nOptimization converged!")
else:
    print("\nWarning: Optimization may not have fully converged")
    print(result.message)

# Extract results
Y_opt = result.x[0::2]
G_opt = result.x[1::2]
PV_opt = -result.fun

# Calculate optimal forest path
X_opt = np.zeros(T+1)
X_opt[0] = X0
for t in range(T):
    X_opt[t+1] = forest_dynamics(X_opt[t], Y_opt[t], G_opt[t])

print(f"\nOptimal PV of net benefits: ${PV_opt/1e9:.2f} billion")
print(f"Initial deforestation: {Y_opt[0]:,.0f} ha/year")
print(f"Initial reforestation: {G_opt[0]:,.0f} ha/year")
print(f"Final forest stock: {X_opt[-1]/1e6:.2f} million ha ({(X_opt[-1]/X0 - 1)*100:+.1f}%)")

# Calculate key metrics for plotting
net_loss_rate = Y_opt - G_opt  # net loss = deforestation - reforestation
time_index = np.arange(T+1)  # 0 to T for X_opt
time_index_flow = np.arange(T)  # 0 to T-1 for flows

# Calculate MSY (Maximum Sustainable Yield) stock level
X_MSY = K / 2  # logistic growth maximizes at K/2

# Plot in style similar to sample_opt.png
fig, axes = plt.subplots(2, 1, figsize=(12, 10))

# Panel 1: Forest Stock Over Time
ax = axes[0]
ax.plot(time_index, X_opt/1e6, 'b-', linewidth=2.5, label='Forest Stock')
ax.axhline(K/1e6, color='black', linestyle='--', linewidth=1.5, label='Carrying Capacity')
ax.axhline(X_MSY/1e6, color='orange', linestyle=':', linewidth=1.5, label='MSY Stock Level')
ax.axhline(X0/1e6, color='gray', linestyle=':', linewidth=1.5, label='Initial Stock')
ax.set_ylabel('Forest Stock', fontsize=12)
ax.set_title('Forest Stock Over Time', fontsize=14, fontweight='bold')
ax.legend(loc='lower right', frameon=True, fontsize=10)
ax.grid(True, alpha=0.3)
ax.set_xlim(0, T)

# Panel 2: Net Loss Rate Over Time
ax = axes[1]
ax.plot(time_index_flow, net_loss_rate/1e6, 'r--', linewidth=2, label='Net Loss Rate', marker='')
ax.axhline(0, color='black', linestyle='-', linewidth=0.8)
ax.set_ylabel('Flow Rates (Million ha/year)', fontsize=12)
ax.set_xlabel('Time (Years)', fontsize=12)
ax.set_title('Net Loss Rate Over Time', fontsize=14, fontweight='bold')
ax.legend(loc='lower right', frameon=True, fontsize=10)
ax.grid(True, alpha=0.3)
ax.set_xlim(0, T)

plt.tight_layout()
plt.savefig('latex_manuscript/figures/fig7_optimization.pdf', dpi=300, bbox_inches='tight')
plt.savefig('latex_manuscript/figures/fig7_optimization.png', dpi=300, bbox_inches='tight')
print("\nSaved: fig7_optimization.pdf and fig7_optimization.png")

# Additional detailed plots for manuscript
fig2, axes2 = plt.subplots(2, 2, figsize=(14, 10))

years = np.arange(2024, 2024+T+1)

# Deforestation
ax = axes2[0, 0]
ax.plot(years[:-1], Y_opt/1000, 'r-', linewidth=2, marker='o', markersize=3, markevery=5)
ax.axhline(58, color='gray', linestyle='--', label='Historical avg (2020-24)')
ax.set_ylabel('Deforestation (1000 ha/year)', fontsize=11)
ax.set_title('Optimal Deforestation Path', fontsize=12)
ax.legend()
ax.grid(alpha=0.3)

# Reforestation
ax = axes2[0, 1]
ax.plot(years[:-1], G_opt/1000, 'g-', linewidth=2, marker='o', markersize=3, markevery=5)
ax.axhline(11.5, color='gray', linestyle='--', label='Historical avg')
ax.set_ylabel('Reforestation (1000 ha/year)', fontsize=11)
ax.set_title('Optimal Reforestation Path', fontsize=12)
ax.legend()
ax.grid(alpha=0.3)

# Forest stock
ax = axes2[1, 0]
ax.plot(years, X_opt/1e6, 'b-', linewidth=2, marker='s', markersize=3, markevery=5)
ax.set_ylabel('Forest Stock (million ha)', fontsize=11)
ax.set_xlabel('Year', fontsize=11)
ax.set_title('Optimal Forest Stock Trajectory', fontsize=12)
ax.grid(alpha=0.3)

# Net change
net_change = G_opt - Y_opt
ax = axes2[1, 1]
ax.bar(years[:-1], net_change/1000, color=['red' if x < 0 else 'green' for x in net_change],
       alpha=0.7, width=0.8)
ax.axhline(0, color='black', linewidth=0.5)
ax.set_ylabel('Net Change (1000 ha/year)', fontsize=11)
ax.set_xlabel('Year', fontsize=11)
ax.set_title('Net Forest Change (Reforestation - Deforestation)', fontsize=12)
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('latex_manuscript/figures/fig7_optimization_detailed.pdf', dpi=300, bbox_inches='tight')
print("Saved: fig7_optimization_detailed.pdf")

# Save results to CSV for reference
results_df = pd.DataFrame({
    'year': years[:-1],
    'deforestation_ha': Y_opt,
    'reforestation_ha': G_opt,
    'forest_stock_ha': X_opt[:-1],
    'net_change_ha': net_change,
    'net_loss_rate_ha': net_loss_rate
})
results_df.to_csv('latex_manuscript/tables/optimization_results.csv', index=False)
print("Saved: optimization_results.csv")

# Save summary statistics for manuscript
summary_stats = {
    'metric': [
        'Initial Forest Stock (million ha)',
        'Final Forest Stock (million ha)',
        'Carrying Capacity (million ha)',
        'MSY Stock Level (million ha)',
        'Average Annual Deforestation (1000 ha/year)',
        'Average Annual Reforestation (1000 ha/year)',
        'Average Net Loss Rate (1000 ha/year)',
        'Total Net Change (million ha)',
        'Percent Change from Initial (%)',
        'Present Value of Net Benefits (billion USD)',
        'Time Horizon (years)',
        'Discount Rate (%)',
        'Carbon Price (USD/Mg CO2e)',
        'Growth Rate (%)'
    ],
    'value': [
        f'{X0/1e6:.2f}',
        f'{X_opt[-1]/1e6:.2f}',
        f'{K/1e6:.2f}',
        f'{X_MSY/1e6:.2f}',
        f'{Y_opt.mean()/1000:.2f}',
        f'{G_opt.mean()/1000:.2f}',
        f'{net_loss_rate.mean()/1000:.2f}',
        f'{(X_opt[-1] - X0)/1e6:+.2f}',
        f'{((X_opt[-1]/X0 - 1)*100):+.1f}',
        f'{PV_opt/1e9:.2f}',
        f'{T}',
        f'{delta*100:.1f}',
        f'{p_c:.0f}',
        f'{r*100:.1f}'
    ]
}
summary_df = pd.DataFrame(summary_stats)
summary_df.to_csv('latex_manuscript/tables/optimization_summary.csv', index=False)
print("Saved: optimization_summary.csv")

print("\nOptimization analysis complete!")
