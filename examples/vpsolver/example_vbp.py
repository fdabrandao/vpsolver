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

from pyvpsolver.solvers import vbpsolver


def main():
    """Example: solve a vector packing instance using 'solvers.vbp'"""

    W = (5180, 2)
    w = [(1120,1), (1250,1), (520,1), (1066,1), (1000,1), (1150,1)]
    b = [9, 5, 91, 18, 11, 64]

    # Solve:
    obj, sol = vbpsolver.solve(
        W, w, b,
        svg_file="tmp/graph_vbp.svg",
        verbose=False, script="vpsolver_glpk.sh"
    )
    print "obj:", obj
    print "sol:", sol
    vbpsolver.print_solution(obj, sol)


if __name__ == "__main__":
    main()
