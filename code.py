import numpy as np
from cvxpy import *

# tree
class Node:
    def __init__(self, i, children=[]):
        self.i = i
        self.children = children

    def __str__(self):
        if self.children:
            return "(%d %s)" % (self.i, " ".join(str(c) for c in self.children))
        else:
            return "(%d)" % (self.i)

    def add_child(self, c):
        self.children.append(c)

    def get_constraints(self, S, R, constraints):
        for c in self.children:
            constraints.append(S[c.i] + R[c.i] <= S[self.i])
            # print("%d < %d" % (c.i, self.i))
            c.get_constraints(S, R, constraints)

def conllu_tree(fn):
    sentences = []
    s = []
    i = 0
    with open(fn, 'r') as f:
        for line in f:
            i = i + 1
            if line[0] == '#': # new sentence
                sentences.append(s)
                s = []
            else: # read word line
                sp = line.split('\t')
                try:
                    v = int(sp[0])
                    u = int(sp[6])
                    s.append((v, u))
                except:
                    print('bad line %d "%s"' % (i, line[:-1]))
        sentences.append(s)
    return sentences[1:]

# edge list => Node
def from_edges(E, n=None):
    if not n: # assume tree
        n = len(E) + 1
    nodes = [Node(i, []) for i in range(0, n)]
    for i,j in E:
        nodes[j].add_child(nodes[i])
    return nodes[0]

#print(from_edges(conllu_tree('smpl.conllu')[0]))

# evaluate convex program to choose speeds given machine assignment over jobs [1...n]
# n integer number of jobs
# T a list of root Nodes
# J machine assignment 2D array
def choose_speeds(n, T, J):
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
    for N in T:
        N.get_constraints(S, R, constraints)

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


#n = 3;
#T = Node(2, [Node(1), Node(0)])
#J = [[0,2], [1]]
#print(choose_speeds(n, [T], J))
