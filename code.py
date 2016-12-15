import numpy as np
from cvxpy import *

n = 3;

E = [(0,2), (1,2)]
J = [[0,2], [1]]

def choose_speeds(n, E, J):
    S = Variable(n)
    R = Variable(n)
    constraints = []

    # non-negativity
    for i in range(0,n):
        constraints.append(S[i] >= 0)
        constraints.append(R[i] >= 0)

    # makespan
    for i in range(0,n):
        constraints.append(S[i] + R[i] <= 1)

    # precedence
    for i, j in E:
        constraints.append(S[i] + R[i] <= S[j])

    # one job at a time
    for A in J:
        for i in range(0, len(A)-1):
            constraints.append(S[A[i]] + R[A[i]] <= S[A[i+1]])

    # objective, assuming cubic power
    obj = Minimize(power(pnorm(R, -2), -2))

    # Form and solve problem.
    prob = Problem(obj, constraints)
    prob.solve(verbose=False,feastol=1e-09)

    return (prob.status, prob.value, S.value, R.value)


print(choose_speeds(n, E, J))
