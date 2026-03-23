# Energy-Aware Behavior Blending for Mobile Robots Using Constrained Optimization

## Overview
This project focuses on improving energy efficiency in mobile robot navigation using a constrained optimization approach. The objective is to minimize energy consumption while maintaining path tracking accuracy and ensuring safe navigation near obstacles.

---

## Objectives
- Minimize energy consumption  
- Maintain path tracking accuracy  
- Ensure safe navigation  
- Optimize robot behavior  

---

## Methodology

The system works in the following steps:

1. Collect data:
   - Voltage (V)
   - Current (I)
   - Robot position (X, Y)
   - Obstacle distance (d)

2. Compute performance metrics:
   - Energy consumption
   - Path tracking error
   - Risk index

3. Apply optimization:
   - Find optimal weights for different navigation modes

4. Generate final motion:
   - Combine fast, slow, and sensor behaviors

---

## Mathematical Model

### Energy Calculation
Power:
P = V * I

Total Energy:
E = sum(P * dt)

---

### Path Tracking Error
S = sqrt((x_actual - x_ref)^2 + (y_actual - y_ref)^2)

---

### Risk Index
R = 1 / (d + epsilon)

---

## Optimization Model

Objective:
Minimize E(w)

Where:
E(w) = wf * Ef + ws * Es + wc * Ec

---

Constraints:

S(w) <= S_max  
R(w) <= R_max  

wf + ws + wc = 1  

wf >= 0, ws >= 0, wc >= 0  

This project demonstrates how optimization techniques can be applied to improve energy efficiency in autonomous robotic systems.

---


