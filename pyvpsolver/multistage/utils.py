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
from __future__ import division
from builtins import str, map, object, range, zip, sorted


def raster_points(W, demands):
    V = set([0])
    for w in sorted(demands, reverse=True):
        T = set()
        for u in V:
            for j in range(demands[w]):
                v = u+w
                if v >= W:
                    break
                if v not in V:
                    T.add(v)
                u = v
        V |= T
    return sorted(V)


def raster_points_org(W, demands):
    """Algorithms for two-dimensional cutting stock and strip
    packing problems using dynamic programming
    and column generation
    http://www.ime.usp.br/~yw/papers/accepted/2D-CuttingStock.DPCG2008.pdf
    """
    dp = [0]*(W+1)
    for w in sorted(demands, reverse=True):
        for i in range(demands[w]):
            for j in range(w, W+1):
                dp[j] = max(dp[j-w]+w, dp[j])
    return [j for j, v in enumerate(dp) if v == j]


def subprob_label(prefix, dim):
    return "{}[{}]".format(prefix, ",".join(map(str, dim)))


def item_label(it, dim, rotated=False):
    if not rotated:
        return "I{}[{}]".format(it, ",".join(map(str, dim)))
    else:
        return "I{}[{}]^".format(it, ",".join(map(str, dim)))


class MultiStage(object):
    """Multi-stage cutting stock."""
    def __init__(self, bins, cost):
        self.problems_at = {}
        self.groups = {}
        self.dimension = {}
        self.cost = {}
        self.demand = {}
        self.subproblem = {}
        self.group_demand = {}
        self.problems_at[0] = set()
        for bdim, bcost in zip(bins, cost):
            prob = subprob_label("root", bdim)
            self.cost[prob] = bcost
            self.dimension[prob] = bdim
            self.problems_at[0].add(prob)
        self.nstages = 0
        self.ready = False

    def add_stage(self, stage_function, args=None):
        assert not self.ready
        self.nstages += 1
        stage = self.nstages
        assert (
            stage-1 in self.problems_at and
            len(self.problems_at[stage-1]) != 0 and
            stage not in self.problems_at
        )
        self.problems_at[stage] = set()
        for prob in self.problems_at[stage-1]:
            group_id, items, subprob = stage_function(
                self, self.dimension[prob], args
            )
            if group_id is not None:
                self.add_to_group(group_id, prob)
            self.subproblem[prob] = subprob
            for newprob, dim, group_id in items:
                self.dimension[newprob] = dim
                self.problems_at[stage].add(newprob)
                if group_id is not None:
                    self.add_to_group(group_id, newprob)

    def add_to_group(self, group_id, prob):
        if group_id not in self.groups:
            self.groups[group_id] = set([prob])
        else:
            self.groups[group_id].add(prob)

    def set_group_demands(self, b):
        assert not self.ready
        for group_id in b:
            self.group_demand[group_id] = b[group_id]
            for item in self.groups[group_id]:
                self.demand[item] = b[group_id]
        self.propagate_demands()
        self.ready = True

    def propagate_demands(self):
        removelst = []
        for stage in sorted(self.problems_at, reverse=True):
            for prob in self.problems_at[stage]:
                if prob in self.subproblem:
                    b = sum(
                        self.demand.get(it, 0)
                        for it, w, noslack in self.subproblem[prob][1]
                        if noslack
                    )
                    if b > 0:
                        self.demand[prob] = b
                    else:
                        removelst.append(prob)
                else:
                    assert prob in self.demand
        self.remove_problems(removelst)

    def remove_problems(self, removelst):
        for prob in removelst:
            # print("remove", prob)
            for stage in self.problems_at:
                if prob in self.problems_at[stage]:
                    self.problems_at[stage].remove(prob)
            if prob in self.subproblem:
                del self.subproblem[prob]
            if prob in self.demand:
                del self.demand[prob]
        for prob in self.subproblem:
            subp = self.subproblem[prob]
            subp = (subp[0], [
                (it, w, noslack)
                for it, w, noslack in subp[1]
                if self.demand.get(it, 0) > 0
            ])
            self.subproblem[prob] = subp
        for key in self.groups:
            for prob in list(self.groups[key]):
                if self.demand.get(prob, 0) == 0:
                    self.groups[key].remove(prob)


def guillotine_cut(obj, parent_dim, args):
    label, cutdim, cuts = args
    stage = obj.nstages
    parent_group = (stage-1, cutdim)+tuple([
        parent_dim[i] for i in range(len(parent_dim)) if i != cutdim
    ])
    tmp = []
    for cutsize in cuts:
        if cutsize <= parent_dim[cutdim]:
            dim = parent_dim[:cutdim] + (cutsize,) + parent_dim[cutdim+1:]
            tmp.append((subprob_label(label, dim), dim, cutsize, None))
    newitems = [(lbl, dim, group_id) for lbl, dim, weigth, group_id in tmp]
    subprob = (parent_dim[cutdim], [
        (lbl, weight, True) for lbl, dim, weight, group_id in tmp
    ])
    return parent_group, newitems, subprob


def cut_items(obj, parent_dim, args):
    itdims, cutdim, exact, allow_rotation, allow_slack = args
    from itertools import permutations
    parent_group = (obj.nstages-1, cutdim)+tuple([
        parent_dim[i] for i in range(len(parent_dim)) if i != cutdim
    ])
    ndims = len(parent_dim)
    m = len(itdims)
    newitems = []
    subprob = (parent_dim[cutdim], [])
    any_noslack = False
    for i in range(m):
        if allow_rotation is False:
            options = [tuple(itdims[i])]
        else:
            options = list(set(permutations(itdims[i], ndims)))
        best_dim = None
        for dim in options:
            if best_dim is None or dim[cutdim] < best_dim[cutdim]:
                if not exact:
                    if all(dim[i] <= parent_dim[i] for i in range(ndims)):
                        best_dim = dim
                else:
                    if all(
                        dim[i] == parent_dim[i] if i != cutdim else
                        dim[i] <= parent_dim[i]
                        for i in range(ndims)
                    ):
                        best_dim = dim
        if best_dim is not None:
            item = item_label(i, best_dim, best_dim != tuple(itdims[i]))
            newitems.append((item, best_dim, "I{}".format(i)))
            noslack = all(
                best_dim[d] == parent_dim[d]
                for d in range(ndims) if d != cutdim
            )
            any_noslack = any_noslack or noslack
            subprob[1].append((item, best_dim[cutdim], noslack))

    if not allow_slack and not exact and newitems != []:
        if not any_noslack:
            newitems = []
            subprob = (parent_dim[cutdim], [])
    return parent_group, newitems, subprob
