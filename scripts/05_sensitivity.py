# sensitivity analysis
# testing how results change with different carbon prices and discount rates
# need this for policy discussion

import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import pandas as pd
import os

os.chdir(r'H:\My Drive\Grad School\fall_26\AIMS\sample1')

# base parameters
T = 20
r = 0.05
K = 9.5e6
X0 = 6.2e6
a = 400
c_r = 2000
v_a = 164
e = 410
s = 1.5

# forest dynamics
def forest_dynamics(X, Y, G):
    natural_growth = r * X * (1 - X/K)
    X_next = X + natural_growth - Y + G
    return max(0, X_next)

# objective function (parameterized)
def objective(vars, p_c, delta):
    Y = vars[0::2]
    G = vars[1::2]
    X = np.zeros(T+1)
    X[0] = X0

    pv = 0
    for t in range(T):
        amenity = v_a * X[t]
        ag_revenue = a * Y[t]
        carbon_cost = p_c * e * Y[t]
        reforest_cost = c_r * G[t]
        carbon_benefit = p_c * s * G[t]
        net_benefit = amenity + ag_revenue - carbon_cost - reforest_cost + carbon_benefit
        pv += net_benefit / ((1 + delta)**t)
        X[t+1] = forest_dynamics(X[t], Y[t], G[t])

    V_T = (v_a + p_c * s / delta) * X[T]
    pv += V_T / ((1 + delta)**T)
    return -pv

def make_constraints(X0, T):
    def forest_constraint(vars):
        Y = vars[0::2]
        G = vars[1::2]
        X = np.zeros(T+1)
        X[0] = X0
        violations = []
        for t in range(T):
            X[t+1] = forest_dynamics(X[t], Y[t], G[t])
            violations.append(X[t] - Y[t])
            violations.append(K - X[t] - G[t])
            violations.append(X[t+1])
        return np.array(violations)
    return [{'type': 'ineq', 'fun': forest_constraint}]

bounds = [(0, X0), (0, K)] * T

# Sensitivity 1: Carbon price
print("Running carbon price sensitivity analysis...")
carbon_prices = [10, 15, 20, 25, 30, 35, 40, 45, 50]
results_carbon = []

x0 = np.zeros(2*T)
x0[0::2] = 50000  # initial guess for Y
x0[1::2] = 10000  # initial guess for G

for pc in carbon_prices:
    print(f"  Solving for p_c = ${pc}/Mg...")
    result = minimize(
        lambda x: objective(x, pc, 0.03),
        x0,
        method='SLSQP',
        bounds=bounds,
        constraints=make_constraints(X0, T),
        options={'maxiter': 150, 'disp': False}
    )

    Y_opt = result.x[0::2]
    G_opt = result.x[1::2]

    # calculate final forest stock
    X = np.zeros(T+1)
    X[0] = X0
    for t in range(T):
        X[t+1] = forest_dynamics(X[t], Y_opt[t], G_opt[t])

    results_carbon.append({
        'carbon_price': pc,
        'avg_deforestation': Y_opt.mean(),
        'avg_reforestation': G_opt.mean(),
        'initial_deforestation': Y_opt[0],
        'initial_reforestation': G_opt[0],
        'final_forest': X[-1],
        'pv': -result.fun
    })

    # use current solution as starting point for next
    x0 = result.x

df_carbon = pd.DataFrame(results_carbon)
print("\nCarbon price sensitivity results:")
print(df_carbon)

# Plot carbon price sensitivity
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

ax = axes[0]
ax.plot(df_carbon['carbon_price'], df_carbon['initial_deforestation']/1000,
        'ro-', linewidth=2, markersize=8, label='Deforestation')
ax.plot(df_carbon['carbon_price'], df_carbon['initial_reforestation']/1000,
        'go-', linewidth=2, markersize=8, label='Reforestation')
ax.axvline(20, color='gray', linestyle='--', alpha=0.5, label='Baseline')
ax.set_xlabel('Carbon Price (USD/Mg CO₂e)', fontsize=11)
ax.set_ylabel('Initial Period (1000 ha/year)', fontsize=11)
ax.set_title('Optimal Policy vs Carbon Price', fontsize=12)
ax.legend()
ax.grid(alpha=0.3)

ax = axes[1]
ax.plot(df_carbon['carbon_price'], df_carbon['final_forest']/1e6,
        'b-', linewidth=2, marker='s', markersize=8)
ax.axhline(X0/1e6, color='gray', linestyle='--', label='Initial stock')
ax.set_xlabel('Carbon Price (USD/Mg CO₂e)', fontsize=11)
ax.set_ylabel('Final Forest Stock (million ha)', fontsize=11)
ax.set_title('Forest Stock at Year 20', fontsize=12)
ax.legend()
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('latex_manuscript/figures/fig8_carbon_sensitivity.pdf', dpi=300, bbox_inches='tight')
print("\nSaved: fig8_carbon_sensitivity.pdf")

# Sensitivity 2: Discount rate
print("\nRunning discount rate sensitivity analysis...")
discount_rates = [0.01, 0.02, 0.03, 0.04, 0.05]
results_discount = []

x0 = np.zeros(2*T)
x0[0::2] = 50000
x0[1::2] = 10000

for dr in discount_rates:
    print(f"  Solving for delta = {dr*100}%...")
    result = minimize(
        lambda x: objective(x, 20, dr),
        x0,
        method='SLSQP',
        bounds=bounds,
        constraints=make_constraints(X0, T),
        options={'maxiter': 150, 'disp': False}
    )

    Y_opt = result.x[0::2]
    G_opt = result.x[1::2]

    X = np.zeros(T+1)
    X[0] = X0
    for t in range(T):
        X[t+1] = forest_dynamics(X[t], Y_opt[t], G_opt[t])

    results_discount.append({
        'discount_rate': dr * 100,
        'avg_deforestation': Y_opt.mean(),
        'avg_reforestation': G_opt.mean(),
        'initial_deforestation': Y_opt[0],
        'initial_reforestation': G_opt[0],
        'final_forest': X[-1],
        'pv': -result.fun
    })

    x0 = result.x

df_discount = pd.DataFrame(results_discount)
print("\nDiscount rate sensitivity results:")
print(df_discount)

# Plot discount rate sensitivity
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

ax = axes[0]
ax.plot(df_discount['discount_rate'], df_discount['initial_deforestation']/1000,
        'ro-', linewidth=2, markersize=8, label='Deforestation')
ax.plot(df_discount['discount_rate'], df_discount['initial_reforestation']/1000,
        'go-', linewidth=2, markersize=8, label='Reforestation')
ax.axvline(3, color='gray', linestyle='--', alpha=0.5, label='Baseline')
ax.set_xlabel('Discount Rate (%)', fontsize=11)
ax.set_ylabel('Initial Period (1000 ha/year)', fontsize=11)
ax.set_title('Optimal Policy vs Discount Rate', fontsize=12)
ax.legend()
ax.grid(alpha=0.3)

ax = axes[1]
ax.plot(df_discount['discount_rate'], df_discount['final_forest']/1e6,
        'b-', linewidth=2, marker='s', markersize=8)
ax.axhline(X0/1e6, color='gray', linestyle='--', label='Initial stock')
ax.set_xlabel('Discount Rate (%)', fontsize=11)
ax.set_ylabel('Final Forest Stock (million ha)', fontsize=11)
ax.set_title('Forest Stock at Year 20', fontsize=12)
ax.legend()
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('latex_manuscript/figures/fig9_discount_sensitivity.pdf', dpi=300, bbox_inches='tight')
print("Saved: fig9_discount_sensitivity.pdf")

# save sensitivity results
df_carbon.to_csv('latex_manuscript/tables/carbon_sensitivity.csv', index=False)
df_discount.to_csv('latex_manuscript/tables/discount_sensitivity.csv', index=False)

# find the threshold carbon price where deforestation drops sharply
# looking for where it drops below 25k ha/year (roughly half of current)
threshold_idx = df_carbon[df_carbon['initial_deforestation'] < 25000].index
if len(threshold_idx) > 0:
    threshold_price = df_carbon.loc[threshold_idx[0], 'carbon_price']
    print(f"\nThreshold carbon price: ~${threshold_price}/Mg")
    print("(where optimal deforestation drops below 25k ha/year)")

print("\nSensitivity analysis complete!")
