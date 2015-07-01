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

from .... import *
from utils import *
import re

class CmdGraph:
    def __init__(self, sets):
        self.zvars = []
        self.defs = ""
        self.sets = sets

    def __getitem__(self, arg1):
        return lambda *args: self.evalcmd(arg1, args)

    def evalcmd(self, arg1, args):
        lst = parse_varlist(arg1)
        Vname, Aname = lst

        W, w, labels, bounds = list(args)+[None]*(4-len(args))

        if type(W) == dict:
            W = [W[k] for k in sorted(W)]
        if type(w) == dict:
            i0 = min(i for i,d in w)
            d0 = min(d for i,d in w)
            m = max(i for i,d in w)-i0+1
            p = max(d for i,d in w)-d0+1
            ww = [None]*m
            for i in xrange(m):
                ww[i] = [w[i0+i,d0+d] for d in xrange(p)]
            w = ww
        if type(bounds) == dict:
            bounds = [bounds[k] for k in sorted(bounds)]

        graph = self.generate_graph(W, w, labels, bounds)

        self.defs += ampl_set(Vname, graph.V, self.sets)[0]
        self.defs += ampl_set(Aname, graph.A, self.sets)[0]

    def generate_graph(self, W, w, labels, bounds):
        m = len(w)
        if type(bounds) == list:
            b = bounds
        else:
            b = [0]*m
            for i in xrange(m):
                b[i] = min(W[d]/w[i][d] for d in xrange(len(w[i])) if w[i][d] != 0)

        instance = VBP(W, w, b, verbose=False)
        graph = AFG(instance, verbose=False).graph()
        graph.relabel(lambda u: u if type(u) != str else "%s"%u, lambda i: labels[i] if type(i)==int and i < m else "LOSS")
        return graph
