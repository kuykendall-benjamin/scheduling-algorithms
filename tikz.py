#!/usr/bin/python3

import json
import sys

def tikz(parsed, fn, scale=10, m=False):
    energy, nmach, data = (parsed['energy'], parsed['machines'], parsed['data'])
    with open(fn, 'w') as f:
        # f.write("Energy: %d\n" % energy)
        f.write("\\begin{tikzpicture}\n")
        offset = 0
        if m:
            offset = 0.3
            for i in range(nmach):
                f.write("\\node at (0,%f) {M$_%d$};\n" % (i+1.5, i+1));
        for i, m in enumerate(data):
            f.write("\draw (%f, %d) rectangle (%f, %d) node[pos=.5] {%d};\n"
                    % (scale*m['start']+offset, nmach-m['machine'],
                        scale*(m['start']+m['flow'])+offset,
                        nmach-m['machine']+1, i))
        f.write("\end{tikzpicture}\n")
