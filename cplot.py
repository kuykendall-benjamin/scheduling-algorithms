#!/usr/bin/python3

import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
import sys, pprint

pp = pprint.PrettyPrinter(indent=2)

def metric(a):
    b = a['energy']/a['machines']/(a['jobs']/a['machines'])**3
    c = a['energy']/(a['height'])**3
    return min(b, c)

maxy = 0
maxx = 0
a = sys.argv[1]
b = sys.argv[2]
a_data = json.load(open(a, "r"))
b_data = json.load(open(b, "r"))
diff = []

for i in range(len(a_data)):
    diff.append({'i': i, 'd': b_data[i]['energy'] / a_data[i]['energy'], 's' : b_data[i]['jobs']})
    if diff[i]['d'] < 1:
        print("%s better than %s on %d : %d %d" %
        (b, a, i, b_data[i]['energy'], a_data[i]['energy']))

diff.sort(key=lambda x: -x['d'])
pp.pprint(diff)
