#!/usr/bin/python
import sys
sys.path.insert(0, "../../../../")

from pyvpsolver.experimental.modlang import *

kp_cons = [
    ([8,12,13,64,22,41],80),
    ([8,12,13,75,22,41],96),
    ([3,6,4,18,6,4],20),
    ([5,10,8,32,6,12],36),
    ([5,13,8,42,6,20],44),
    ([5,13,8,48,6,20],48),
    ([0,0,0,0,8,0],10),
    ([3,0,4,0,8,0],18),
    ([3,2,4,0,8,4],22),
    ([3,2,4,8,8,4],24),
    #([3,3,3,3,3,5,5,5],17),
]

cons = set()
for k in xrange(len(kp_cons)):
    a, a0 = kp_cons[k]
    aS = abs(2*a0+1-sum(a))
    if a0 < (sum(a)-1)/2:
        a0 += aS
        fix_as = 1
    else:
        fix_as = 0
        if aS > a0: continue
    a = a+[aS]

    ampl = ParseAMPL("equivknapsack01.mod", pyvars = locals())
    ampl.writeMOD("equivknapsack01.out.mod")
    glpk_mod2lp(ampl.model_file(), "equivknapsack01.lp")
    #os.system("glpsol --math " + ampl.model_file() + "| grep -v Generating")
    out, varvalues = VPSolver.script_wsol("vpsolver_gurobi.sh", "equivknapsack01.lp", verbose=False)

    b = [varvalues.get('pi(%d)'%(i+1),0) for i in xrange(len(a))]
    b0 = varvalues.get('pi(0)',0)

    #print a, a0
    #print b, b0

    if fix_as == 1:
        b0 -= b[-1]
        b = b[:-1]
    else:
        b = b[:-1]

    if sum(b) != 0:
        cons.add((tuple(b),b0))

print "Original knapsack inequalities:"
for a, a0 in sorted(kp_cons, key=lambda x: (x[1],x[0])):
    #print a, a0
    print " + ".join("%2g x%d"%(a[i],i) for i in xrange(len(a))), "<=", a0
print "Minimal equivalent knapsack inequalities:"
for b, b0 in sorted(cons, key=lambda x: (x[1],x[0])):
    #print b, b0
    print " + ".join("%2g x%d"%(b[i],i) for i in xrange(len(b))), "<=", b0
