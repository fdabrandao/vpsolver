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
import sys
from pyvpsolver.solvers import mvbpsolver

if __name__ == "__main__":
    sdir = os.path.dirname(__file__)
    if sdir != "":
        os.chdir(sdir)


def main():
    """Examples: Multiple-choice Vector Bin Packing"""

    """
    'solvers.mvbp' uses the method proposed in:
    Brandao, F. and Pedroso, J. P. (2013). Multiple-choice Vector Bin Packing:
    Arc-flow Formulation with Graph Compression. Technical Report DCC-2013-13,
    Faculdade de Ciencias da Universidade do Porto, Universidade do Porto, Portugal.
    """

    inf = float("inf")

    # Example 1:
    # Bins:
    W1 = (100, 100)
    W2 = (50, 120)
    W3 = (150, 25)
    Ws = [W1, W2, W3]    # Capacities
    Cs = [3, 7, 2]       # Costs
    Qs = [inf, inf, inf] # Number of available bins
    # Items:
    ws1, b1 = [(50, 25), (25, 50), (0, 75)], 1
    ws2, b2 = [(40, 40), (60, 25), (25, 60)], 1
    ws3, b3 = [(30, 10), (20, 40), (10, 50)], 1
    b = [b1, b2, b3]
    ws = [ws1, ws2, ws3]

    # Solve Example 1:
    obj, sol = mvbpsolver.solve(
        Ws, Cs, Qs, ws, b,
        svg_file="tmp/graphA_mvbp.svg",
        verbose=True, script="vpsolver_glpk.sh"
    )
    print("obj:", obj)
    print("sol:", sol)
    mvbpsolver.print_solution(obj, sol)

    ## Example 2
    # Bins:
    W1 = (100, 75)
    W2 = (75, 50)
    Ws = [W1, W2]
    Cs = [3, 2]
    Qs = [inf, inf]
    # Items
    ws1, b1 = [(75, 50)], 2
    ws2, b2 = [(40, 15), (25, 25)], 1
    b = [b1, b2]
    ws = [ws1, ws2]

    # Solve Example 2:
    obj, sol = mvbpsolver.solve(
        Ws, Cs, Qs, ws, b,
        svg_file="tmp/graphB_mvbp.svg",
        script="vpsolver_glpk.sh",
        verbose=True
    )
    print("obj:", obj)
    print("sol:", sol)
    mvbpsolver.print_solution(obj, sol)

    assert obj == 5  # check the solution objective value


if __name__ == "__main__":
    main()
