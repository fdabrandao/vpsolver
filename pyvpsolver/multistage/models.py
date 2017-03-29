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
but wiHOUT ANY WARRANTY; wihout even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along wih this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from __future__ import print_function
from __future__ import division
from builtins import str, map, object, range, zip, sorted

from time import time
from .. import VBP, MVP, AFG, AFGraph
from pympl import Model

LOSS = "L"


def multistage_simple(prob, verbose=None):
    """Model multi-stage cutting stock problems using arc-flow models."""
    assert prob.ready
    V, A = [], []
    zflow = {}
    count = 0
    total_count = sum(
        1 for stage in sorted(prob.problems_at)
        for curbin in sorted(prob.problems_at[stage])
        if curbin in prob.subproblem
    )
    print("#Groups:", len(prob.groups)-len(prob.group_demand))
    for stage in sorted(prob.problems_at)[:-1]:
        print("Stage {}: {}".format(stage+1, len(prob.problems_at[stage])))
    for stage in sorted(prob.problems_at):
        for curbin in sorted(prob.problems_at[stage]):
            if curbin not in prob.subproblem:
                continue
            count += 1
            if count % 100 == 0:
                print("Graph: {}/{}".format(count, total_count))
            W, tmp = prob.subproblem[curbin]
            subp = [
                (it, w, min(W//w, prob.demand[it]))
                for it, w, noslack in tmp
                if min(W//w, prob.demand.get(it, 0)) > 0
            ]
            items = [it for it, w, b in subp]
            itw = [(w,) for it, w, b in subp]
            itb = [b for it, w, b in subp]
            instance = VBP((W,), itw, itb, verbose=False)
            graph = AFG(instance, verbose=False).graph()
            graph.relabel(
                lambda v: "{}:{}".format(curbin, v),
                lambda it: ("IT", items[it]) if it < len(items) else LOSS
            )
            feedback = (graph.Ts[0], graph.S, LOSS)
            graph.A.append(feedback)
            zflow[curbin] = feedback
            V += graph.V
            A += graph.A

    V = list(set(V))
    A = list(set(A))
    print("#V:", len(V))
    print("#A:", len(A))

    graph = AFGraph(V, A, None, None, LOSS=LOSS)
    vnames = {}
    ub = {}
    varl, cons = graph.get_flow_cons(vnames)
    assocs = graph.get_assocs(vnames)

    for curbin in zflow:
        lbl = ("IT", curbin)
        if lbl in assocs:
            var = vnames[zflow[curbin]]
            ub[var] = prob.demand[curbin]
            cons.append((assocs[lbl], ">=", var))
        else:
            assert curbin in prob.cost

    for group in sorted(prob.group_demand):
        b = prob.group_demand[group]
        arcs = []
        for lbl in prob.groups[group]:
            arcs += assocs[("IT", lbl)]
        if b > 1:
            cons.append((arcs, ">=", b))
        else:
            cons.append((arcs, "=", b))

    ub = {}

    print("NVARS:", len(varl))
    print("NCONS:", len(cons))

    model = Model()
    for var in varl:
        model.add_var(name=var, lb=0, ub=ub.get(var, None), vtype="I")
    for lincomb, sign, rhs in cons:
        model.add_con(lincomb, sign, rhs)
    objlincomb = [
        (vnames[zflow[curbin]], prob.cost[curbin]) for curbin in prob.cost
    ]
    model.set_obj("min", objlincomb)
    return graph, zflow, vnames, model


def multistage_groups(prob, verbose=None):
    """Model multi-stage cutting stock problems using arc-flow models
    and grouping compatible cutting-stock sub-problems into
    variable-sized cutting-stock problems.
    """
    assert prob.ready
    t0 = time()
    V, A = set(), set()
    zflow = {}
    print("#Groups:", len(prob.groups)-len(prob.group_demand))
    for stage in sorted(prob.problems_at)[:-1]:
        print("Stage {}: {}".format(stage+1, len(prob.problems_at[stage])))
    gi = 1
    print("---")

    group_name = {}
    for group_id in prob.groups:
        for item in prob.groups[group_id]:
            group_name[item] = group_id

    for key in sorted(prob.groups):
        if not any(p in prob.subproblem for p in prob.groups[key]):
            continue
        probnames = []
        Ws = []
        items = {}
        for p in prob.groups[key]:
            assert p in prob.subproblem
            assert p in prob.demand
            probnames.append(p)
            W = (prob.subproblem[p][0],)
            assert W not in Ws
            Ws.append(W)
            for it, w, noslack in prob.subproblem[p][1]:
                assert it in prob.demand
                assert it not in items or items[it] == (w,)
                items[it] = (w,)

        labels = []
        ws, bs = [], []
        grps = set()
        for it, w in items.items():
            grps.add(group_name[it])
            labels.append((group_name[it], it))
            ws.append(items[it])
            bs.append(prob.demand[it])

        # print(key, sorted(ws), sorted(Ws))
        cpp = True
        if cpp:
            Cs = [1]*len(Ws)
            Qs = [-1]*len(Ws)
            ws = [(wi,) for wi in ws]
            instance = MVP(Ws, Cs, Qs, ws, bs, verbose=False)
            afg = AFG(instance, verbose=False)
            # wih open(afg.afg_file, "r") as f:
            #     print(f.read())
            graph = afg.graph()
            graph.relabel(
                lambda u: u,
                lambda lbl: labels[lbl[0]] if lbl != graph.LOSS else LOSS
            )
            Ts = graph.Ts
        else:
            mvp_graph = MVBPGraph(  # FIXME
                ws, bs, Ws, labels,
                iterative=True,
                verbose=False
            )
            Ts = mvp_graph.Ts
            graph = mvp_graph.graph

        graph.relabel(lambda v: "G{}:{}".format(gi, v))

        assert V & set(graph.V) == set()
        assert A & set(graph.A) == set()
        V |= set(graph.V)
        A |= set(graph.A)
        for i, name in enumerate(probnames):
            zflow[name] = (
                "G{}:{}".format(gi, Ts[i]), "G{}:S".format(gi), LOSS
            )
        gi += 1

    V = list(set(V))
    A = list(set(A))
    print("#V:", len(V))
    print("#A:", len(A))
    print("time: {:.2f}".format(time()-t0))

    graph = AFGraph(V, A, None, None, LOSS=LOSS)
    vnames = {}
    ub = {}
    varl, cons = graph.get_flow_cons(vnames)
    assocs = graph.get_assocs(vnames)

    for curbin in zflow:
        if (group_name[curbin], curbin) in assocs:
            zarc = vnames[zflow[curbin]]
            ub[zarc] = prob.demand[curbin]
            cons.append((assocs[group_name[curbin], curbin], ">=", zarc))
        else:
            assert curbin in prob.cost

    for group in sorted(prob.group_demand):
        b = prob.group_demand[group]
        arcs = []
        for lbl in prob.groups[group]:
            arcs += assocs.get((group, lbl), [])
        if b > 1:
            cons.append((arcs, ">=", b))
        else:
            cons.append((arcs, ">=", b))

    print("NVARS:", len(varl))
    print("NCONS:", len(cons))

    ub = {}

    model = Model()
    for var in varl:
        # model.add_var(name=var, lb=0, vtype="I")
        model.add_var(name=var, lb=0, ub=ub.get(var, None), vtype="I")
    for lincomb, sign, rhs in cons:
        model.add_con(lincomb, sign, rhs)

    objlincomb = [
        (vnames[zflow[curbin]], prob.cost[curbin]) for curbin in prob.cost
    ]
    model.set_obj("min", objlincomb)
    return graph, zflow, vnames, model


def onecut_model(W, H, w, h, b, stage3=False, exact=False, rotation=False):
    """Model two- and three-stage cutting stock problems using the mothod
    proposed in: "Silva et al. (2010). An integer programming model for
    two- and three-stage two-dimensional cutting stock problems.
    """
    def vname(i, j):
        return "x[{},{}]".format(i, j)

    def cut_stage1(pw, ph, wi, hi):
        return [(pw, ph-hi, 1), (pw-wi, hi, 2)]

    def cut_stage2(pw, ph, wi, hi):
        if stage3 is False:
            if not exact or hi == ph:
                return [(pw-wi, hi, 2)]
            else:
                return []
        else:
            return [(wi, ph-hi, 3), (pw-wi, ph, 2)]

    def cut_stage3(pw, ph, wi, hi):
        if not exact or wi == pw:
            return [(wi, ph-hi, 3)]
        else:
            return []

    def cut(plate, it):
        pw, ph, stage = plate
        cut_func = [None, cut_stage1, cut_stage2, cut_stage3][stage]
        return cut_func(pw, ph, w[it], h[it])

    def fits(plate, it):
        pw, ph, stage = plate
        return w[it] <= pw and h[it] <= ph

    org_types = len(w)
    labels = list(range(org_types))
    if rotation:
        w, h = w[:], h[:]
        for i in range(org_types):
            if w[i] != h[i]:
                w.append(h[i])
                h.append(w[i])
                labels.append(i)

    m = len(w)
    initial = (W, H, 1)
    R = {initial: 0}
    C = set((initial, it) for it in range(m))
    A = set((initial, it) for it in range(m))
    cuts = {}
    while len(C) != 0:
        c = C.pop()
        A.add(c)
        plate, it = c
        new_plates = cut(plate, it)
        for residual_plate in new_plates:
            if residual_plate not in R:
                R[residual_plate] = len(R)
            pi = R[plate]
            pr = R[residual_plate]
            if (it, pi) not in cuts:
                cuts[it, pi] = set()
            cuts[it, pi].add(pr)
        for residual_plate in new_plates:
            for it in range(m):
                if fits(residual_plate, it):
                    if (residual_plate, it) not in A:
                        C.add((residual_plate, it))

    assocs_it = {}
    assocs_pi = {}
    assocs_pr = {}
    for it, pi in cuts:
        if it not in assocs_it:
            assocs_it[it] = []
        assocs_it[it].append(pi)
        if pi not in assocs_pi:
            assocs_pi[pi] = []
        assocs_pi[pi].append(it)
        for pr in cuts[it, pi]:
            if pr not in assocs_pr:
                assocs_pr[pr] = []
            assocs_pr[pr].append((it, pi))

    varl = []
    cons = []
    for it in range(org_types):
        prod_it = [
            vname(i, pi)
            for i in range(m)
            if labels[i] == it
            for pi in assocs_it[i]
        ]
        varl += prod_it
        cons.append((prod_it, ">=", b[it]))

    for k in assocs_pr:
        if k in assocs_pi:
            prod_k = [vname(it, pi) for it, pi in assocs_pr[k]]
            use_k = [vname(it, k) for it in assocs_pi[k]]
            cons.append((prod_k, ">=", use_k))

    print("#R:", len(R))
    print("NVARS:", len(varl))
    print("NCONS:", len(cons))

    model = Model()
    for var in varl:
        model.add_var(name=var, lb=0, vtype="I")
    for left, sign, right in cons:
        model.add_con(left, sign, right)
    objlincomb = [(vname(it, 0), 1) for it in assocs_pi[0]]
    model.set_obj("min", objlincomb)
    return model
