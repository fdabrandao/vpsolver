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

import os
from glob import glob
from pympl import Tools
from .. import VPSolver
from ..multistage.models import onecut_model
from ..multistage.models import multistage_simple, multistage_groups
from ..multistage.utils import MultiStage, guillotine_cut, cut_items
from ..multistage.utils import raster_points
from ..multistage.draw import draw_solution


def solve(W, H, w, h, b, stage3=False, exact=False, allow_rotation=False,
          restricted=True, simple=False, script=None, script_options=None,
          solution_folder=None, verbose=None):
    """Solve muti-stage cutting stock problems using the arc-flow model."""
    from collections import Counter
    if verbose is None:
        verbose = VPSolver.VERBOSE
    dims = [(W, H)]
    costs = [1]
    itdims = list(zip(w, h))
    itb = b

    prob = MultiStage(dims, costs)

    r0 = raster_points(W, Counter(w))
    r1 = raster_points(H, Counter(h))
    r01 = list(set(r0) | set(r1))
    r0.remove(0)
    r1.remove(0)
    r01.remove(0)

    allow_slack = False
    print("exact:", exact)
    print("rotation:", allow_rotation)
    print("restricted:", restricted)
    print("allow slack:", allow_slack)

    if stage3 is False:
        # 2-stage
        print("2-stage")
        if allow_rotation is False:
            prob.add_stage(
                guillotine_cut, ("S1", 1, list(set(h)))
            )  # 1st
        else:
            prob.add_stage(
                guillotine_cut, ("S1", 1, list(set(h) | set(w)))
            )  # 1st
        prob.add_stage(
            cut_items, (itdims, 0, exact, allow_rotation, allow_slack)
        )

    else:
        # 3-stage
        print("3-stage")
        if allow_rotation is False:
            if restricted:
                prob.add_stage(
                    guillotine_cut, ("S1", 1, list(set(h)))
                )  # 1st
            else:
                prob.add_stage(
                    guillotine_cut, ("S1", 1, r1)
                )  # 1st
            prob.add_stage(
                guillotine_cut, ("S2", 0, list(set(w)))
            )  # 2nd
        else:
            if restricted:
                prob.add_stage(
                    guillotine_cut, ("S1", 1, list(set(w) | set(h)))
                )  # 1st
            else:
                prob.add_stage(
                    guillotine_cut, ("S1", 1, r01)
                )  # 1st
            prob.add_stage(
                guillotine_cut, ("S2", 0, list(set(w) | set(h)))
            )  # 2nd
        prob.add_stage(
            cut_items, (itdims, 1, exact, allow_rotation, allow_slack)
        )

    prob.set_group_demands({"I{}".format(i): bi for i, bi in enumerate(itb)})

    if simple:
        graph, zflow, vnames, model = multistage_simple(prob)
    else:
        graph, zflow, vnames, model = multistage_groups(prob)

    model_file = VPSolver.new_tmp_file(".lp")
    model.write(model_file)
    out, varvalues = Tools.script(
        script, model_file, options=script_options, verbose=verbose
    )
    obj = sum(varvalues.get(var, 0) * coef for (var, coef) in model.obj)

    labels = {}
    for (u, v, lbl) in graph.A:
        if lbl != graph.LOSS:
            labels[u, v, lbl] = [lbl[1]]

    graph.set_flow(varvalues, vnames)
    graph.set_labels(labels)

    solution = {}
    for stage in range(prob.nstages):
        print("Stage: {}".format(stage))
        for curbin in prob.problems_at[stage]:
            f = varvalues.get(vnames[zflow[curbin]], 0)
            if f > 0:
                t = zflow[curbin][0]
                s = t[:t.find(":")]+":S"
                sol = graph.extract_solution(s, "<-", t, flow_limit=f)
                if sol != []:
                    print("\t", curbin, sol)
                    if curbin not in solution:
                        solution[curbin] = []
                    for nrep, patt in sol:
                        for i in range(nrep):
                            solution[curbin].append(list(patt))
        print()

    if solution_folder:
        for f in glob("{}/*.svg".format(solution_folder)):
            os.remove(f)
        draw_solution(
            prob.problems_at[0], solution,
            prob.dimension, prob.group_demand, "{}/sol".format(solution_folder)
        )
    return obj


def onecut(W, H, w, h, b, stage3=False, exact=False, allow_rotation=False,
           restricted=True, script=None, script_options=None, verbose=None):
    """Solve muti-stage cutting stock problems using Elsa's onecut model."""
    if verbose is None:
        verbose = VPSolver.VERBOSE
    assert restricted is True
    model = onecut_model(W, H, w, h, b, stage3, exact, allow_rotation)
    model_file = VPSolver.new_tmp_file(".lp")
    model.write(model_file)
    out, varvalues = Tools.script(
        script, model_file, options=script_options, verbose=verbose
    )
    obj = sum(varvalues.get(var, 0)*coef for var, coef in model.obj)
    return obj
