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

from .utils import inf, relabel_graph, sort_vertices, sort_arcs, draw_graph


class AFGraph(object):
    """Manipulable graph objects."""

    def __init__(self, V, A, S, Ts, LOSS=None):
        self.V, self.A = list(set(V)), list(set(A))
        self.S, self.Ts, self.LOSS = S, Ts, LOSS
        self.names = {}
        self.flow = None
        self.labels = None

    def relabel(self, fv, fa=lambda x: x):
        """Relabel the graph."""
        assert self.flow is None
        assert self.labels is None
        self.V, self.A = relabel_graph(self.V, self.A, fv, fa)
        if self.LOSS is not None:
            self.LOSS = fa(self.LOSS)
        if self.S is not None:
            self.S = fv(self.S)
        if self.Ts is not None:
            self.Ts = [fv(t) for t in self.Ts]

    def draw(self, svg_file, show_labels=False, ignore=None, back=None,
             loss=None, weights=None, capacities=None, lpaths=False,
             graph_attrs=None, verbose=False):
        """Draw the arc-flow graph in .svg format."""
        V, A = self.V, self.A
        if loss is None:
            loss = self.LOSS
        if back is None:
            back = set((u, v) for (u, v, i) in self.A if v == self.S)

        if lpaths:
            assert weights is not None
            assert capacities is not None
            lp_source = self.lpaths_source(weights, capacities)
            lp_targets = self.lpaths_targets(weights, capacities)
            newlabels = {
                v: "{}:\nL({})\nU({})".format(
                    str(v),
                    ",".join(map(str, lp_source[v])),
                    ",".join(map(str, lp_targets[v]))
                )
                for v in V
            }
            if ignore is not None:
                ignore = [
                    (newlabels.get(u, u), newlabels.get(v, v))
                    for (u, v) in ignore
                ]
            if back is not None:
                back = [
                    (newlabels.get(u, u), newlabels.get(v, v))
                    for (u, v) in back
                ]
            V, A = relabel_graph(V, A, lambda v: newlabels.get(v, v))

        draw_graph(
            svg_file, sort_vertices(V), sort_arcs(A),
            show_labels=show_labels, ignore=ignore, back=back, loss=loss,
            graph_attrs=graph_attrs, verbose=verbose
        )

    def vname(self, u, v, i, vnames=None):
        """Return the variable name attributed to the arc."""
        if vnames is None:
            vnames = self.names
        if (u, v, i) in vnames:
            return vnames[u, v, i]
        vnames[u, v, i] = "F{0:x}".format(len(vnames))
        # vnames[u, v, i] = "F_{0}_{1}_{2}".format(u, v, i)
        return vnames[u, v, i]

    def lpaths_source(self, weights, capacities):
        """Compute longest paths to the source."""
        ndims = len(capacities[0])
        radj = {u: [] for u in self.V}
        for u, v, lbl in self.A:
            if v != self.S:
                radj[v].append((u, lbl))

        zero = tuple([0]*ndims)
        minlabel = tuple([0]*ndims)

        def lp_source(u, labels):
            if u in labels:
                return labels[u]
            lbl = minlabel
            for v, it in radj[u]:
                wi = weights.get(it, zero)
                vlbl = lp_source(v, labels)
                lbl = tuple(max(lbl[d], vlbl[d]+wi[d]) for d in range(ndims))
            labels[u] = lbl
            return lbl

        labels = {}
        for t in self.Ts:
            lp_source(t, labels)
        return labels

    def lpaths_targets(self, weights, capacities):
        """Compute longest paths to the targets."""
        ndims = len(capacities[0])
        adj = {u: [] for u in self.V}
        for u, v, lbl in self.A:
            if v != self.S:
                adj[u].append((v, lbl))

        zero = tuple([0]*ndims)
        maxlabel = tuple([inf]*ndims)

        def lp_targets(u, labels):
            if u in labels:
                return labels[u]
            lbl = maxlabel
            for v, it in adj[u]:
                wi = weights.get(it, zero)
                vlbl = lp_targets(v, labels)
                lbl = tuple(min(lbl[d], vlbl[d]-wi[d]) for d in range(ndims))
            labels[u] = lbl
            return lbl

        labels = {t: Wt for t, Wt in zip(self.Ts, capacities)}
        lp_targets(self.S, labels)
        return labels

    def get_vertices_sorted(self, reverse=False):
        """Return the list of vertices sorted."""
        return sort_vertices(self.V, reverse)

    def get_arcs_sorted(self, reverse=False):
        """Return the list of arcs sorted."""
        return sort_arcs(self.A, reverse)

    def get_flow_cons(self, vnames=None):
        """Return the list of flow conservation constraints."""
        Ain = {u: [] for u in self.V}
        Aout = {u: [] for u in self.V}
        varl = []
        for (u, v, i) in self.get_arcs_sorted():
            name = self.vname(u, v, i, vnames)
            Aout[u].append(name)
            Ain[v].append(name)
            varl.append(name)
        cons = []
        for u in self.get_vertices_sorted():
            if Ain[u] != [] and Aout[u] != []:
                lincomb = []
                if u in Ain:
                    lincomb += [(var, 1) for var in Ain[u]]
                if u in Aout:
                    lincomb += [(var, -1) for var in Aout[u]]
                if lincomb != []:
                    cons.append((lincomb, "=", 0))
        return varl, cons

    def get_assocs(self, vnames=None):
        """Return the arc variables grouped by label."""
        assocs = {}
        for (u, v, i) in self.get_arcs_sorted():
            if i not in assocs:
                assocs[i] = []
            name = self.vname(u, v, i, vnames)
            assocs[i].append(name)
        return assocs

    def set_flow(self, varvalues, vnames=None):
        """Set flows."""
        flow = {}
        for (u, v, i) in self.A:
            name = self.vname(u, v, i, vnames)
            f = varvalues.get(name, 0)
            if f != 0:
                flow[u, v, i] = f
        self.flow = flow

    def set_labels(self, labels):
        """Set labels."""
        self.labels = labels

    def extract_solution(self, source, direction, target, flow_limit=inf):
        """Extract a vector packing solution form an arc-flow solution."""
        assert direction in ("<-", "->")
        assert self.flow is not None
        assert self.labels is not None
        flow = self.flow
        labels = self.labels
        adj = {u: [] for u in self.V}

        if direction == "<-":
            node_a, node_b = target, source
            for (u, v, i) in flow:
                adj[v].append((u, (u, v, i)))
        else:
            node_a, node_b = source, target
            for (u, v, i) in flow:
                adj[u].append((v, (u, v, i)))

        if node_a not in adj or node_b not in adj:
            return []

        solution = []

        def go(u, f, path):
            """Recursive function for flow extraction."""
            if f == 0:
                return
            if u == node_b:
                patt = []
                for arc in path:
                    flow[arc] -= f
                    patt += labels.get(arc, [])
                solution.append((f, patt))
            else:
                for v, arc in adj[u]:
                    # v != node_a to avoid cycles
                    if v != node_a and flow[arc] > 0:
                        ff = min(f, flow[arc])
                        go(v, ff, path+[arc])
                        f -= ff

        go(node_a, flow_limit, [])

        # group identical patterns
        rep = {}
        for (r, p) in solution:
            p = tuple(sorted(p, key=repr))
            if p not in rep:
                rep[p] = r
            else:
                rep[p] += r

        solution = []
        for p in rep:
            solution.append((rep[p], list(p)))

        return solution
