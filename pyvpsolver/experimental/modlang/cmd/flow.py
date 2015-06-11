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
from ..writemod import *
import re

rgx_varname = "[a-zA-Z_][a-zA-Z0-9_]*"

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
    def __init__(self, vtype="I"):
        self.zvars = []
        self.graphs = []
        self.prefixes = []
        self.vtype = vtype

    def parse_var_range(self, exp, m):
        match = re.match("("+rgx_varname+"){(\d+)?..(\d+)?}", exp)
        assert match != None
        vname, x, y = match.groups()
        assert x != None or x == y == None
        if x == None: x, y = 1, m
        elif y == None: x, y = int(x), int(x)+m-1
        else: x, y = int(x), int(y)
        return ["%s[%d]"%(vname,i) for i in xrange(x,y+1)]

    def __getitem__(self, zvar):
        return lambda *args: self.evalcmd(zvar, args)

    def evalcmd(self, zvar, args):
        match = re.match("("+rgx_varname+")(.*)", zvar)
        zvar, ztype = match.groups()
        ztype = ztype.replace(',','')

        if type(args[0]) in [list, tuple]:
            W, w, b, bounds = list(args)+[None]*(4-len(args))
            if type(b) == str:
                b = self.parse_var_range(b, len(w))
                assert len(b) == len(w)
        else:
            fname, b, bounds = list(args)+[None]*(3-len(args))
            if type(fname) == str:
                instance = VBP.fromFile(fname, verbose=False)
            else:
                assert isinstance(fname, VBP)
                instance = fname
            W, w = instance.W, instance.w
            if b == None:
                b = instance.b
                bounds = instance.b
            elif type(b) == str:
                b = self.parse_var_range(b, instance.m)
                assert len(b) == len(w)

        graph, model, excluded_vars = self.generate_model(zvar, W, w, b, bounds, noobj=True)
        prefix = "_"+zvar+"_"
        self.zvars.append(zvar)
        self.graphs.append(graph)
        self.prefixes.append(prefix)
        return model2gmpl(model, zvar, ztype, excluded_vars, prefix)

    def generate_model(self, zvar, W, w, b, bounds=None, noobj=False):
        m = len(w)
        bb = [0]*m
        bvars = []
        for i in xrange(m):
            if type(b[i]) == str:
                bb[i] = min(W[d]/w[i][d] for d in xrange(len(w[i])) if w[i][d] != 0)
                if bounds != None:
                    bb[i] = min(bb[i],bounds[i])
                bvars.append(b[i])
            else:
                bb[i] = b[i]

        instance = VBP(W, w, bb, verbose=False)
        graph = AFG(instance, verbose=False).graph()
        feedback = (graph.T, graph.S, 'Z')
        graph.A.append(feedback)

        vnames = {}
        vnames[feedback] = zvar
        ub = {}
        varl, cons = graph.getFlowCons(vnames)
        assocs = graph.getAssocs(vnames)
        graph.names = vnames

        for i in xrange(m):
            if bounds != None:
                for var in assocs[i]:
                    ub[var] = bounds[i]
            if type(b[i]) == str:
                varl.append(b[i])
                cons.append((assocs[i],"=",b[i]))
            else:
                if b[i] > 1:
                    cons.append((assocs[i],">=",b[i]))
                else:
                    cons.append((assocs[i],"=",b[i]))

        model = Model()
        for var in varl:
            model.addVar(name=var, lb=0, ub=ub.get(var,None), vtype=self.vtype)
        for lincomb, sign, rhs in cons:
            model.addCons(lincomb, sign, rhs)

        if noobj == False:
            objlincomb = [(vnames[feedback], 1)]
            model.setObj("min", objlincomb)

        labels = {}
        for (u,v,i) in graph.A:
            if type(i) == int and i < m:
                labels[u,v,i] = ["i=%d"%(i+1)]
        graph.set_labels(labels)

        excluded_vars=bvars
        return graph, model, excluded_vars

    def extract(self, varvalues, verbose=False):
        lst_sol = []
        newvv = varvalues.copy()
        for i in xrange(len(self.zvars)):
            zvar, graph, prefix = self.zvars[i], self.graphs[i], self.prefixes[i]
            vv = {k.replace(prefix,'',1):v for k,v in varvalues.items() if k.startswith(prefix)}
            for k in vv:
                del newvv[prefix+k]
            graph.set_flow(vv)
            sol = graph.extract_solution(graph.S, '<-', graph.T)
            lst_sol.append((zvar, varvalues.get(zvar,0), sol))
            if verbose:
                print 'Graph: %s (flow=%d)' % (zvar, varvalues.get(zvar,0))
                print '\t', sol
        return lst_sol, newvv
