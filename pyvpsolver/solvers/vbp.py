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

from .. import *
import sys

def solve(W, w, b, svg_file="", lp_file="", mps_file="",
          verbose=False, script="vpsolver_gurobi.sh"):
    assert svg_file=="" or svg_file.endswith(".svg")
    instance = VBP(W, w, b, verbose=False)
    if svg_file == "" and lp_file == "" and mps_file == "":
        out, (obj, sol) = VPSolver.script(script, instance, verbose=verbose)
    else:
        afg = AFG(instance, verbose=verbose)
        if svg_file.endswith(".svg"):
            if verbose: print "Generating .SVG file..."
            afg.graph().draw(svg_file)
        if lp_file.endswith(".lp"):
            VPSolver.afg2lp(afg.afg_file, lp_file, verbose=False)
            if verbose: print ".LP model successfully generated!"
        if mps_file.endswith(".mps"):
            VPSolver.afg2mps(afg.afg_file, mps_file, verbose=False)
            if verbose: print ".MPS model successfully generated!"
        mps_model = MPS(afg, verbose=verbose)
        out, (obj, sol) = VPSolver.script(script, mps_model, afg, verbose=verbose)
    return obj, sol

def print_solution(obj, sol, f=sys.stdout):
    if obj != None: print >>f, "Objective:", obj
    print >>f, "Solution:"
    for mult, patt in sol:
        print >>f, "%d x [%s]" % (mult, ", ".join(["i=%d" % (it+1) for it in patt]))
