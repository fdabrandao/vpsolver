#!/usr/bin/env python
"""
This code is part of the Arc-flow Vector Packing Solver (VPSolver).

Copyright (C) 2013-2016, Filipe Brandao
Faculdade de Ciencias, Universidade do Porto
Porto, Portugal. All rights reserved. E-mail: <fdabrandao@dcc.fc.up.pt>.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from __future__ import print_function
import os


def main():
    """Example: solve a vector packing instance using 'solvers.vbpsolver'"""
    from pyvpsolver.solvers import vbpsolver
    os.chdir(os.path.dirname(__file__) or os.curdir)

    W = (5180, 9)
    w = [(1120, 1), (1250, 1), (520, 1), (1066, 1), (1000, 1), (1150, 1)]
    b = [9, 5, 91, 18, 11, 64]

    # Solve:
    solution = vbpsolver.solve(
        W, w, b,
        svg_file="tmp/graph_vbp.svg",
        script="vpsolver_glpk.sh",
        verbose=True
    )
    vbpsolver.print_solution(solution)

    # check the solution objective value
    obj, patterns = solution
    assert obj == 33


if __name__ == "__main__":
    main()
