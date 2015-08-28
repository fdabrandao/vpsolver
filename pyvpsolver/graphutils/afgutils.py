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
from builtins import str
from builtins import map
from builtins import range
from builtins import object

import random


class AFGUtils(object):
    """Tools for manipulating arc-flow graphs."""

    @staticmethod
    def read_graph(afg_file):
        """Reads graphs from .afg files."""
        f = open(afg_file, "r")
        s = f.read()

        lst = s.split()
        m = int(lst[lst.index("M:")+1])
        lst = lst[lst.index("IDS:")+1:]
        ids = list(map(int, lst[:m]))

        s = s[s.find("#GRAPH_BEGIN#"):]
        s = s[:s.find("#GRAPH_END#\n")]
        s = s.replace("#GRAPH_BEGIN#", "")
        lst = s.split()
        lst.pop(0)  # ignore "S:"
        S = int(lst.pop(0))
        lst.pop(0)  # ignore "T:"
        T = int(lst.pop(0))
        lst.pop(0)  # ignore "NV:"
        NV = int(lst.pop(0))
        lst.pop(0)  # ignore "NA:"
        NA = int(lst.pop(0))
        lst = list(map(int, lst))
        A = []
        V = set([])
        for i in range(0, len(lst), 3):
            u, v, i = lst[i:i+3]
            V.add(u)
            V.add(v)
            if i < m:
                A.append((u, v, ids[i]))
            else:
                A.append((u, v, i))
        V = sorted(V)
        return V, A, S, T

    @staticmethod
    def relabel(V, A, fv, fa=lambda x: x):
        """Relabels graphs."""
        V = list(map(fv, V))
        At = []
        for (u, v, i) in A:
            u, v = fv(u), fv(v)
            if u != v:
                At.append((u, v, fa(i)))
        return list(set(V)), list(set(At))

    @staticmethod
    def draw(
            svg_file, V, A, multigraph=True, showlabel=False, ignore=None,
            loss=None, verbose=None):
        """Draws arc-flow graphs in .svg format."""
        from pygraphviz.agraph import AGraph
        if loss is None:
            loss = [i for (u, v, i) in A if not isinstance(i, int)]
            loss.append(max([i for (u, v, i) in A if isinstance(i, int)]+[-1]))
        g = AGraph(
            rankdir="LR", directed=True, bgcolor="white", text="black",
            font_color="white", ranksep="1.0", nodesep="0.10",
            strict=not multigraph
        )
        # g.node_attr["shape"] = "point"
        g.node_attr["shape"] = "circle"
        g.node_attr["color"] = "black"
        g.node_attr["fontcolor"] = "black"
        g.node_attr["fontstyle"] = "bold"
        g.node_attr["penwidth"] = "2.0"

        lbls = list(set(i for (u, v, i) in A))
        lbls.sort()
        M = len(lbls)

        if multigraph:
            colors = Colors.uniquecolors(2*M)
            random.shuffle(colors)

            for (u, v, i) in A:
                if ignore is not None and (u, v) in ignore:
                    continue
                assert u != v
                if i in loss:
                    g.add_edge(u, v, color="black", penwidth=4)
                else:
                    lbl = str(i) if showlabel else ""
                    g.add_edge(
                        u, v,
                        color=colors[lbls.index(i) % len(colors)],
                        penwidth="{0}".format(4),
                        label=lbl
                    )

        else:
            colors = Colors.uniquecolors(M+1)
            random.shuffle(colors)

            links = {}
            for (u, v, i) in A:
                if (u, v) not in links:
                    links[u, v] = []
                links[u, v].append(i)

            for (ind, (u, v)) in enumerate(links):
                if ignore is not None and (u, v) in ignore:
                    continue
                assert u != v
                if (
                    M in links[u, v] or
                    any(not isinstance(e, int) for e in links[u, v])
                ):
                    g.add_edge(u, v, color="black", penwidth=4)
                if len(links[u, v]) != 1:
                    lbl = ",".join(map(str, links[u, v])) if showlabel else ""
                    g.add_edge(
                        u, v,
                        color=colors[ind % len(colors)],
                        penwidth="{0}".format(4),
                        label=lbl
                    )

        g.draw(svg_file, format="svg", prog="dot")
        print("SVG file '{0}' generated!".format(svg_file))


class Colors(object):
    """
    Finding N Distinct RGB Colors
    Based on code from StackOverflow: http://stackoverflow.com/a/2142206
    """

    @staticmethod
    def rgbcode(t):
        """Converts (r, g, b) tuples to hexadecimal."""
        r, g, b = t
        r = int(r*255)
        g = int(g*255)
        b = int(b*255)
        return "#{0:0>2x}{1:0>2x}{2:0>2x}".format(r, g, b)

    @staticmethod
    def rgbcolor(h, f, v, p):
        """Converts colors specified by h-value and f-value to
        RGB three-tuples."""
        # q = 1 - f
        # t = f
        if h == 0:
            return v, f, p
        elif h == 1:
            return 1 - f, v, p
        elif h == 2:
            return p, v, f
        elif h == 3:
            return p, 1 - f, v
        elif h == 4:
            return f, p, v
        elif h == 5:
            return v, p, 1 - f

    @staticmethod
    def uniquecolors(n, v=0.5, p=0.0):
        """Computes a list of distinct colors, ecah of which is
        represented as an RGB three-tuple."""
        import math
        hues = (360.0/n*i for i in range(n))
        hs = (math.floor(hue/60) % 6 for hue in hues)
        fs = (hue/60-math.floor(hue/60) for hue in hues)
        return [
            Colors.rgbcode(Colors.rgbcolor(h, f, v, p))
            for h, f in zip(hs, fs)
        ]
