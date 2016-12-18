#!/usr/bin/python3

import json
import numpy as np
import matplotlib.pyplot as plt
import sys

def metric(a):
    b = a['energy']/a['machines']/(a['jobs']/a['machines'])**3
    c = a['energy']/(a['height'])**3
    return min(b, c)

if len(sys.argv) < 2:
    print("usage: %s indep-var data1 data2 ..." % sys.argv[0])
    print(" -- plots metric against independent variable in datasets")
    sys.exit(0)

ax = sys.argv[1]
for name in sys.argv[2:]:
    json_data = json.load(open(name, "r"))
    maxd = max([v[ax] for v in json_data])
    data = [[metric(v) for v in json_data if v[ax] == a] for a in range(0, maxd)]
    means = [np.mean(v) for v in data if len(v)]
    stddev = [np.std(v) for v in data if len(v)]
    xdata = [i for i, v in enumerate(data) if len(v)]
    plt.errorbar(xdata, means, yerr=stddev, label=name)

plt.xlabel(ax)
plt.ylabel("ratio")
plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)
plt.show()


