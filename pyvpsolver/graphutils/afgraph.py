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
from builtins import zip
from builtins import map
from builtins import range
from builtins import sorted
from builtins import object

from .afgutils import AFGUtils

inf = float("inf")


class AFGraph(object):
    """Manipulable graph objects."""

    def __init__(self, V, A, S, Ts, LOSS=None):
        self.V, self.A = list(set(V)), list(set(A))
        self.S, self.Ts, self.LOSS = S, Ts, LOSS
        self.names = {}
        self.flow = None
        self.labels = None

    @classmethod
    def from_file(cls, afg_file, labels=None):
        """Loads a graph from a .afg file."""
        V, A, S, Ts, LOSS = AFGUtils.read_graph(afg_file, labels)
        lbls = {}
        lbls[S] = "S"
        if len(Ts) > 1:
            newTs = ["T{}".format(i+1) for i in range(len(Ts))]
            for t, newt in zip(Ts, newTs):
                lbls[t] = newt
        else:
            newTs = ["T"]
            lbls[Ts[0]] = "T"
        V, A = AFGUtils.relabel(V, A, lambda u: lbls.get(u, u))
        return cls(V, A, "S", newTs, LOSS)

    def relabel(self, fv, fa=lambda x: x):
        """Relabels the graph."""
        self.V, self.A = AFGUtils.relabel(self.V, self.A, fv, fa)
        if self.LOSS is not None:
            self.LOSS = fa(self.LOSS)
        if self.S is not None:
            self.S = fv(self.S)
        if self.Ts is not None:
            self.Ts = [fv(t) for t in self.Ts]

    def draw(self, svg_file, showlabels=False, ignore=None, back=None,
            loss=None, verbose=None):
        """Draws the arc-flow graph in .svg format."""
        if loss is None:
            loss = self.LOSS
        if back is None:
            back = set((u, v) for (u, v, i) in self.A if v == self.S)
        AFGUtils.draw(
            svg_file, self.V, self.A, showlabels=showlabels, ignore=ignore,
            back=back, loss=loss, verbose=verbose
        )

    def vname(self, u, v, i, vnames=None):
        """Returns the variable name attributed to an arc."""
        if vnames is None:
            vnames = self.names
        if (u, v, i) in vnames:
            return vnames[u, v, i]
        vnames[u, v, i] = "F{0:x}".format(len(vnames))
        # vnames[u, v, i] = "F_{0}_{1}_{2}".format(u, v, i)
        return vnames[u, v, i]

    def get_arcs_sorted(self, reverse=False):
        """Returns the list of arcs sorted."""
        return sorted(
            self.A, key=lambda a: tuple((repr(type(k)), k) for k in a),
            reverse=reverse
        )

    def get_vertices_sorted(self, reverse=False):
        """Returns the list of vertices sorted."""
        return sorted(
            self.V, key=lambda k: (repr(type(k)), k),
            reverse=reverse
        )

    def get_flow_cons(self, vnames=None):
        """Returns the list of flow conservation constraints."""
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
        """Returns the arc variables grouped by label."""
        assocs = {}
        for (u, v, i) in self.get_arcs_sorted():
            if i not in assocs:
                assocs[i] = []
            name = self.vname(u, v, i, vnames)
            assocs[i].append(name)
        return assocs

    def get_assocs_multi(self, vnames=None):
        """Returns the arc variables grouped by label (multi-label variant)."""
        assocs = {}
        for (u, v, l) in self.get_arcs_sorted():
            if not isinstance(l, (list, tuple)):
                lst = [l]
            else:
                lst = l
            name = self.vname(u, v, l, vnames)
            for i in set(lst):
                if i not in assocs:
                    assocs[i] = []
                coef = lst.count(i)
                assocs[i].append((name, coef))
        return assocs

    def set_flow(self, varvalues, vnames=None):
        """Sets arc flows."""
        flow = {}
        for (u, v, i) in self.A:
            name = self.vname(u, v, i, vnames)
            f = varvalues.get(name, 0)
            if f != 0:
                flow[u, v, i] = f
        self.flow = flow

    def set_labels(self, labels):
        """Sets arc labels."""
        self.labels = labels

    def extract_solution(self, source, direction, target, flow_limit=inf):
        """Extracts vector packing solutions form arc-flow solutions."""
        assert direction in ("<-", "->")
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
