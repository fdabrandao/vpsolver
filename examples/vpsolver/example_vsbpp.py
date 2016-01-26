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
from pyvpsolver.solvers import mvpsolver as mvpsolver

if __name__ == "__main__":
    sdir = os.path.dirname(__file__)
    if sdir != "":
        os.chdir(sdir)


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
    obj, sol = mvpsolver.solve(
        Ws, Cs, Qs, ws, b,
        svg_file="tmp/graph_vsbpp.svg",
        script="vpsolver_glpk.sh",
        verbose=True
    )
    print("obj:", obj)
    print("sol:", sol)
    mvpsolver.print_solution(obj, sol)

    assert obj == 1280  # check the solution objective value


if __name__ == "__main__":
    main()
