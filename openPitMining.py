#!/usr/bin/env python3

import sys
import io
import os
import pulp
from pulp import LpProblem, LpMaximize, LpVariable, LpBinary, lpSum, PULP_CBC_CMD, LpStatusOptimal

# Model data
cost = []
for i in range(18):
    if (i < 8):
      cost.append(100)
    elif (i < 14 and i >= 8):
      cost.append(200)
    else:
      cost.append(300)

cost[8] = 1000
cost[13] = 1000
cost[14] = 1000
cost[15] = 1000
cost[17] = 1000

value = []
for i in range(18):
    value.append(0)

value[0] = 200
value[6] = 300
value[9] = 500
value[11] = 200
value[16] = 1000 
value[17] = 1200

edges = []

for i in range(8,14):
    edges.append([i,i-8])
    edges.append([i,i-7])
    edges.append([i,i-6])

for i in range(14,18):
    edges.append([i,i-6])
    edges.append([i,i-5])
    edges.append([i,i-4])


# Optimization
def optimize(cost, value_vec, edges, output=False):

    # Define problem
    prob = LpProblem("openPitMining", LpMaximize)

    n = len(cost)  # number of blocks

    # Indicator variable for each block (binary)
    xb = [LpVariable(f"x{i}", cat=LpBinary) for i in range(n)]

    # Objective
    prob += lpSum((value_vec[i] - cost[i]) * xb[i] for i in range(n))

    # Precedence constraints
    for u, v in edges:
        prob += xb[u] <= xb[v]

    # Configure solver (CBC by default in PuLP)
    log_str = ""
    if output:
        log_path = os.path.join(os.path.dirname(__file__), "cbc.log")
        # When using logPath, keep msg False to avoid warning and duplicate output
        solver = PULP_CBC_CMD(msg=False, timeLimit=10, logPath=log_path)
    else:
        solver = PULP_CBC_CMD(msg=False, timeLimit=10)

    prob.solve(solver)

    # Collect log output if requested
    if output:
        log_path = os.path.join(os.path.dirname(__file__), "cbc.log")
        try:
            if os.path.exists(log_path):
                with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                    log_str = f.read()
                try:
                    os.remove(log_path)
                except Exception:
                    pass
        except Exception:
            pass

    # Check optimality (mimic prior behavior of requiring optimal solution)
    if prob.status != LpStatusOptimal:
        return ["error"]

    # Build solution vector in variable index order
    solution = [var.value() for var in xb]
    solution.append(pulp.value(prob.objective))

    return [solution, log_str]

def handleoptimize(jsdict):
    if 'cost' in jsdict and 'value' in jsdict and 'edges' in jsdict:
        solution = optimize(jsdict['cost'], jsdict['value'], jsdict['edges'])
        return {'solution': solution }


if __name__ == '__main__':
    import json
    jsdict = json.load(sys.stdin)
    jsdict = handleoptimize(jsdict)
    print('Content-Type: application/json\n\n')
    print(json.dumps(jsdict))
