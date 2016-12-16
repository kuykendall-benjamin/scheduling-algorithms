#!/usr/bin/python3

from random import choice
from numpy import argmax
from cvxpy import *
from codecs import open as copen
import pprint

# evaluate convex program to choose speeds given machine assignment over jobs [1...n]
# n integer number of jobs
# E edge list of prec constrains
# J machine assignment 2D array
def choose_speeds(n, E, J):
    S = Variable(n)
    R = Variable(n)
    constraints = []

    # non-negativity
    # print("NON-NEGATIVE")
    for i in range(0,n):
        constraints.append(S[i] >= 0)
        # print("S[%d] >= 0" % i)
        constraints.append(R[i] >= 0)
        # print("R[%d] >= 0" % i)

    # makespan
    # print("MAKESPAN")
    for i in range(0,n):
        constraints.append(S[i] + R[i] <= 1)
        # print("S[%d] + R[%d] <= 1" % (i,i))

    # precedence
    # print("PRECEDENCE")
    for i,j in E:
        constraints.append(S[i] + R[i] <= S[j])
        # print("S[%d] + R[%d] <= S[%d]" % (i,i,j))

    # one job at a time
    # print("ONE AT A TIME")
    for A in J:
        for i in range(0, len(A)-1):
            constraints.append(S[A[i]] + R[A[i]] <= S[A[i+1]])
            # print("S[%d] + R[%d] <= S[%d]" % (A[i],A[i],A[i+1]))

    # objective, assuming cubic power
    # obj = Minimize(power(pnorm(R, -2), -2))
    obj = Maximize(pnorm(R, -2))

    # Form and solve problem.
    prob = Problem(obj, constraints)
    try:
        prob.solve(verbose=False,feastol=1e-8)
    except:
        pass

    return (prob.status, prob.value, S.value, R.value)

# res is output of choose_speeds
def tikz(parsed, fn):
    energy, num_mach, data = parsed
    with open(fn, 'w') as f:
        f.write("Energy: %d\n" % energy)
        f.write("\\begin{tikzpicture}\n")
        for i, (m, s, r) in enumerate(data):
            f.write("\draw (%f, %d) rectangle (%f, %d) node[pos=.5] {%d};\n"
                    % (10*s, num_mach-m, 10*(s+r), num_mach-m+1, i))
        f.write("\end{tikzpicture}\n")

# (energy, # mach, [(m, start, time), (m, start, time), (m, start, time), ...])
def parse_schedule(J, res):
    _, E, S, R = res
    E = pow(E, -2)
    nm = sum(len(i) for i in J)
    M = [[0, 0, 0] for i in range(nm)]
    for m, v in enumerate(J):
        for j in v:
            M[j][0] = m

    for i in range(nm):
        M[i][1] = S.item(i, 0)
        M[i][2] = R.item(i, 0)

    M = [(a[0], a[1], a[2]) for a in M]
    return (E, len(J), M)


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

    def pop_rand(self):
        if not self.children:
            return self
        pos = [c.length() for c in self.children]
        inds = [i for i in range(len(pos)) if pos[i] == max(pos)]
        n = self.children[choice(inds)].pop_next()
        if n in self.children:
            n.parent = self
            self.children.remove(n)
        return n

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

def schedule(m, T, rand=False, zz=False):
    n = T.size()
    E = T.get_edges()
    J = [[] for i in range(m)]

    forwards = True

    if rand:
        jobs = [T.pop_rand() for i in range(n)]
    else:
        jobs = [T.pop_next() for i in range(n)]

    while True:
        forwards = forwards != zz
        for j in jobs:
            j.schedulable = True
        for mach in (J if forwards else reversed(J)):
            for j in jobs:
                if j.schedulable:
                    break
            if not j.schedulable:
                break
            jobs.remove(j)
            j.schedule()
            mach.append(j.value())
            # print(j, end="\t")
            if j == T:
                # print()
                return (J, choose_speeds(n,E,J))
        # print()


tree = conllu_tree('smpl.conllu')[0]
print(tree)
J, S = schedule(3, tree)

#J, S = schedule(3, Node(0, [Node(1, [Node(2), Node(3)]),
#                            Node(4, [Node(5), Node(6)])]), zz=True)
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(J)
parsed = parse_schedule(J, S)
pp.pprint(parsed)
tikz(parsed, "out.tikz")

#trees = conllu_tree('en-ud-train.conllu')
#print("total: ", len(trees))
#for i in range(len(trees)):
#    schedule(3,trees[i])
#    print(i)

#n = 3;
#T = Node(2, [Node(1), Node(0)])
#J = [[0,2], [1]]
#print(choose_speeds(n, [T], J))
