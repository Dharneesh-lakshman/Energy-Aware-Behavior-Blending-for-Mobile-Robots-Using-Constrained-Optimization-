import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

# -----------------------------
# 1️⃣ LOAD DATASET
# -----------------------------
df = pd.read_excel("dataset_15_each.xlsx")

# Ensure correct sorting
df = df.sort_values(by=["Mode", "Time_s"])

# -----------------------------
# 2️⃣ COMPUTE METRICS
# -----------------------------

# Compute power
df["Power"] = df["Voltage_V"] * df["Current_A"]

# Compute time difference per mode
df["dt"] = df.groupby("Mode")["Time_s"].diff().fillna(0)

# Energy
df["Energy"] = df["Power"] * df["dt"]

# Path Error
df["Path_Error"] = np.sqrt(
    (df["X_actual"] - df["X_ref"])**2 +
    (df["Y_actual"] - df["Y_ref"])**2
)

# Risk Index
df["Risk"] = 1 / (df["Obstacle_Distance_m"] + 0.001)

# -----------------------------
# 3️⃣ AVERAGE PER MODE
# -----------------------------
summary = df.groupby("Mode").agg({
    "Energy": "sum",
    "Path_Error": "mean",
    "Risk": "mean"
}).reset_index()

print("\n===== MODE METRICS =====")
print(summary)

# Extract values
E_fast = summary[summary["Mode"]=="Fast"]["Energy"].values[0]
E_slow = summary[summary["Mode"]=="Slow"]["Energy"].values[0]
E_sensor = summary[summary["Mode"]=="Sensor"]["Energy"].values[0]

S_fast = summary[summary["Mode"]=="Fast"]["Path_Error"].values[0]
S_slow = summary[summary["Mode"]=="Slow"]["Path_Error"].values[0]
S_sensor = summary[summary["Mode"]=="Sensor"]["Path_Error"].values[0]

R_fast = summary[summary["Mode"]=="Fast"]["Risk"].values[0]
R_slow = summary[summary["Mode"]=="Slow"]["Risk"].values[0]
R_sensor = summary[summary["Mode"]=="Sensor"]["Risk"].values[0]

# -----------------------------
# 4️⃣ CONSTRAINT LIMITS
# -----------------------------
S_max = 0.20 # adjust if needed
R_max = 1.2  # adjust if needed

# -----------------------------
# 5️⃣ OPTIMIZATION
# -----------------------------
def objective(w):
    wf, ws, wc = w
    return wf*E_fast + ws*E_slow + wc*E_sensor

def constraint_sum(w):
    return w[0] + w[1] + w[2] - 1

def constraint_error(w):
    return S_max - (w[0]*S_fast + w[1]*S_slow + w[2]*S_sensor)

def constraint_risk(w):
    return R_max - (w[0]*R_fast + w[1]*R_slow + w[2]*R_sensor)

constraints = [
    {'type':'eq','fun':constraint_sum},
    {'type':'ineq','fun':constraint_error},
    {'type':'ineq','fun':constraint_risk}
]

bounds = [(0,1),(0,1),(0,1)]
initial_guess = [0.3,0.3,0.4]

result = minimize(objective, initial_guess,
                  bounds=bounds,
                  constraints=constraints)

wf_opt, ws_opt, wc_opt = result.x

E_opt = objective(result.x)
S_opt = wf_opt*S_fast + ws_opt*S_slow + wc_opt*S_sensor
R_opt = wf_opt*R_fast + ws_opt*R_slow + wc_opt*R_sensor

print("\n===== OPTIMIZATION RESULT =====")
print("Fast Weight:", round(wf_opt,3))
print("Slow Weight:", round(ws_opt,3))
print("Sensor Weight:", round(wc_opt,3))
print("Optimized Energy:", round(E_opt,2))
print("Optimized Path Error:", round(S_opt,3))
print("Optimized Risk:", round(R_opt,3))

S_values = [0.15, 0.2, 0.25, 0.3]
results = []

for S_max in S_values:

    def constraint_error(w):
        return S_max - (w[0]*S_fast + w[1]*S_slow + w[2]*S_sensor)

    constraints = [
        {'type':'eq','fun':constraint_sum},
        {'type':'ineq','fun':constraint_error},
        {'type':'ineq','fun':constraint_risk}
    ]

    result = minimize(objective, initial_guess,
                      bounds=bounds,
                      constraints=constraints)

    wf, ws, wc = result.x
    E_final = objective(result.x)

    results.append([S_max, wf, ws, wc, E_final])

import pandas as pd
df_sensitivity = pd.DataFrame(results, 
                columns=["S_max","Fast_w","Slow_w","Sensor_w","Energy"])

print(df_sensitivity)

print("Constraint Activity Check:")
print("Final Error - S_max =", S_opt - 0.2)
print("Final Risk - R_max =", R_opt - 1.2)

print("\nEnergy Reduction Compared to Sensor:")
reduction = ((E_sensor - E_opt)/E_sensor)*100
print(round(reduction,2), "%")

import matplotlib.pyplot as plt

plt.figure()
plt.plot(df_sensitivity["S_max"], df_sensitivity["Energy"], marker='o')
plt.xlabel("Tracking Constraint (S_max)")
plt.ylabel("Optimized Energy")
plt.title("Energy vs Tracking Constraint")
plt.grid(True)
plt.show()

comparison = {
    "Mode": ["Fast", "Sensor", "Slow", "Optimized"],
    "Energy": [E_fast, E_sensor, E_slow, E_opt],
    "Path_Error": [S_fast, S_sensor, S_slow, S_opt],
    "Risk": [R_fast, R_sensor, R_slow, R_opt]
}

df_compare = pd.DataFrame(comparison)
print(df_compare)

print("\nEnergy Reduction Compared to Fast:",
      round((E_fast - E_opt)/E_fast * 100, 2), "%")

print("Energy Reduction Compared to Sensor:",
      round((E_sensor - E_opt)/E_sensor * 100, 2), "%")

print("Energy Increase Compared to Slow:",
      round((E_opt - E_slow)/E_slow * 100, 2), "%")
# -----------------------------
# 6️⃣ PLOTS
# -----------------------------

labels = ["Fast","Slow","Sensor","Optimized"]
energy_values = [E_fast,E_slow,E_sensor,E_opt]
error_values = [S_fast,S_slow,S_sensor,S_opt]
risk_values = [R_fast,R_slow,R_sensor,R_opt]

plt.figure()
plt.bar(labels, energy_values)
plt.title("Energy Comparison")
plt.ylabel("Energy")
plt.show()

plt.figure()
plt.bar(labels, error_values)
plt.title("Path Error Comparison")
plt.ylabel("Average Error")
plt.show()

plt.figure()
plt.bar(labels, risk_values)
plt.title("Risk Comparison")
plt.ylabel("Average Risk")
plt.show()