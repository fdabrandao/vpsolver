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
import sys
from .. import VPSolver, MVP, AFG
from .mvputils import validate_solution, print_solution
from pympl import Model


def solve(bins, items, maxbins=-1, svg_file="", lp_file="", mps_file="",
          script=None, script_options=None, stats=None, verbose=None):
    """Solve generalized vector packing problems."""
    assert script is not None
    assert svg_file == "" or svg_file.endswith(".svg")
    if stats is None and verbose is not None:
        stats = verbose

    Ws = [_capacity for _capacity, _cost, _l, _u in bins]
    Cs = [_cost for _capacity, _cost, _l, _u in bins]
    Ls = [_l for _capacity, _cost, _l, _u in bins]
    Us = [_u for _capacity, _cost, _l, _u in bins]
    ws = [_volumes for _volumes, _profit, _d, _dopt in items]
    profit = [_profit for _volumes, _profit, _d, _dopt in items]
    b = [_d + _dopt for _volumes, _profit, _d, _dopt in items]
    d = [_d for _volumes, _profit, _d, _dopt in items]
    dopt = [_dopt for _volumes, _profit, _d, _dopt in items]
    nbtypes, ndims = len(Ws), len(Ws[0])

    instance = MVP(Ws, Cs, Us, ws, b, verbose=False)
    afg = AFG(instance, verbose=stats)
    if svg_file.endswith(".svg"):
        VPSolver.log("Generating .SVG file...", verbose)
        try:
            graph = afg.graph()
            graph.draw(svg_file, verbose=verbose)
        except Exception as e:
            VPSolver.log(e, verbose)

    # Build the model:
    graph = afg.graph()
    LOSS = graph.LOSS
    S, Ts = graph.S, graph.Ts
    V, A = graph.V, graph.A
    varl, cons = graph.get_flow_cons()
    assocs = graph.get_assocs()

    lb, ub = {}, {}
    for lbl in assocs:
        if lbl != LOSS:
            for var in assocs[lbl]:
                ub[var] = b[lbl[0]]

    for i in range(nbtypes):
        var = graph.vname(Ts[i], S, LOSS)
        if Ls[i] != -1:
            lb[var] = Ls[i]
        if Us[i] != -1:
            ub[var] = Us[i]

    extra = ["extra{}".format(i) for i in range(len(b))]
    varl += extra

    for i in range(len(b)):
        lincomb = [(var, 1) for var in assocs[i, 0]]
        cons.append((lincomb, "=", [d[i], extra[i]]))
        ub[extra[i]] = dopt[i]  # optional demand

    if maxbins != -1:
        cons.append((
            [(graph.vname(Ts[i], S, LOSS), 1) for i in range(nbtypes)],
            "<=", maxbins
        ))

    # Generate the model
    model = Model()
    for var in varl:
        model.add_var(name=var, lb=0, ub=ub.get(var, None), vtype="I")
    for lincomb, sign, rhs in cons:
        model.add_con(lincomb, sign, rhs)

    # Define the objective
    obj_lincomb = [
        (graph.vname(Ts[i], S, LOSS), Cs[i]) for i in range(nbtypes)
    ] + [
        (extra[i], -profit[i]) for i in range(len(b))
    ]
    model.set_obj("min", obj_lincomb)

    # Generate .lp/.mps models if requested
    if lp_file.endswith(".lp"):
        model.write(lp_file)
        VPSolver.log(".LP model successfully generated!", verbose)
    if mps_file.endswith(".mps"):
        model.write(mps_file)
        VPSolver.log(".MPS model successfully generated!", verbose)

    # Solve the model
    model_file = VPSolver.new_tmp_file(".lp")
    model.write(model_file)
    out, varvalues = VPSolver.script_wsol(
        script, model_file, options=script_options, verbose=verbose
    )
    os.remove(model_file)

    # Extract the solution
    lst_sol = []
    graph.set_flow(varvalues)
    graph.set_labels({(u, v, i): [i] for (u, v, i) in A if i != LOSS})
    for i in range(nbtypes):
        lst_sol.append(graph.extract_solution(S, "<-", Ts[i]))

    # Validate the solution
    assert validate_solution(lst_sol, nbtypes, ndims, Ws, ws, d)
    c1 = sum(sum(r for r, patt in lst_sol[i])*Cs[i] for i in range(nbtypes))
    c2 = sum(
        varvalues.get(graph.vname(Ts[i], S, LOSS), 0) * Cs[i]
        for i in range(nbtypes)
    )
    assert c1 == c2

    obj = sum(varvalues.get(var, 0)*coef for var, coef in obj_lincomb)
    return obj, lst_sol
