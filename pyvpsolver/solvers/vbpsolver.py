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

import sys
from .. import VPSolver, VBP, AFG, MPS


def solve(W, w, b,
          svg_file="", lp_file="", mps_file="",
          script=None, script_options=None, stats=None, verbose=None):
    """
    Solve vector packing instances using the method proposed in:
    Brandao, F. and Pedroso, J. P. (2013). Bin Packing and Related
    Problems: General Arc-flow Formulation with Graph Compression. Technical
    Report DCC-2013-08, Faculdade de Ciencias da Universidade do Porto,
    Universidade do Porto, Portugal.
    """
    assert script is not None
    assert svg_file == "" or svg_file.endswith(".svg")
    if stats is None and verbose is not None:
        stats = verbose
    instance = VBP(W, w, b, verbose=False)
    if (stats == verbose and svg_file == "" and
            lp_file == "" and mps_file == ""):
        out, (obj, sol) = VPSolver.script(script, instance, verbose=verbose)
    else:
        afg = AFG(instance, verbose=stats)
        if svg_file.endswith(".svg"):
            VPSolver.log("Generating .SVG file...", verbose)
            try:
                afg.graph().draw(svg_file, verbose=verbose)
            except Exception as e:
                VPSolver.log(e, verbose)
        if lp_file.endswith(".lp"):
            VPSolver.afg2lp(afg.afg_file, lp_file, verbose=False)
            VPSolver.log(".LP model successfully generated!", verbose)
        if mps_file.endswith(".mps"):
            VPSolver.afg2mps(afg.afg_file, mps_file, verbose=False)
            VPSolver.log(".MPS model successfully generated!", verbose)
        mps_model = MPS(afg, verbose=verbose)
        out, (obj, sol) = VPSolver.script(
            script, mps_model, afg, options=script_options, verbose=verbose
        )
    return obj, sol


def print_solution(arg1, arg2=None, i0=1, fout=sys.stdout):
    """Pretty-print a vector packing solution."""
    if arg2 is None:
        obj, lst_sol = arg1
    else:
        obj, lst_sol = arg1, arg2
    assert len(lst_sol) == 1
    sol = lst_sol[0]
    if obj is not None:
        print("Objective:", obj, file=fout)
    print("Solution:", file=fout)
    for mult, patt in sol:
        assert all(opt == 0 for it, opt in patt)
        print("{0} x [{1}]".format(
            mult, ", ".join(
                ["i={0}".format(it+i0) for it, opt in patt]
            )
        ), file=fout)
