from unittest import TestCase
import draw

brackets = OrderedDict([
    (4, [1, 2, 3, 4, 5]),
    (3, [6, 7, 8, 9]),
    (2, [10, 11, 12, 13, 14]),
    (1, [15, 16])
])

print brackets
import copy
ppd = PowerPairedDraw(None, pairing_method="fold")
for name in PowerPairedDraw.ODD_BRACKET_FUNCTIONS:
    print name
    b2 = copy.deepcopy(brackets)
    ppd.options["odd_bracket"] = name
    ppd.resolve_odd_brackets(b2)
    print b2
    pairings = ppd.generate_pairings(b2)
    print "\n".join(map(str, pairings))
