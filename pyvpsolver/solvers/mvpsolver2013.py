"""
This code is part of the Arc-flow Vector Packing Solver (VPSolver).
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


def solve(
    Ws,
    Cs,
    Qs,
    ws,
    b,
    transitive_reduction=True,
    svg_file="",
    lp_file="",
    mps_file="",
    script=None,
    script_options=None,
    stats=None,
    verbose=None,
):
    """
    Solve multiple-choice vector bin packing instances
    using the method proposed in:
    Brandao, F. and Pedroso, J. P. (2013). Multiple-choice Vector
    Bin Packing: Arc-flow Formulation with Graph Compression. Technical Report
    DCC-2013-13, Faculdade de Ciencias da Universidade do Porto, Universidade
    do Porto, Portugal.
    """
    assert script is not None
    assert svg_file == "" or svg_file.endswith(".svg")
    if stats is None and verbose is not None:
        stats = verbose
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

    LOSS = "L"
    instances = [None] * nbtypes
    graphs = [None] * nbtypes
    Ss, Ts = [None] * nbtypes, [None] * nbtypes
    for i in range(nbtypes):
        bbi = bb[:]
        for j in range(len(ww)):
            if any(a > b for a, b in zip(ww[j], Ws[i])):
                bbi[j] = 0
                continue
        symb = "G{0}:".format(i)
        instances[i] = VBP(Ws[i], ww, bbi, verbose=False)
        graphs[i] = AFG(instances[i], verbose=verbose).graph()
        loss = graphs[i].LOSS
        graphs[i].relabel(
            lambda u: "{0}{1}".format(symb, u), lambda lbl: lbl if lbl != loss else LOSS
        )
        Ss[i] = graphs[i].S
        Ts[i] = graphs[i].Ts[0]
        graphs[i].A.remove((Ts[i], Ss[i], LOSS))
        if svg_file.endswith(".svg"):
            try:
                graphs[i].draw(
                    svg_file.replace(".svg", "{0}.svg".format(i + 1)), verbose=verbose
                )
            except Exception as e:
                VPSolver.log(e, verbose)

    S, T = "S", "T"
    V = sum([g.V for g in graphs], [])
    A = sum([g.A for g in graphs], [])
    V += [S, T]
    A += [(S, s, LOSS) for s in Ss]
    A += [(t, T, LOSS) for t in Ts]
    A += [(T, S, LOSS)]

    graph = AFGraph(V, A, S, [T], LOSS)
    if svg_file.endswith(".svg"):
        try:
            graph.draw(svg_file, verbose=verbose)
        except Exception as e:
            VPSolver.log(e, verbose)

    adj = {u: [] for u in V}
    for (u, v, i) in A:
        adj[v].append((u, i))

    VPSolver.log("Final compression steps:", verbose)

    nv1, na1 = len(V), len(A)
    VPSolver.log("  #V1: {0} #A1: {1}".format(nv1, na1), verbose=stats)
    zero = tuple([0] * ndims)

    def compress(u):
        if u == S:
            return zero
        if u in newlbl:
            return newlbl[u]
        lbl = zero
        for v, i in adj[u]:
            wi = ww[i] if i != LOSS else zero
            vlbl = compress(v)
            lbl = tuple(max(lbl[d], vlbl[d] + wi[d]) for d in range(ndims))
        newlbl[u] = lbl
        return lbl

    # Relabel the graph using the longest path from the source:
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

    if transitive_reduction:
        # Reduce graph size by connecting nodes to non-dominated targets only:
        tadj = {}
        for (u, v, i) in graph.A:
            if isinstance(u, tuple):
                if v in Ts:
                    if u not in tadj:
                        tadj[u] = []
                    tadj[u].append(Ts.index(v))

        graph.A = [(u, v, i) for (u, v, i) in graph.A if v not in Ts]
        V, A = set(graph.V), set(graph.A)

        def fits(w1, w2):
            return all(x <= y for x, y in zip(w1, w2))

        dominatedby = {i: [] for i in range(nbtypes)}
        for i in range(nbtypes):
            for j in range(nbtypes):
                if i < j and Ws[i] == Ws[j]:
                    dominatedby[i].append(j)
                elif i != j and fits(Ws[i], Ws[j]):
                    dominatedby[i].append(j)

        for v in tadj:
            tgts = set(tadj[v])
            for i in range(nbtypes):
                if i not in tgts:
                    continue
                for j in dominatedby[i]:
                    try:
                        tgts.remove(j)
                    except:
                        pass
            for t in tgts:
                A.add((v, Ts[t], LOSS))

        for i in range(nbtypes):
            tgts = set(dominatedby[i])
            for j in dominatedby[i]:
                for t in dominatedby[j]:
                    try:
                        tgts.remove(t)
                    except:
                        pass
            for t in tgts:
                A.add((Ts[i], Ts[t], LOSS))

        graph.V, graph.A = V, A

    # Relabel the graph with indices:
    newlbl = {}
    for u in graph.get_vertices_sorted():
        if isinstance(u, tuple):
            newlbl[u] = len(newlbl) + 1
    graph.relabel(lambda u: newlbl.get(u, u))
    V, A = graph.V, graph.A

    nv2, na2 = len(V), len(A)
    VPSolver.log("  #V2: {0} #A2: {1}".format(nv2, na2), verbose=stats)
    VPSolver.log("  #V2/#V1 = {0:.2f}".format(nv2 / nv1), verbose=stats)
    VPSolver.log("  #A2/#A1 = {0:.2f}".format(na2 / na1), verbose=stats)

    if svg_file.endswith(".svg"):
        try:
            graph.draw(svg_file.replace(".svg", ".final.svg"), verbose=verbose)
        except Exception as e:
            VPSolver.log(e, verbose)

    # Remove redudant parallel arcs:
    At = []
    used = set()
    for (u, v, i) in A:
        k = itlabel[i][0] if i != LOSS else LOSS
        if (u, v, k) not in used:
            At.append((u, v, i))
            used.add((u, v, k))
    A = At
    graph = AFGraph(V, A, S, [T], LOSS)

    nv3, na3 = len(V), len(A)
    VPSolver.log("  #V3: {0} #A3: {1}".format(nv3, na3), verbose=stats)
    VPSolver.log("  #V3/#V1 = {0:.2f}".format(nv3 / nv1), verbose=stats)
    VPSolver.log("  #A3/#A1 = {0:.2f}".format(na3 / na1), verbose=stats)

    # Generate the model:
    varl, cons = graph.get_flow_cons()
    assocs = graph.get_assocs()
    for i in range(len(b)):
        lincomb = [
            (var, 1)
            for it, (j, t) in enumerate(itlabel)
            if j == i
            for var in assocs[it]
        ]
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
        if Qs[i] == -1:
            ub[var] = n
        else:
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
        "#V3/#V1: {0:.2f} #A3/#A1: {1:.2f}".format(nv3 / nv1, na3 / na1), verbose
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

    validate_solution(lst_sol, nbtypes, ndims, Ws, ws, b)

    c1 = sum(sum(r for r, patt in lst_sol[i]) * Cs[i] for i in range(nbtypes))
    c2 = sum(
        varvalues.get(graph.vname(Ts[i], T, LOSS), 0) * Cs[i] for i in range(nbtypes)
    )
    assert c1 == c2

    return c1, lst_sol


def validate_solution(lst_solutions, nbtypes, ndims, Ws, ws, b):
    """Validate multiple-choice vector packing solutions."""
    if any(
        sum(ws[it][t][d] for (it, t) in pat) > Ws[i][d]
        for i in range(nbtypes)
        for d in range(ndims)
        for r, pat in lst_solutions[i]
    ):
        return False

    aggsol = sum([sol for sol in lst_solutions], [])

    c = [0] * len(b)
    for (r, p) in aggsol:
        for i, t in p:
            c[i] += r

    return all(c[i] >= b[i] for i in range(len(b)))


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
        print(
            "Bins of type {0}: {1} {2}".format(i + i0, cnt, ["bins", "bin"][cnt == 1]),
            file=fout,
        )
        for mult, patt in sol:
            print(
                "{0} x [{1}]".format(
                    mult,
                    ", ".join(
                        ["i={0} opt={1}".format(it + i0, opt + i0) for it, opt in patt]
                    ),
                ),
                file=fout,
            )
