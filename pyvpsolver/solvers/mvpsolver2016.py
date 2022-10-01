"""
This code is part of the Arc-flow Vector Packing Solver (VPSolver).
"""
from __future__ import print_function

import sys
from .. import VPSolver, MVP, AFG, MPS


def solve(Ws, Cs, Qs, ws, b,
          svg_file="", lp_file="", mps_file="",
          script=None, script_options=None, stats=None, verbose=None):
    """
    Solve multiple-choice vector bin packing instances
    using the method proposed in:
    Brandao, F. (2016). VPSolver 3: Multiple-choice Vector Packing Solver.
    arXiv:1602.04876. http://arxiv.org/abs/1602.04876
    """
    assert script is not None
    assert svg_file == "" or svg_file.endswith(".svg")
    if stats is None and verbose is not None:
        stats = verbose
    instance = MVP(Ws, Cs, Qs, ws, b, verbose=False)
    if (stats == verbose and svg_file == "" and
            lp_file == "" and mps_file == ""):
        out, (obj, sol) = VPSolver.script(script, instance, verbose=verbose)
    else:
        afg = AFG(instance, verbose=stats)
        if svg_file.endswith(".svg"):
            VPSolver.log("Generating .SVG file...", verbose)
            try:
                graph = afg.graph()
                graph.draw(svg_file, verbose=verbose)
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
