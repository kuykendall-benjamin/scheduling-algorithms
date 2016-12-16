#!/usr/bin/python3

import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
import sys

def metric(a):
    b = a['energy']/a['machines']/(a['jobs']/a['machines'])**3
    c = a['energy']/(a['height'])**3
    return min(b, c)

maxy = 0
maxx = 0
for name in sys.argv[1:]:
    json_data = json.load(open(name, "r"))
    json_data.sort(key=metric)
    data = [metric(a) for a in json_data] # if a["jobs"] > 3]

    data2 = [a['jobs'] for a in json_data] # if a["jobs"] > 3]
    plt.plot(data2, data, 'o', label=name)

    """density = gaussian_kde(data)
    xs = np.linspace(0, max(data)*1.1, 200)
    density.covariance_factor = lambda: 0.01
    density._compute_covariance()
    plt.plot(xs, density(xs), label=name)"""
    if max(data2) > maxx:
        maxx = max(data2)
    if max(data) > maxy:
        maxy = max(data)

plt.axis([0, maxx, 0, maxy])
plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)
plt.show()


