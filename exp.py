#!/usr/bin/python3

from code import *
import pprint, json, sys

# some example trees

# tree = conllu_tree('smpl.conllu')[0]

# tree = Node(0, [Node(7, [Node(1, [Node(2), Node(3)])]),
#                Node(4, [Node(5), Node(6)])])

name = "dump.json"
try:
    name = sys.argv[1]
except:
    pass
with open(name, "w") as f:
    f.write("[\n");
    first = True
    for m in range(2, 20):
        trees = conllu_tree('en-ud-train.conllu')
        for i, tree in enumerate(trees):
            if i%10 == 0:
                print("iteration %d/%d with %d mach" % (i, len(trees), m))
            if i > 200:
                break

            if not first:
                f.write(",\n")
            first = False
            height = tree.length()
            s = tree.__str__()
            J, res = schedule(m, tree, rand=True)
            parsed = parse_schedule(J, res)
            # parsed['tree'] = s
            parsed['height'] = height
            del parsed['data']
            f.write(json.dumps(parsed, indent=2, sort_keys=True))
    f.write("\n]");
