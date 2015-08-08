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
    """Parses 'tsp.mod' and tests cut generators."""
    from gurobipy import GRB, LinExpr, read

    mod_in = "tsp.mod"
    mod_out = "tmp/tsp.out.mod"
    graph_size = "large"
    parser = PyMPL(locals_=locals(), globals_=globals())
    parser.parse(mod_in, mod_out)

    lp_out = "tmp/tsp.lp"
    glpkutils.mod2lp(mod_out, lp_out, True)

    m = read(lp_out)
    m.params.LazyConstraints = 1
    m.params.MIPGap = 0
    m.params.MIPGapAbs = 1-1e-5

    def sep_callback(model, where):
        """Gurobi callback function"""
        if where == GRB.callback.MIPNODE:
            model._cnt += 1
            if model._cnt - model._lastrun < 10:
                return
            model._lastrun = model._cnt

            # check if the submodel was used
            assert "ATSP_MTZ" in parser.submodels()

            # calls the separate method to compute valid inequalities
            cuts = parser["ATSP_MTZ"].separate(
                lambda name: model.cbGetNodeRel(model.getVarByName(name))
            )

            # add the cuts to the model
            if len(cuts) > 0:
                print "add {0} {1}".format(
                    len(cuts), "cuts" if len(cuts) > 1 else "cut"
                )
            for cut in cuts:
                lincomb, sign, rhs = cut
                expr = LinExpr([
                    (coef, model.getVarByName(var))
                    for var, coef in lincomb
                ])
                if sign[0] == ">":
                    model.cbLazy(expr >= rhs)
                elif sign[0] == "<":
                    model.cbLazy(expr <= rhs)
                else:
                    model.cbLazy(expr == rhs)

    m._cnt = 0
    m._lastrun = float("-inf")
    m.optimize(sep_callback)

    print "Objective:", m.ObjVal

if __name__ == "__main__":
    main()
