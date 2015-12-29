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
from __future__ import print_function
from __future__ import division
from builtins import zip
from builtins import range

import os
import sys
from .. import VPSolver, VBP, AFG
from .. import AFGraph
from pympl import Model

LOSS = "L"


def solve(
        Ws, Cs, Qs, ws, b, svg_file="", lp_file="", mps_file="",
        script="vpsolver_glpk.sh", verbose=False):
    """
    Solves multiple-choice vector bin packing instances
    using the method proposed in:
    Brandao, F. and Pedroso, J. P. (2013). Multiple-choice Vector
    Bin Packing: Arc-flow Formulation with Graph Compression. Technical Report
    DCC-2013-13, Faculdade de Ciencias da Universidade do Porto, Universidade
    do Porto, Portugal.
    """
    assert svg_file == "" or svg_file.endswith(".svg")
    nbtypes = len(Ws)
    ndims = len(Ws[0])

    ww = []
    bb = []
    itlabel = []
    for i in range(len(ws)):
        for j in range(len(ws[i])):
            itlabel.append((i, j))
            ww.append(ws[i][j])
            bb.append(b[i])

    instances = [None] * nbtypes
    graphs = [None] * nbtypes
    Ss, Ts = [None] * nbtypes, [None] * nbtypes
    for i in range(nbtypes):
        bbi = bb[:]
        for j in range(len(ww)):
            if any(a > b for a, b in zip(ww[j], Ws[i])):
                bbi[j] = 0
                continue
        symb = "G{0}".format(i)
        instances[i] = VBP(Ws[i], ww, bbi, verbose=False)
        graphs[i] = AFG(instances[i], verbose=verbose).graph()
        graphs[i].relabel(
            lambda u: "{0}{1}".format(symb, u),
            lambda lbl: lbl if lbl < len(ww) else LOSS
        )
        Ss[i] = symb+"S"
        Ts[i] = symb+"T"
        if svg_file.endswith(".svg"):
            try:
                graphs[i].draw(svg_file.replace(".svg", "{0}.svg".format(i)))
            except Exception as e:
                VPSolver.log(e, verbose)

    S, T = "S", "T"
    V = sum([g.V for g in graphs], [])
    A = sum([g.A for g in graphs], [])
    V += [S, T]
    A += [(S, s, LOSS) for s in Ss]
    A += [(t, T, LOSS) for t in Ts]
    A += [(T, S, LOSS)]

    graph = AFGraph(V, A, S, T)
    if svg_file.endswith(".svg"):
        try:
            graph.draw(svg_file, ignore=[(T, S)])
        except Exception as e:
                VPSolver.log(e, verbose)

    adj = {u: [] for u in V}
    for (u, v, i) in A:
        adj[v].append((u, i))

    VPSolver.log("Final compression steps:", verbose)

    nv1, na1 = len(V), len(A)
    VPSolver.log("  #V1: {0} #A1: {1}".format(nv1, na1), verbose)
    zero = tuple([0]*ndims)

    def compress(u):
        if u == S:
            return zero
        if u in newlbl:
            return newlbl[u]
        lbl = zero
        for v, i in adj[u]:
            wi = ww[i] if i != LOSS else zero
            vlbl = compress(v)
            lbl = tuple(max(lbl[d], vlbl[d]+wi[d]) for d in range(ndims))
        newlbl[u] = lbl
        return lbl

    newlbl = {}
    compress(T)
    newlbl[S] = S
    newlbl[T] = T
    for t in Ts:
        newlbl[t] = t
    for u in newlbl:
        if newlbl[u] == zero:
            newlbl[u] = S

    graph.relabel(lambda u: newlbl.get(u, u))

    newlbl = {}
    for u in sorted(graph.V):
        if isinstance(u, tuple):
            newlbl[u] = len(newlbl)

    graph.relabel(lambda u: newlbl.get(u, u))
    V, A = graph.V, graph.A

    nv2, na2 = len(V), len(A)
    VPSolver.log("  #V2: {0} #A2: {1}".format(nv2, na2), verbose)
    VPSolver.log("  #V2/#V1 = {0:.2f}".format(nv2/nv1), verbose)
    VPSolver.log("  #A2/#A1 = {0:.2f}".format(na2/na1), verbose)

    if svg_file.endswith(".svg"):
        try:
            graph.draw(
                svg_file.replace(".svg", ".final.svg"), ignore=[(T, S)]
            )
        except Exception as e:
                VPSolver.log(e, verbose)

    # remove redudant parallel arcs
    At = []
    used = set()
    for (u, v, i) in A:
        k = itlabel[i][0] if i != LOSS else LOSS
        if (u, v, k) not in used:
            At.append((u, v, i))
            used.add((u, v, k))

    A = At
    graph = AFGraph(V, A, S, T)

    nv3, na3 = len(V), len(A)
    VPSolver.log("  #V3: {0} #A3: {1}".format(nv3, na3), verbose)
    VPSolver.log("  #V3/#V1 = {0:.2f}".format(nv3/nv1), verbose)
    VPSolver.log("  #A3/#A1 = {0:.2f}".format(na3/na1), verbose)

    varl, cons = graph.get_flow_cons()

    assocs = graph.get_assocs()
    for i in range(len(b)):
        lincomb = [
            (var, 1)
            for it, (j, t) in enumerate(itlabel) if j == i
            for var in assocs[it]
        ]
        # cons.append((lincomb, ">=", b[i]))
        if b[i] > 1:
            cons.append((lincomb, ">=", b[i]))
        else:
            cons.append((lincomb, "=", b[i]))

    model = Model()

    ub = {}
    for i in range(len(b)):
        for var in assocs[i]:
            ub[var] = b[i]

    n = sum(b)
    for i in range(nbtypes):
        var = graph.vname(Ts[i], T, LOSS)
        ub[var] = min(Qs[i], n)

    for var in varl:
        # model.add_var(name=var, lb=0, vtype="I")
        model.add_var(name=var, lb=0, ub=ub.get(var, None), vtype="I")

    for lincomb, sign, rhs in cons:
        model.add_con(lincomb, sign, rhs)

    lincomb = [(graph.vname(Ts[i], T, LOSS), Cs[i]) for i in range(nbtypes)]
    model.set_obj("min", lincomb)

    model_file = VPSolver.new_tmp_file(".lp")
    model.write(model_file)
    if lp_file.endswith(".lp"):
        model.write(lp_file)
        VPSolver.log(".LP model successfully generated!", verbose)
    if mps_file.endswith(".mps"):
        model.write(mps_file)
        VPSolver.log(".MPS model successfully generated!", verbose)
    out, varvalues = VPSolver.script_wsol(script, model_file, verbose=verbose)
    os.remove(model_file)

    VPSolver.log("#V1: {0} #A1: {1}".format(nv1, na1), verbose)
    VPSolver.log("#V2: {0} #A2: {1}".format(nv2, na2), verbose)
    VPSolver.log("#V3: {0} #A3: {1}".format(nv3, na3), verbose)
    VPSolver.log(
        "#V3/#V1: {0:.2f} #A3/#A1: {1:.2f}".format(
            nv3/nv1, na3/na1
        ),
        verbose
    )

    labels = {}
    for (u, v, i) in A:
        if i != LOSS:
            labels[u, v, i] = [itlabel[i]]

    lst_sol = []
    graph.set_flow(varvalues)
    graph.set_labels(labels)
    for i in range(nbtypes):
        lst_sol.append(graph.extract_solution(S, "<-", Ts[i]))

    assert graph.validate_solution(lst_sol, nbtypes, ndims, Ws, ws, b)

    c1 = sum(sum(r for r, patt in lst_sol[i])*Cs[i] for i in range(nbtypes))
    c2 = sum(
        varvalues.get(graph.vname(Ts[i], T, LOSS), 0) * Cs[i]
        for i in range(nbtypes)
    )
    assert c1 == c2

    return c1, lst_sol


def print_solution(obj, lst_sol, fout=sys.stdout):
    """Pretty-print function for multiple-choice vector packing solutions."""
    if obj is not None:
        print("Objective:", obj, file=fout)
    print("Solution:", file=fout)
    for i, sol in enumerate(lst_sol):
        cnt = sum(m for m, p in sol)
        print("Bins of type {0}: {1} {2}".format(
            i+1, cnt, ["bins", "bin"][cnt == 1]
        ), file=fout)
        for mult, patt in sol:
            print("{0} x [{1}]".format(
                mult, ", ".join(
                    ["i={0} opt={1}".format(it+1, opt+1) for it, opt in patt]
                )
            ), file=fout)
