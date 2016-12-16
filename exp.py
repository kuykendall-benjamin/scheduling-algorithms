#!/usr/bin/python3

from code import *
import pprint, json, sys

# some example trees

# tree = conllu_tree('smpl.conllu')[0]

# tree = Node(0, [Node(7, [Node(1, [Node(2), Node(3)])]),
#                Node(4, [Node(5), Node(6)])])

pp = pprint.PrettyPrinter(indent=2)

name = "dump.json"
try:
    name = sys.argv[1]
except:
    pass
trees = conllu_tree('en-ud-train.conllu')
with open(name, "w") as f:
    f.write("[\n");
    first = True
    for i, tree in enumerate(trees):
        if i%10 == 0:
            print("iteration %d/%d" % (i, len(trees)))

        if not first:
            f.write(",\n")
        first = False
        s = tree.__str__()
        J, res = schedule_aa(3, tree)
        parsed = parse_schedule(J, res)
        parsed['tree'] = s;
        del parsed['data']
        del parsed['tree']
        f.write(json.dumps(parsed, indent=2, sort_keys=True))
    f.write("\n]");
