#!/usr/bin/python3

import json
import sys

def tikz(parsed, fn, scale=10):
    energy, nmach, data = (parsed['energy'], parsed['machines'], parsed['data'])
    with open(fn, 'w') as f:
        f.write("Energy: %d\n" % energy)
        f.write("\\begin{tikzpicture}\n")
        for i, m in enumerate(data):
            f.write("\draw (%f, %d) rectangle (%f, %d) node[pos=.5] {%d};\n"
                    % (scale*m['start'], nmach-m['machine'],
                        scale*(m['start']+m['flow']),
                        nmach-m['machine']+1, i))
        f.write("\end{tikzpicture}\n")
