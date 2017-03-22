#!/usr/bin/env python
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
from builtins import range
from builtins import map
import os


def read_twostage(fname):
    """Loads two-stage instances."""
    with open(fname) as f:
        lst = list(map(int, f.read().split()))
        W = lst.pop(0)
        H = lst.pop(0)
        m = lst.pop(0)
        w, h, b = [], [], []
        for i in range(m):
            w.append(lst.pop(0))
            h.append(lst.pop(0))
            b.append(lst.pop(0))
        return W, H, w, h, b


def main():
    """Parses 'twostage.mod'."""
    from pympl import PyMPL, Tools, glpkutils
    os.chdir(os.path.dirname(__file__) or os.curdir)

    mod_in = "twostage.mod"
    mod_out = "tmp/twostage.out.mod"
    parser = PyMPL(locals_=locals(), globals_=globals())
    parser.parse(mod_in, mod_out)

    lp_out = "tmp/twostage.lp"
    glpkutils.mod2lp(mod_out, lp_out, True)

    out, varvalues = Tools.script(
        "glpk_wrapper.sh", lp_out, verbose=True
    )

    print("")
    print("varvalues:", [
        (k, v)
        for k, v in sorted(varvalues.items()) if not k.startswith("_")
    ])
    print("")
    assert varvalues["Z"] == 11  # check the solution objective value

    exctacted_solution = parser["VBP_FLOW"].extract(
        lambda name: varvalues.get(name, 0),
        verbose=True
    )

    solution = {}
    for zvar, value, sol in exctacted_solution:
        solution[zvar] = []
        for r, pattern in sol:
            solution[zvar] += [pattern]*r
        assert value == len(solution[zvar])

    def pop_pattern(zvar):
        pattern = []
        for it in solution[zvar].pop():
            if it not in solution:
                pattern.append(it)
            else:
                pattern.append((it, pop_pattern(it)))
        return pattern

    print("\n\nSolution:")
    for i in range(varvalues["Z"]):
        pattern = pop_pattern("Z")
        print("Sheet {}: {}".format(i+1, pattern))


if __name__ == "__main__":
    main()
