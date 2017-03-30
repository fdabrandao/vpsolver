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


def solve(genvbp_instance, svg_file="", lp_file="", mps_file="",
          script=None, script_options=None, stats=None, verbose=None):
    """Solve generalized vector packing problems."""
    assert script is not None
    assert svg_file == "" or svg_file.endswith(".svg")
    if stats is None and verbose is not None:
        stats = verbose

    (Ws, Cs, Ls, Us, U, ws, I, J, dem, prof, req, opt) = genvbp_instance
    b = [
        sum(dem[i, l] for l in req[i]) + sum(dem[i, l] for l in opt[i])
        for i in I
    ]

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
    for i in range(nbtypes):
        var = graph.vname(Ts[i], S, LOSS)
        if Ls[i] != -1:
            lb[var] = Ls[i]
        if Us[i] != -1:
            ub[var] = Us[i]

    delta = {(i, l): "delta_{}_{}".format(i, l) for i in I for l in opt[i]}
    varl += delta.values()

    const_profit = "const_profit"
    varl.append(const_profit)
    lb[const_profit] = ub[const_profit] = sum(
        dem[i, l] * prof[i, l] for l in req[i]
    )

    for i in I:
        lincomb = [(var, 1) for j in J[i] for var in assocs[i, j]]
        cons.append((lincomb, "=", [
                sum(dem[i, l] for l in req[i])  # required demand
            ] + [
                delta[i, l] for l in opt[i]  # optional demand
            ]
        ))
        for l in opt[i]:
            ub[delta[i, l]] = dem[i, l]

    if U != -1:
        cons.append((
            [(graph.vname(Ts[i], S, LOSS), 1) for i in range(nbtypes)],
            "<=", U
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
        (delta[i, l], -prof[i, l]) for i in I for l in opt[i]
    ] + [(const_profit, -1)]
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
    demand = [
        sum(dem[i, l] for l in req[i]) +
        sum(varvalues.get(delta[i, l], 0) for l in opt[i])
        for i in I
    ]
    assert validate_solution(lst_sol, nbtypes, ndims, Ws, ws, demand)

    obj = sum(varvalues.get(var, 0)*coef for var, coef in obj_lincomb)
    return obj, lst_sol
