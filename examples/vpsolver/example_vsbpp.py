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

from pyvpsolver.solvers import mvbpsolver


def main():
    """ Variable-sized Bin Packing Example """

    """
    'solvers.mvbp' the method proposed in:
    Brandao, F. and Pedroso, J. P. (2013). Multiple-choice Vector Bin Packing:
    Arc-flow Formulation with Graph Compression. Technical Report DCC-2013-13,
    Faculdade de Ciencias da Universidade do Porto, Universidade do Porto, Portugal.
    """

    inf = float("inf")

    # Capacities:
    Ws = [[100], [120], [150]]

    # Cots:
    Cs = [100, 120, 150]

    # Number of bins available of each type:
    Qs = [inf, inf, inf]

    # Item weights:
    ws = [[[10]], [[14]], [[17]], [[19]], [[24]], [[29]], [[32]], [[33]], [[36]],
          [[38]], [[40]], [[50]], [[54]], [[55]], [[63]], [[66]], [[71]], [[77]],
          [[79]], [[83]], [[92]], [[95]], [[99]]]

    # Item demands:
    b = [1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1]

    # Solve the variable-sized bin packing instance:
    obj, sol = mvbpsolver.solve(
        Ws, Cs, Qs, ws, b,
        svg_file="tmp/graph_vsbpp.svg",
        verbose=True, script="vpsolver_glpk.sh")
    print "obj:", obj
    print "sol:", sol
    mvbpsolver.print_solution(obj, sol)


if __name__ == "__main__":
    main()
