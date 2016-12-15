#!/usr/bin/python3

from numpy import argmax
from cvxpy import *
from codecs import open as copen

# evaluate convex program to choose speeds given machine assignment over jobs [1...n]
# n integer number of jobs
# E edge list of prec constrains
# J machine assignment 2D array
def choose_speeds(n, E, J):
    S = Variable(n)
    R = Variable(n)
    constraints = []

    # non-negativity
    print("NON-NEGATIVE")
    for i in range(0,n):
        constraints.append(S[i] >= 0)
        print("S[%d] >= 0" % i)
        constraints.append(R[i] >= 0)
        print("R[%d] >= 0" % i)

    # makespan
    print("MAKESPAN")
    for i in range(0,n):
        constraints.append(S[i] + R[i] <= 1)
        print("S[%d] + R[%d] <= 1" % (i,i))

    # precedence
    print("PRECEDENCE")
    for i,j in E:
        constraints.append(S[i] + R[i] <= S[j])
        print("S[%d] + R[%d] <= S[%d]" % (i,i,j))

    # one job at a time
    print("ONE AT A TIME")
    for A in J:
        for i in range(0, len(A)-1):
            constraints.append(S[A[i]] + R[A[i]] <= S[A[i+1]])
            print("S[%d] + R[%d] <= S[%d]" % (A[i],A[i],A[i+1]))

    # objective, assuming cubic power
    #obj = Minimize(power(pnorm(R, -2), -2))
    obj = Maximize(pnorm(R, -2))

    # Form and solve problem.
    prob = Problem(obj, constraints)
    prob.solve(verbose=True,feastol=1e-8)
    #prob.solve(verbose=False,feastol=1e-08,solver=CVXOPT)

    return (prob.status, prob.value, S.value, R.value)

# tree
class Node:
    def __init__(self, i, children=[]):
        self.i = i
        self.children = children
        self.schedulable = True
        self.parent = None

    def __str__(self):
        if self.children:
            return "(%d %s)" % (self.i, " ".join(str(c) for c in self.children))
        else:
            return "(%d)" % (self.i)

    def __repr__(self):
        return self.__str__()

    def value(self):
        return self.i

    def add_child(self, c):
        self.children.append(c)

    def get_edges(self):
        E = []
        for c in self.children:
            E.append((c.i, self.i))
            E = E + c.get_edges()
        return E

    def size(self):
        if not self.children:
            return 1
        else:
            return 1 + sum(c.size() for c in self.children)

    def schedule(self):
        self.schedulable = False
        if self.parent:
            self.parent.schedule()

    def flatten(self):
        res = [self]
        for c in self.children:
            res = res + c.flatten()
        return res

    def length(self):
        if not self.children:
            return 1
        else:
            return 1 + max(c.length() for c in self.children)

    def pop_next(self): # cyclically
        if not self.children:
            return self
        pos = [c.length() for c in self.children]
        n = self.children[argmax(pos)].pop_next()
        if n in self.children:
            n.parent = self
            self.children.remove(n)
        return n

    def pop_next_random(self): # w/o hueristic
        return

# edge list => Node
def from_edges(E, n=None):
    if not n: # assume tree
        n = len(E) + 1
    nodes = [Node(i, []) for i in range(0, n)]
    for i,j in E:
        nodes[j].add_child(nodes[i])
    return nodes[0]

def conllu_tree(fn):
    sentences = []
    s = []
    i = 0
    with copen(fn, "r", "utf-8") as f:
        for line in f:
            i = i + 1
            if len(line) != 1 and line[0] != '#':
                sp = line.split('\t')
                try:
                    v = int(sp[0])
                    u = int(sp[6])
                    if (v == 1):
                        s = []
                        sentences.append(s)
                    s.append((v, u))
                except:
                    print('bad line %d "%s"' % (i, line[:-1]))
    return [from_edges(s) for s in sentences]

# hueristic schedule
def schedule(m, T):
    n = T.size()
    E = T.get_edges()
    J = [[] for i in range(m)]

    jobs = [T.pop_next() for i in range(n)]

    while True:
        for j in jobs:
            j.schedulable = True
        for mach in J:
            for j in jobs:
                if j.schedulable:
                    break
            if not j.schedulable:
                break
            jobs.remove(j)
            j.schedule()
            mach.append(j.value())
            print(j, end="\t")
            if j == T:
                print()
                return choose_speeds(n,E,J)
        print()


tree = conllu_tree('smpl.conllu')[0]
print(tree)
print(schedule(3, tree))

#print(schedule(2, Node(2, [Node(1, [Node(3), Node(4)]), Node(0)])))
#print(schedule(2, Node(0, [Node(1, [Node(2), Node(3), Node(4)]), Node(5)])))

#trees = conllu_tree('en-ud-train.conllu')

#n = 3;
#T = Node(2, [Node(1), Node(0)])
#J = [[0,2], [1]]
#print(choose_speeds(n, [T], J))
