#!/usr/bin/python3

from random import choice, shuffle
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

    return (prob.status, pow(prob.value, -2), S.value, R.value)

# (energy, # mach, [(m, start, time), (m, start, time), (m, start, time), ...])
def parse_schedule(J, res):
    _, E, S, R = res
    nj = sum(len(i) for i in J)
    M = [{} for i in range(nj)]
    for m, v in enumerate(J):
        for j in v:
            M[j]['machine'] = m
            M[j]['job'] = j

    for i in range(nj):
        try:
            M[i]['start'] = S.item(i, 0)
            M[i]['flow'] = R.item(i, 0)
        except:
            M[i]['start'] = S[i]
            M[i]['flow'] = R[i]

    return {'energy':round(E, 3), 'machines':len(J), 'jobs': nj, 'data':M}


# tree
class Node:
    def __init__(self, i, *children):
        self.i = i
        self.children = list(children) if len(children) > 0 else []
        self.schedulable = True
        self.parent = None
        self.chain_height = None

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

    def assign_chain_height(self):
        for c in self.children:
            c.assign_chain_height()
        if not self.children:
            self.chain_height = 1
        elif len(self.children) == 1:
            self.chain_height = self.children[0].chain_height + 1
        else:
            self.chain_height = max(c.chain_height for c in self.children) + 1

    def chains(self, prec=[]):
        if not self.children:
            return [(prec + [self], self.chain_height)]
        if len(self.children) == 1:
            return self.children[0].chains(prec + [self])
        else:
            res = [(prec + [self], self.chain_height)]
            for c in self.children:
                res = res + c.chains()
            return res

    def chain_decompose(self):
        self.assign_chain_height()
        res = [[] for i in range(self.chain_height)]
        for chain, height in self.chains():
            res[height-1].append([c.i for c in chain])
        return [r for r in res if r]


# edge list => Node
def from_edges(E, n=None):
    if not n: # assume tree
        n = len(E) + 1
    nodes = [Node(i) for i in range(n)]
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

def schedule(m, T, rand=False, zz=False, optimize=True):
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
                if optimize: # todo: break into two methods
                    return (J, choose_speeds(n,E,J))
                else:
                    return (J, None)
        if rand:
            shuffle(J)
        # print()

def schedule_aa(m, T):
    n = T.size()
    blocks = T.chain_decompose()
    # print(blocks)

    JS = []
    ID = []

    # assign each block using existing alg
    for b in range(len(blocks)):
        i = 1
        ids = {}
        J = []

        # to tree
        root = Node(0)
        for l in blocks[b]:
            prev = []
            for j in reversed(l):
                prev = [Node(i, *prev)]
                ids[i] = j
                i = i + 1
            root.add_child(prev[0])

        # assign to machines
        J, _ = schedule(m, root, optimize=False)

        # remove root (always last so does not change assignment)
        for mach in J:
            if mach and mach[-1] == 0:
                mach.pop(-1)

        JS.append(J)
        ID.append(ids)

    # scale each block to constant width
    total = sum(len(J[0]) for J in JS)
    off = 0
    S = [0]*n
    R = [0]*n
    J_ALL = [[] for _ in range(m)]
    for b in range(len(blocks)):
        J = JS[b]
        I = ID[b]
        c = len(J[0]) / total
        # print(c)
        for i in range(len(J)):
            if not J[i]:
                continue
            inc = c / len(J[i])
            # print("  ", len(J[i]), " * ", inc)
            for j in range(len(J[i])):
                S[I[J[i][j]]] = off + inc*j
                R[I[J[i][j]]] = inc
                J_ALL[i].append(I[J[i][j]])
        off += c

    E = sum(pow(r,-2) for r in R)
    return (J_ALL, ("ok", E, S, R))


