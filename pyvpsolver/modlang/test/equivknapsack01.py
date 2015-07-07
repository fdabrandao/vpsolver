#!/usr/bin/python
"""
This code is part of the Arc-flow Vector Packing Solver (VPSolver).

Copyright (C) 2013-2015, Filipe Brandao
Faculdade de Ciencias, Universidade do Porto
Porto, Portugal. All rights reserved. E-mail: <fdabrandao@dcc.fc.up.pt>.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys
sys.path.insert(0, "../../../")

from pyvpsolver.modlang import AMPLParser, glpk_mod2lp
from pyvpsolver import VPSolver

kp_cons = [
    ([8, 12, 13, 64, 22, 41], 80),
    ([8, 12, 13, 75, 22, 41], 96),
    ([3, 6, 4, 18, 6, 4], 20),
    ([5, 10, 8, 32, 6, 12], 36),
    ([5, 13, 8, 42, 6, 20], 44),
    ([5, 13, 8, 48, 6, 20], 48),
    ([0, 0, 0, 0, 8, 0], 10),
    ([3, 0, 4, 0, 8, 0], 18),
    ([3, 2, 4, 0, 8, 4], 22),
    ([3, 2, 4, 8, 8, 4], 24),
    # ([3, 3, 3, 3, 3, 5, 5, 5], 17),
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
        if aS > a0:
            continue
    a = a+[aS]

    parser = AMPLParser(
        "equivknapsack01.mod", locals_=locals(), globals_=globals()
    )
    parser.write_mod("tmp/equivknapsack01.out.mod")
    glpk_mod2lp(parser.model_file, "tmp/equivknapsack01.lp")
    # os.system("glpsol --math " + parser.model_file + "| grep -v Generating")
    out, varvalues = VPSolver.script_wsol(
        "vpsolver_gurobi.sh", "tmp/equivknapsack01.lp", verbose=False
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
        cons.add((tuple(b), b0))

print "Original knapsack inequalities:"
for a, a0 in sorted(kp_cons, key=lambda x: (x[1], x[0])):
    # print a, a0
    print " + ".join("%2g x%d" % (a[i], i+1) for i in xrange(len(a))), "<=", a0
print "Minimal equivalent knapsack inequalities:"
for b, b0 in sorted(cons, key=lambda x: (x[1], x[0])):
    # print b, b0
    print " + ".join("%2g x%d" % (b[i], i+1) for i in xrange(len(b))), "<=", b0
