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

from colors import *
from random import *

class AFGraph:
    def __init__(self, V, A, S, T):
        self.V, self.A = list(set(V)), list(set(A))
        self.S, self.T = S, T
        self.names = {}

    @classmethod
    def fromFile(cls, afg_file):
        V, A, S, T = AFGUtils.read_graph(afg_file)
        V, A = AFGUtils.relabel(V, A, lambda u: "S" if u == S else "T" if u == T else u)
        return cls(V, A, "S", "T")

    def relabel(self, fv, fa = lambda x: x):
        self.S = fv(self.S)
        self.T = fv(self.T)
        self.V, self.A = AFGUtils.relabel(self.V, self.A, fv, fa)

    def draw(self, svg_file, multigraph=True, showlabel=False, ignore=None, loss=None):
        AFGUtils.draw(svg_file, self.V, self.A, multigraph=multigraph, showlabel=showlabel, ignore=ignore, loss=loss)

    def vname(self, u, v, i, vnames=None):
        if vnames == None: vnames = self.names
        if (u,v,i) in vnames:
            return vnames[u,v,i]
        vnames[u,v,i] = "F%x" % len(vnames)
        #vnames[u,v,i] = "F_%s_%s_%s" % (u,v,i)
        return vnames[u,v,i]

    def getFlowCons(self, vnames=None):
        if self.V == None: self.load()
        Ain = {u:[] for u in self.V}
        Aout = {u:[] for u in self.V}
        varl = []
        for (u,v,i) in self.A:
            name = self.vname(u,v,i,vnames)
            Aout[u].append(name)
            Ain[v].append(name)
            varl.append(name)
        cons = []
        for u in self.V:
            if Ain[u] != [] and Aout[u] != []:
                lincomb = []
                if u in Ain:
                    lincomb += [(var, 1) for var in Ain[u]]
                if u in Aout:
                    lincomb += [(var, -1) for var in Aout[u]]
                if lincomb != []:
                    cons.append((lincomb,"=",0))
        return varl, cons

    def getAssocs(self, vnames=None):
        assocs = {}
        for (u,v,i) in self.A:
            if i not in assocs: assocs[i] = []
            name = self.vname(u,v,i,vnames)
            assocs[i].append(name)
        return assocs

    def getAssocsMulti(self, vnames=None):
        assocs = {}
        for (u,v,l) in self.A:
            if type(l) != list and type(l) != tuple:
                lst = [l]
            else:
                lst = l
            name = self.vname(u,v,l,vnames)
            for i in set(lst):
                if i not in assocs: assocs[i] = []
                coef = lst.count(i)
                assocs[i].append((name,coef))
        return assocs

    def set_flow(self, varvalues):
        flow = {}
        for (u,v,i) in self.A:
            name = self.vname(u,v,i)
            f = varvalues.get(name,0)
            if f != 0:
                flow[u,v,i] = f
        self.flow = flow

    def set_labels(self, labels):
        self.labels = labels

    def extract_solution(self, source, direction, target):
        assert direction in ['<-', '->']
        flow = self.flow
        labels = self.labels
        adj = {u:[] for u in self.V}

        if direction == '<-':
            node_a, node_b = target, source
            for (u,v,i) in flow:
                adj[v].append((u, (u,v,i)))
        else:
            node_a, node_b = source, target
            for (u,v,i) in flow:
                adj[u].append((v, (u,v,i)))

        if node_a not in adj or node_b not in adj: return []

        solution = []

        def go(u, f, path):
            if f == 0: return
            if u == node_b:
                patt = []
                for arc in path:
                    flow[arc] -= f
                    patt += labels.get(arc,[])
                solution.append((f,patt))
            else:
                for v,arc in adj[u]:
                    if v != node_a and flow[arc] > 0: # v != node_a to avoid cycles
                        ff = min(f, flow[arc])
                        go(v, ff, path+[arc])
                        f -= ff

        go(node_a, float('inf'), [])

        # group identical patterns
        rep = {}
        for (r, p) in solution:
            p = tuple(sorted(p))
            if p not in rep: rep[p] = r
            else: rep[p] += r

        solution = []
        for p in rep:
            solution.append((rep[p], list(p)))

        return solution

    def validate_solution(self, lst_solutions, nbtypes, ndims, Ws, ws, b):
        for i in xrange(nbtypes):
            for r, pat in lst_solutions[i]:
                if any(sum(ws[it][t][d] for (it, t) in pat) > Ws[i][d] for d in xrange(ndims)):
                    return False

        aggsol = sum([sol for sol in lst_solutions], [])

        c = [0] * len(b)
        for (r, p) in aggsol:
            for i, t in p:
                c[i] += r

        return all(c[i] >= b[i] for i in xrange(len(b)))

class AFGUtils:
    @staticmethod
    def read_graph(afg_file):
        f = open(afg_file, "r")
        s = f.read()

        lst = s.split()
        m = int(lst[lst.index("M:")+1])
        lst = lst[lst.index("IDS:")+1:]
        ids = map(int,lst[:m])

        s = s[s.find("#GRAPH_BEGIN#"):]
        s = s[:s.find("#GRAPH_END#\n")]
        s = s.replace("#GRAPH_BEGIN#", "")
        lst = s.split()
        lst.pop(0) #S:
        S = int(lst.pop(0))
        lst.pop(0) #T:
        T = int(lst.pop(0))
        lst.pop(0) #NV:
        NV = int(lst.pop(0))
        lst.pop(0) #NA:
        NA = int(lst.pop(0))
        lst = map(int, lst)
        A = []
        V = set([])
        for i in xrange(0,len(lst),3):
            u, v, i = lst[i:i+3]
            V.add(u)
            V.add(v)
            if i < m:
                A.append((u,v,ids[i]))
            else:
                A.append((u,v,i))
        V = sorted(V)
        return V, A, S, T

    @staticmethod
    def relabel(V, A, fv, fa = lambda x: x):
        V = map(fv, V)
        At = []
        for (u, v, i) in A:
            u, v = fv(u), fv(v)
            if u != v:
                At.append((u,v,fa(i)))
        return list(set(V)), list(set(At))

    @staticmethod
    def draw(svg_file, V, A, multigraph=True, showlabel=False, ignore=None, loss=None):
        if loss == None:
            loss = [i for (u,v,i) in A if type(i)!=int]
            loss.append(max([i for (u,v,i) in A if type(i)==int]+[-1]))
        try:
            from pygraphviz.agraph import AGraph
        except:
            print "Failed to load pygraphviz!"
            return
        g = AGraph(rankdir="LR", directed=True, bgcolor="white", text="black",
                   font_color="white", ranksep="1.0", nodesep="0.10", strict=not multigraph)
        #g.node_attr["shape"] = "point"
        g.node_attr["shape"] = "circle"
        g.node_attr["color"] = "black"
        g.node_attr["fontcolor"] = "black"
        g.node_attr["fontstyle"] = "bold"
        g.node_attr["penwidth"] = "2.0"

        lbls = list(set(i for (u,v,i) in A))
        lbls.sort()
        M = len(lbls)

        if multigraph:
            colors = uniquecolors(2*M)
            shuffle(colors)

            for (u,v,i) in A:
                if ignore != None and (u,v) in ignore: continue
                assert u != v
                if i in loss:
                    g.add_edge(u,v,color="black", penwidth=4)
                else:
                    lbl = str(i) if showlabel else ""
                    g.add_edge(u,v,color=colors[lbls.index(i)%len(colors)], penwidth="%d" % 4, label=lbl)

        else:
            colors = uniquecolors(M+1)
            shuffle(colors)

            links = {}
            for (u, v, i) in A:
                if (u,v) not in links:
                    links[u,v] = []
                links[u,v].append(i)

            for (ind, (u, v)) in enumerate(links):
                if ignore != None and (u,v) in ignore: continue
                assert u != v
                if M in links[u,v] or any(type(e) != int for e in links[u,v]):
                    g.add_edge(u,v,color="black", penwidth=4)
                if len(links[u,v]) != 1:
                    lbl = ",".join(map(str,links[u,v,])) if showlabel else ""
                    g.add_edge(u,v,color=colors[ind%len(colors)], penwidth="%d" % 4, label=lbl)

        g.draw(svg_file, format="svg", prog="dot")
        print "SVG file '%s' generated!" % svg_file
