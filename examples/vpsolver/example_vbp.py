#!/usr/bin/env python
"""
This code is part of the Arc-flow Vector Packing Solver (VPSolver).

Copyright (C) 2013-2016, Filipe Brandao <fdabrandao@gmail.com>
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
        W, w, b, svg_file="tmp/graph_vbp.svg", script="vpsolver_glpk.sh", verbose=True
    )
    vbpsolver.print_solution(solution)

    # check the solution objective value
    obj, patterns = solution
    assert obj == 33


if __name__ == "__main__":
    main()
