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

if __name__ == "__main__":
    if "test_install" in sys.argv:
        sys.argv.remove("test_install")
    else:
        project_dir = "../../"
        sys.path.insert(0, project_dir)
        os.environ["PATH"] = "{0}/scripts:{0}/bin:{1}".format(
            project_dir, os.environ["PATH"]
        )

from pyvpsolver import VPSolver, PyMPL, glpkutils


def read_tsp(fname):
    """Reads TSP instances from files."""
    xs, ys = [], []
    with open(fname) as f:
        lst = map(float, f.read().split())
        n = int(lst.pop(0))
        for i in xrange(n):
            xs.append(lst.pop(0))
            ys.append(lst.pop(0))
    return n, xs, ys


def main():
    """Parses 'tsp.mod'."""

    mod_in = "tsp.mod"
    mod_out = "tmp/tsp.out.mod"
    parser = PyMPL(locals_=locals(), globals_=globals())
    parser.parse(mod_in, mod_out)

    lp_out = "tmp/tsp.lp"
    glpkutils.mod2lp(mod_out, lp_out, True)
    try:
        out, varvalues = VPSolver.script_wsol(
            "vpsolver_gurobi.sh", lp_out, verbose=True
        )
    except Exception as e:
        print repr(e)

    out, varvalues = VPSolver.script_wsol(
        "vpsolver_glpk.sh", lp_out, verbose=True
    )

    print "varvalues:", [
        (k, v)
        for k, v in sorted(varvalues.items())
        if not k.startswith("_")
    ]

if __name__ == "__main__":
    main()
