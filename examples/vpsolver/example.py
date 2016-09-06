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
    """Example: how to use VBP, MVP, AFG, MPS, LP and VPSolver."""
    from pyvpsolver import VPSolver, VBP, MVP, AFG, MPS, LP
    from pyvpsolver.solvers import vbpsolver, mvpsolver
    os.chdir(os.path.dirname(__file__) or os.curdir)

    # Create instanceA:
    instanceA = VBP(
        (5180,),
        [(1120,), (1250,), (520,), (1066,), (1000,), (1150,)],
        [9, 5, 91, 18, 11, 64]
    )

    # Create instanceB from a .vbp file
    instanceB = VBP.from_file("instance.vbp")

    # Create an arc-flow graph for instanceA
    afg = AFG(instanceA, verbose=False)

    # Create .mps and .lp models for instanceA
    mps_model = MPS(afg, verbose=False)
    lp_model = LP(afg, verbose=False)

    # Draw the arc-flow graph for instanceA (requires pygraphviz)
    try:
        afg.draw("tmp/graph1.svg")
    except ImportError as e:
        print(repr(e))

    # Solve instanceA using bin/vpsolver (requires Gurobi)
    try:
        out, sol = VPSolver.vpsolver(instanceA, verbose=True)
    except Exception as e:
        print("Failed to call vpsolver")
        print(repr(e))

    # Solve instanceA using any vpsolver script (i.e., any MIP solver):
    #   The scripts accept models with and without the underlying graphs.
    #   However, the graphs are required to extract the solution.
    out, sol = VPSolver.script("vpsolver_glpk.sh", lp_model, afg, verbose=True)
    try:
        out, sol = VPSolver.script(
            "vpsolver_gurobi.sh", mps_model, verbose=True
        )
    except Exception as e:
        print(repr(e))

    # Solve an instance directly without creating AFG, MPS or LP objects:
    out, solution = VPSolver.script(
        "vpsolver_glpk.sh", instanceB, verbose=True
    )

    # Print the solution:
    obj, patterns = solution
    print("Objective:", obj)
    print("Solution:", patterns)

    # Pretty-print the solution:
    vbpsolver.print_solution(solution)

    # check the solution objective value
    obj, patterns = solution
    assert obj == 21

    # Create instanceC:
    W1 = (100, 100)
    W2 = (50, 120)
    W3 = (150, 25)
    ws1, b1 = [(50, 25), (25, 50), (0, 75)], 1
    ws2, b2 = [(40, 40), (60, 25), (25, 60)], 1
    ws3, b3 = [(30, 10), (20, 40), (10, 50)], 1
    Ws = [W1, W2, W3]     # capacities
    Cs = [3, 7, 2]        # costs
    Qs = [-1, -1, -1]     # number of bins available
    ws = [ws1, ws2, ws3]  # items
    b = [b1, b2, b3]      # demands
    instanceC = MVP(Ws, Cs, Qs, ws, b)

    # Solve an instance directly without creating AFG, MPS or LP objects:
    out, solution = VPSolver.script(
        "vpsolver_glpk.sh", instanceC, verbose=True
    )
    mvpsolver.print_solution(solution)

    # check the solution objective value
    obj, patterns = solution
    assert obj == 3

    # Create instanceD from a .mvp file
    instanceD = MVP.from_file("instance.mvp")

    # Draw the arc-flow graph for instanceD (requires pygraphviz)
    try:
        AFG(instanceD).draw("tmp/graph2.svg")
    except ImportError as e:
        print(repr(e))

    # Solve an instance directly without creating AFG, MPS or LP objects:
    out, solution = VPSolver.script(
        "vpsolver_glpk.sh", instanceD, verbose=True
    )
    mvpsolver.print_solution(solution)

    # check the solution objective value
    obj, patterns = solution
    assert obj == 8


if __name__ == "__main__":
    main()
