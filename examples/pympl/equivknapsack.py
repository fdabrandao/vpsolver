#!/usr/bin/env python
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

import os
import sys
sdir = os.path.dirname(__file__)
if sdir != "":
    os.chdir(sdir)

INSTALLED = False
if not INSTALLED:
    project_dir = "../../"
    sys.path.insert(0, project_dir)
    os.environ["PATH"] = "{0}/scripts:{0}/bin:{1}".format(
        project_dir, os.environ["PATH"]
    )

from pyvpsolver.pympl import PyMPL, glpk_mod2lp
from pyvpsolver import VPSolver


def main():
    """
    Computes minimal equivalent knapsack inequalities using 'equivknapsack.mod'
    """

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

        mod_in = "equivknapsack.mod"
        mod_out = "tmp/equivknapsack.out.mod"
        parser = PyMPL(locals_=locals())
        parser.parse(mod_in, mod_out)

        lp_out = "tmp/equivknapsack.lp"
        glpk_mod2lp(mod_out, lp_out)
        # os.system("glpsol --math {0} | grep -v Generating".format(mod_out))
        out, varvalues = VPSolver.script_wsol(
            "vpsolver_glpk.sh", lp_out, verbose=True
        )

        b = [varvalues.get("pi({0})".format(i+1), 0) for i in xrange(len(a))]
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
        print " + ".join(
            "{0:2g} x{1:d}".format(a[i], i+1) for i in xrange(len(a))
        ), "<=", a0
    print "Minimal equivalent knapsack inequalities:"
    for b, b0, bounds in sorted(cons, key=lambda x: (x[1], x[0])):
        # print b, b0
        print " + ".join(
            "{0:2g} x{1:d}".format(b[i], i+1) for i in xrange(len(b))
        ), "<=", b0, bounds[:-1]


if __name__ == "__main__":
    main()
