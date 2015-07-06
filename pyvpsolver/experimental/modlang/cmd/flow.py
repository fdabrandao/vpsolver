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

import re
from .... import *
from ..writemod import *

RGX_VARNAME = "[a-zA-Z_][a-zA-Z0-9_]*"


def lincomb2str(lincomb):
    expr = ""
    for var, coef in lincomb:
        if abs(coef) != 1:
            if coef >= 0:
                expr += " + %g %s" % (coef, var)
            elif coef < 0:
                expr += " - %g %s" % (abs(coef), var)
        else:
            if coef >= 0:
                expr += " + %s" % (var)
            elif coef < 0:
                expr += " - %s" % (var)
    return expr


class CmdFlow:
    def __init__(self, pyvars, sets, params):
        self.zvars = []
        self.graphs = []
        self.prefixes = []
        self.pyvars = pyvars
        self.sets = sets
        self.params = params

    def __getitem__(self, zvar):
        return lambda *args, **kwargs: self.evalcmd(zvar, *args, **kwargs)

    def evalcmd(self, zvar, W=None, w=None, b=None, bounds=None):
        match = re.match("("+RGX_VARNAME+")(.*)", zvar)
        zvar, ztype = match.groups()
        ztype = ztype.replace(",", "")

        if type(W) == dict:
            W = [W[k] for k in sorted(W)]
        if type(w) == dict:
            i0 = min(i for i, d in w)
            d0 = min(d for i, d in w)
            m = max(i for i, d in w)-i0+1
            p = max(d for i, d in w)-d0+1
            ww = [None]*m
            for i in xrange(m):
                ww[i] = [w[i0+i, d0+d] for d in xrange(p)]
            w = ww
        if type(b) == dict:
            b = [b[k] for k in sorted(b)]
        if type(bounds) == dict:
            bounds = [bounds[k] for k in sorted(bounds)]

        graph, model, excluded_vars = self.generate_model(
            zvar, W, w, b, bounds, noobj=True
        )
        prefix = "_%s_" % zvar
        self.zvars.append(zvar)
        self.graphs.append(graph)
        self.prefixes.append(prefix)
        self.pyvars["_model"] += model2ampl(
            model, zvar, ztype, excluded_vars, prefix
        )

    def generate_model(self, zvar, W, w, b, bounds=None, noobj=False):
        m = len(w)
        bb = [0]*m
        bvars = []
        for i in xrange(m):
            if type(b[i]) == str:
                bb[i] = min(
                    W[d]/w[i][d] for d in xrange(len(w[i])) if w[i][d] != 0
                )
                if bounds is not None:
                    bb[i] = min(bb[i], bounds[i])
                bvars.append(b[i])
            else:
                bb[i] = b[i]

        instance = VBP(W, w, bb, verbose=False)
        graph = AFG(instance, verbose=False).graph()
        feedback = (graph.T, graph.S, "Z")
        graph.A.append(feedback)

        vnames = {}
        vnames[feedback] = zvar
        ub = {}
        varl, cons = graph.getFlowCons(vnames)
        assocs = graph.getAssocs(vnames)
        graph.names = vnames

        for i in xrange(m):
            if bounds is not None:
                for var in assocs[i]:
                    ub[var] = bounds[i]
            if type(b[i]) == str:
                varl.append(b[i])
                cons.append((assocs[i], "=", b[i]))
            else:
                if b[i] > 1:
                    cons.append((assocs[i], ">=", b[i]))
                else:
                    cons.append((assocs[i], "=", b[i]))

        model = Model()
        for var in varl:
            model.addVar(name=var, lb=0, ub=ub.get(var, None), vtype="I")
        for lincomb, sign, rhs in cons:
            model.addCons(lincomb, sign, rhs)

        if noobj is False:
            objlincomb = [(vnames[feedback], 1)]
            model.setObj("min", objlincomb)

        labels = {}
        for (u, v, i) in graph.A:
            if type(i) == int and i < m:
                labels[u, v, i] = ["i=%d" % (i+1)]
        graph.set_labels(labels)

        excluded_vars = bvars
        return graph, model, excluded_vars

    def extract(self, varvalues, verbose=False):
        lst_sol = []
        newvv = varvalues.copy()
        for zvar, graph, prefix in zip(self.zvars, self.graphs, self.prefixes):
            vv = {
                k.replace(prefix, "", 1): v
                for k, v in varvalues.items() if k.startswith(prefix)
            }
            for k in vv:
                del newvv[prefix+k]
            graph.set_flow(vv)
            sol = graph.extract_solution(graph.S, "<-", graph.T)
            lst_sol.append((zvar, varvalues.get(zvar, 0), sol))
            if verbose:
                print "Graph: %s (flow=%d)" % (zvar, varvalues.get(zvar, 0))
                print "\t", sol
        return lst_sol, newvv
