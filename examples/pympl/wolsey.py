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

if __name__ == "__main__":
    if "test_install" in sys.argv:
        sys.argv.remove("test_install")
    else:
        project_dir = "../../"
        sys.path.insert(0, project_dir)
        os.environ["PATH"] = "{0}/scripts:{0}/bin:{1}".format(
            project_dir, os.environ["PATH"]
        )

from pyvpsolver import VPSolver, PyMPL, glpkutils


def main():
    """Parses 'graph.mod'"""

    a, a0 = [65, 64, 41, 22, 13, 12, 8, 2], 80
    aS = abs(2*a0+1-sum(a))
    if a0 < (sum(a)-1)/2:
        a0 += aS
    a.append(aS)

    print 'self-dual:', a, a0

    m = len(a)
    W = [a0]+[1]*len(a)
    w = [[a[i]]+[1 if j == i else 0 for j in xrange(m)] for i in xrange(m)]
    labels = [i+1 for i in xrange(m)]
    bounds = [1 if w[i] <= W else 0 for i in xrange(m)]

    # wolseyR2network:

    print "-"*10
    print "Primal:"

    mod_in = "wolseyR2network.mod"
    mod_out = "tmp/wolseyR2network.out.mod"
    parser = PyMPL(locals_=locals(), globals_=globals())
    parser.parse(mod_in, mod_out)
    lp_out = "tmp/wolseyR2network.lp"
    glpkutils.mod2lp(mod_out, lp_out, verbose=False)
    out, varvalues = VPSolver.script_wsol(
        "vpsolver_glpk.sh", lp_out, verbose=False
    )
    print
    print "varvalues:", [(k, v) for k, v in sorted(varvalues.items())]
    print

    # Check the solution objective value:
    assert abs(varvalues["Z0"] - 9) < 1e-5

    exit_code = os.system("glpsol --math {0}".format(mod_out))
    assert exit_code == 0

    # wolseyR1gamma:

    print "-"*10
    print "wolseyR1gamma:"

    mod_in = "wolseyR1gamma.mod"
    mod_out = "tmp/wolseyR1gamma.mod.out.mod"
    parser = PyMPL(locals_=locals(), globals_=globals())
    parser.parse(mod_in, mod_out)
    lp_out = "tmp/wolseyR1gamma.mod.lp"
    glpkutils.mod2lp(mod_out, lp_out, verbose=False)
    out, varvalues = VPSolver.script_wsol(
        "vpsolver_glpk.sh", lp_out, verbose=False
    )
    print
    print "varvalues:", [(k, v) for k, v in sorted(varvalues.items())]
    print

    # Check the solution objective value:
    assert abs(varvalues['theta(T)'] - 9) < 1e-5

    exit_code = os.system("glpsol --math {0}".format(mod_out))
    assert exit_code == 0

if __name__ == "__main__":
    main()
