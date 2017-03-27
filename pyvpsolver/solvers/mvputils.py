"""
This code is part of the Arc-flow Vector Packing Solver (VPSolver).

Copyright (C) 2013-2017, Filipe Brandao
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
from __future__ import division
from builtins import str, map, object, range, zip, sorted
import sys


def validate_solution(lst_solutions, nbtypes, ndims, Ws, ws, b):
    """Validate multiple-choice vector packing solutions."""
    if any(
        sum(ws[it][t][d] for (it, t) in pat) > Ws[i][d]
        for i in range(nbtypes)
        for d in range(ndims)
        for r, pat in lst_solutions[i]
    ):
        return False

    aggsol = sum([sol for sol in lst_solutions], [])

    c = [0] * len(b)
    for (r, p) in aggsol:
        for i, t in p:
            c[i] += r

    return all(c[i] >= b[i] for i in range(len(b)))


def print_solution(solution, arg2=None, i0=1, fout=sys.stdout):
    """Pretty-print a multiple-choice vector packing solution."""
    if arg2 is None:
        obj, lst_sol = solution
    else:
        obj, lst_sol = solution, arg2
    if obj is not None:
        print("Objective:", obj, file=fout)
    print("Solution:", file=fout)
    for i, sol in enumerate(lst_sol):
        cnt = sum(m for m, p in sol)
        print("Bins of type {0}: {1} {2}".format(
            i+i0, cnt, ["bins", "bin"][cnt == 1]
        ), file=fout)
        for mult, patt in sol:
            print("{0} x [{1}]".format(
                mult, ", ".join(
                    ["i={0} opt={1}".format(it+i0, opt+i0) for it, opt in patt]
                )
            ), file=fout)
