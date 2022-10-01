#!/usr/bin/env python
from __future__ import print_function
import os


def main():
    """Variable-sized Bin Packing Example"""
    from pyvpsolver.solvers import mvpsolver

    os.chdir(os.path.dirname(__file__) or os.curdir)

    # Capacities:
    Ws = [[100], [120], [150]]

    # Cots:
    Cs = [100, 120, 150]

    # Number of bins available of each type:
    Qs = [-1, -1, -1]

    # Item weights:
    ws = [
        [[10]],
        [[14]],
        [[17]],
        [[19]],
        [[24]],
        [[29]],
        [[32]],
        [[33]],
        [[36]],
        [[38]],
        [[40]],
        [[50]],
        [[54]],
        [[55]],
        [[63]],
        [[66]],
        [[71]],
        [[77]],
        [[79]],
        [[83]],
        [[92]],
        [[95]],
        [[99]],
    ]

    # Item demands:
    b = [1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1]

    # Solve the variable-sized bin packing instance:
    solution = mvpsolver.solve(
        Ws,
        Cs,
        Qs,
        ws,
        b,
        svg_file="tmp/graph_vsbpp.svg",
        script="vpsolver_glpk.sh",
        verbose=True,
    )
    mvpsolver.print_solution(solution)

    # check the solution objective value
    obj, patterns = solution
    assert obj == 1280


if __name__ == "__main__":
    main()
