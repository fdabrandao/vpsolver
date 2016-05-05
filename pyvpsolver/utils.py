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
from builtins import zip
from builtins import str
from builtins import map
from builtins import range
from builtins import object
from builtins import sorted

import re
import random

inf = float("inf")


def get_opt(key, content, default=None):
    """Extract an option from the content of a .vbp/.afg file."""
    matches = re.findall("\${0}\s*{{([^}}]+)}}".format(key), content)
    if matches == []:
        return default
    else:
        return matches[0]


def relabel_graph(V, A, fv, fa=lambda x: x):
    """Relabel an arc-flow graph."""
    V = set(map(fv, V))
    A = set((fv(u), fv(v), fa(i)) for (u, v, i) in A if fv(u) != fv(v))
    return list(V), list(A)


def sort_vertices(V, reverse=False):
    """Return the list of vertices sorted."""
    return sorted(V, key=lambda k: (repr(type(k)), k), reverse=reverse)


def sort_arcs(A, reverse=False):
    """Return the list of arcs sorted."""
    return sorted(
        A, key=lambda a: tuple((repr(type(k)), k) for k in a), reverse=reverse
    )


def draw_graph(svg_file, V, A, show_labels=False, ignore=None, back=None,
               loss=None, graph_attrs=None, verbose=False):
    """Draw an arc-flow graph in .svg format."""
    from pygraphviz.agraph import AGraph
    if ignore is None:
        ignore = []
    if back is None:
        back = []
    if loss is None:
        loss = []
    elif not isinstance(loss, (tuple, list)):
        loss = [loss]
    g = AGraph(
        rankdir="LR", directed=True, bgcolor="white",
        ranksep="1.0", nodesep="0.10",
        strict=False
    )
    if graph_attrs is not None:
        for attr, value in graph_attrs.items():
            g.graph_attr[attr] = value
    g.node_attr["shape"] = "ellipse"
    g.node_attr["color"] = "black"
    g.node_attr["fontcolor"] = "black"
    g.node_attr["penwidth"] = "2.0"

    lbls = sorted(
        set(i for (u, v, i) in A if i not in loss),
        key=lambda lbl: (repr(type(lbl)), lbl)
    )

    colors = Colors.uniquecolors(len(lbls)+1, v=0.5, p=0.0)
    # random.shuffle(colors)

    used = set()
    for (u, v, i) in A:
        if (u, v) in ignore:
            continue
        used.add(u)
        used.add(v)
        if (u, v) in back:
            u, v = v, u
            d = "back"
        else:
            d = "front"
        if i in loss:
            g.add_edge(u, v, color="black", style="dashed", penwidth=2, dir=d)
        else:
            lbl = str(i) if show_labels else ""
            color = colors[lbls.index(i) % len(colors)]
            g.add_edge(u, v, color=color, penwidth=2, label=lbl, dir=d)

    for v in V:
        if v not in used:
            g.add_node(v)

    g.draw(svg_file, format="svg", prog="dot")
    if verbose:
        print("SVG file '{0}' generated!".format(svg_file))


class Colors(object):
    """
    Finding N Distinct RGB Colors
    Based on code from StackOverflow: http://stackoverflow.com/a/2142206
    """

    @staticmethod
    def rgbcode(t):
        """Convert (r, g, b) tuples to hexadecimal."""
        r, g, b = t
        r = int(r*255)
        g = int(g*255)
        b = int(b*255)
        return "#{0:0>2x}{1:0>2x}{2:0>2x}".format(r, g, b)

    @staticmethod
    def rgbcolor(h, f, v, p):
        """Convert colors specified by h-value and f-value to RGB three-tuples.
        """
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
        """Generate a list of distinct colors, each of which is
        represented as an RGB three-tuple."""
        import math
        hues = list(360.0/n*i for i in range(n))
        hs = list(math.floor(hue/60) % 6 for hue in hues)
        fs = list((hue/60) % 1 for hue in hues)
        return [
            Colors.rgbcode(Colors.rgbcolor(h, f, v, p))
            for h, f in zip(hs, fs)
        ]
