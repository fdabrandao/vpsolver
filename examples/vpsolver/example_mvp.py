#!/usr/bin/env python
"""
This code is part of the Arc-flow Vector Packing Solver (VPSolver).

Copyright (C) 2013-2016, Filipe Brandao <fdabrandao@gmail.com>
"""
from __future__ import print_function
import os


def main():
    """Examples: Multiple-choice Vector Bin Packing"""
    from pyvpsolver.solvers import mvpsolver

    os.chdir(os.path.dirname(__file__) or os.curdir)

    # Example 1:
    # Bins:
    W1 = (100, 100)
    W2 = (50, 120)
    W3 = (150, 25)
    Ws = [W1, W2, W3]  # Capacities
    Cs = [3, 7, 2]  # Costs
    Qs = [-1, -1, -1]  # Number of available bins
    # Items:
    ws1, b1 = [(50, 25), (25, 50), (0, 75)], 1
    ws2, b2 = [(40, 40), (60, 25), (25, 60)], 1
    ws3, b3 = [(30, 10), (20, 40), (10, 50)], 1
    b = [b1, b2, b3]
    ws = [ws1, ws2, ws3]

    # Solve Example 1:
    solution = mvpsolver.solve(
        Ws,
        Cs,
        Qs,
        ws,
        b,
        svg_file="tmp/graphA_mvbp.svg",
        script="vpsolver_glpk.sh",
        verbose=True,
    )
    mvpsolver.print_solution(solution)

    # check the solution objective value
    obj, patterns = solution
    assert obj == 3

    # Example 2
    # Bins:
    W1 = (100, 75)
    W2 = (75, 50)
    Ws = [W1, W2]
    Cs = [3, 2]
    Qs = [-1, -1]
    # Items
    ws1, b1 = [(75, 50)], 2
    ws2, b2 = [(40, 15), (25, 25)], 1
    b = [b1, b2]
    ws = [ws1, ws2]

    # Solve Example 2:
    solution = mvpsolver.solve(
        Ws,
        Cs,
        Qs,
        ws,
        b,
        svg_file="tmp/graphB_mvbp.svg",
        script="vpsolver_glpk.sh",
        verbose=True,
    )
    mvpsolver.print_solution(solution)

    # check the solution objective value
    obj, patterns = solution
    assert obj == 5


if __name__ == "__main__":
    main()
