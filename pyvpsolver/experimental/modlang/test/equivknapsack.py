#!/usr/bin/python
import sys
sys.path.insert(0, "../../../../")

from pyvpsolver.experimental.modlang import *

kp_cons = [
    ([3, 5], 17, None)
]

cons = set()
for k in xrange(len(kp_cons)):
    a, a0, bounds = kp_cons[k]
    if bounds is None:
        bounds = [a0]*len(a)
    for i in xrange(len(a)):
        bounds[i] = a0/a[i] if a[i] != 0 else 0
    sum_a = sum(x*y for x, y in zip(a, bounds))
    aS = abs(2*a0+1-sum_a)
    if a0 < (sum_a-1)/2:
        a0 += aS
        fix_as = 1
    else:
        if aS > a0:
            continue
        fix_as = 0
    a = a+[aS]
    bounds = bounds+[1]

    ampl = ParseAMPL("equivknapsack.mod", pyvars=locals())
    ampl.writeMOD("equivknapsack.out.mod")
    glpk_mod2lp(ampl.model_file(), "equivknapsack.lp")
    # os.system("glpsol --math " + ampl.model_file() + "| grep -v Generating")
    out, varvalues = VPSolver.script_wsol(
        "vpsolver_gurobi.sh", "equivknapsack.lp", verbose=False
    )

    b = [varvalues.get("pi(%d)" % (i+1), 0) for i in xrange(len(a))]
    b0 = varvalues.get("pi(0)", 0)

    # print a, a0
    # print b, b0

    if fix_as == 1:
        b0 -= b[-1]
        b = b[:-1]
    else:
        b = b[:-1]

    if sum(b) != 0:
        cons.add((tuple(b), b0, tuple(bounds)))

print "Original knapsack inequalities:"
for a, a0, bounds in sorted(kp_cons, key=lambda x: (x[1], x[0])):
    # print a, a0
    print " + ".join("%2g x%d" % (a[i], i) for i in xrange(len(a))), "<=", a0
print "Minimal equivalent knapsack inequalities:"
for b, b0, bounds in sorted(cons, key=lambda x: (x[1], x[0])):
    # print b, b0
    print " + ".join("%2g x%d" % (b[i], i) for i in xrange(len(b))), "<=", b0,
    print bounds[:-1]
