"""
This code is part of the Arc-flow Vector Packing Solver (VPSolver).

Copyright (C) 2013, Filipe Brandao
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

from vpsolver import *
import sys

def solve_mvbp(Ws, ws, b, cost, svg_file="", log_file="", verbose=False, script="vpsolver_gurobi.sh"):
    """
    Solves multiple-choice vector bin packing instances using the method
    proposed in Brandao, F. and Pedroso, J. P. (2013). Multiple-choice Vector Bin Packing:
    Arc-flow Formulation with Graph Compression. Technical Report DCC-2013-13, 
    Faculdade de Ciencias da Universidade do Porto, Universidade do Porto, Portugal.
    """
    assert svg_file=="" or svg_file.endswith(".svg")
    nbtypes = len(Ws)
    ndims = len(Ws[0])
    
    ww = []
    bb = []
    itlabel = []
    for i in xrange(len(ws)):
        for j in xrange(len(ws[i])):
            itlabel.append((i,j))
            ww.append(ws[i][j])
            bb.append(b[i])            
            
    instances = [None] * nbtypes
    graphs = [None] * nbtypes
    Ss, Ts = [None] * nbtypes, [None] * nbtypes
    for i in xrange(nbtypes):        
        bbi = bb[:]
        for j in xrange(len(ww)):
            if any(a > b for a,b in zip(ww[j], Ws[i])):
                bbi[j] = 0
                continue
        symb = "G%d" % i
        instances[i] = VBP(Ws[i], ww, bbi, verbose=False)
        graphs[i] = AFG(instances[i], verbose=False).graph()
        graphs[i].relabel(lambda u: "%s%s" % (symb,u))
        Ss[i] = symb+"S"
        Ts[i] = symb+"T"
        if svg_file.endswith(".svg"): 
            graphs[i].draw(svg_file.replace(".svg", "%d.svg" % i))

    V = sum([g.V for g in graphs], [])
    A = sum([g.A for g in graphs], [])
    V += ['S', 'T']
    A += [('S', s, 'L') for s in Ss]
    A += [(t, 'T', 'L') for t in Ts]
    A += [('T', 'S', 'L')]       
    
    graph = AFGraph(V, A, 'S', 'T')
    if svg_file.endswith(".svg"):
        graph.draw(svg_file, ignore=[('T','S')])

    adj = {u:[] for u in V}
    for (u,v,i) in A:
        adj[v].append((u,i))
    S, T = 'S', 'T'
                       
    newlbl = {}        
    def compress(u):
        if u == S: return [0]*ndims
        if u in newlbl: return newlbl[u]
        def itemw(lbl):
            if type(lbl) == int and lbl < len(ww):
                return ww[lbl]
            else:
                return [0]*ndims                
        lbl = [0]*ndims
        for v,i in adj[u]:
            wi = itemw(i)
            vlbl = compress(v)
            for d in xrange(ndims):
                lbl[d] = max(lbl[d], vlbl[d]+wi[d])
        newlbl[u] = lbl
        return lbl

    compress(T)    
    revlbl = {tuple(x): [] for x in newlbl.values()}
    for u in newlbl:
        if u not in Ts+[T]:
            revlbl[tuple(newlbl[u])].append(u)

    revlbl2 = {}
    for i,x in enumerate(sorted(revlbl)):
        if sum(x) != 0:
            revlbl2["V%d"%i] = revlbl[x]
        else:
            revlbl2[S] = revlbl[x] 

    vlbl = {}
    for lbl in revlbl2:
        for v in revlbl2[lbl]:
            vlbl[v] = lbl

    assert set([v for v in V if v not in vlbl]) == set([S,T]+Ts)

    nv1, na1 = len(V), len(A)
    #print "#V1: %d #A1: %d" % (nv1, na1)
           
    graph.relabel(lambda u: vlbl.get(u,u))
    V, A = graph.V, graph.A

    nv2, na2 = len(V), len(A)
    #print "#V2: %d #A2: %d" % (nv2, na2)       

    if svg_file.endswith(".svg"):
        graph.draw(svg_file.replace(".svg", ".final.svg"), ignore=[('T','S')])    

    # remove redudant parallel arcs
    At = []
    used = set()
    for (u,v,i) in A:
        if isinstance(i, int) and i < len(itlabel):
            k = (u,v,itlabel[i][0])
        else:
            k = (u,v,'L')
        if k not in used:
            At.append((u,v,i))
            used.add(k)

    A = At
    nv3, na3 = len(V), len(A)
    #print "#V3: %d #A3: %d" % (nv3, na3)         

    #print "#V3/#V1: %.2f #A3/#A1: %.1f" % (nv3/float(nv1), na3/float(na1))

    varl, cons = graph.getFlowCons()

    assocs = graph.getAssocs()
    for i in xrange(len(b)):
        lincomb = [(var, 1) for it, (j, t) in enumerate(itlabel) if j==i for var in assocs[it]]    
        #cons.append((lincomb,">=",b[i]))      
        if b[i] > 1:
            cons.append((lincomb,">=",b[i]))      
        else:
            cons.append((lincomb,"=",b[i]))

    model = Model()        

    ub = {}        
    for i in xrange(len(b)):
        for var in assocs[i]:
            ub[var] = b[i]

    for var in varl:
        #model.addVar(name=var, lb=0, vtype="I")
        model.addVar(name=var, lb=0, ub=ub.get(var,None), vtype="I")

    for lincomb, sign, rhs in cons:
        model.addCons(lincomb, sign, rhs)
                                                
    lincomb = [(graph.vname(Ts[i], 'T', 'L'), cost[i]) for i in xrange(nbtypes)]
    model.setObj("min", lincomb)

    model_file = VPSolver.new_tmp_file(".lp")  
    model.write(model_file)
    out, varvalues = VPSolver.script_wsol(script, model_file, verbose=verbose)
    os.remove(model_file)
    
    if log_file != "":
        f = open(log_file, "w")
        print >>f, "#V1: %d #A1: %d" % (nv1, na1)
        print >>f, "#V2: %d #A2: %d" % (nv2, na2)
        print >>f, "#V3: %d #A3: %d" % (nv3, na3)
        print >>f, "#V3/#V1: %.2f #A3/#A1: %.1f" % (nv3/float(nv1), na3/float(na1))
        print >>f, out
        f.close()
    
    labels = {}
    for (u,v,i) in A:
        if type(i) == int and i < len(itlabel):        
            labels[u,v,i] = [itlabel[i]]              
    
    lst_sol = []
    graph.set_flow(varvalues)
    graph.set_labels(labels)
    for i in xrange(nbtypes):
        lst_sol.append(graph.extract_solution('S', '<-', Ts[i]))            
    
    assert graph.validate_solution(lst_sol, nbtypes, ndims, Ws, ws, b)
    
    c1 = sum(sum(r for r, patt in lst_sol[i])*cost[i] for i in xrange(nbtypes))
    c2 = sum(varvalues.get(graph.vname(Ts[i], 'T', 'L'),0) * cost[i] for i in xrange(nbtypes))
    assert c1 == c2
    
    return c1, lst_sol

def solve_vbp(W, w, b, svg_file="", verbose=False, script="vpsolver_gurobi.sh"):
    assert svg_file=="" or svg_file.endswith(".svg")
    instance = VBP(W, w, b, verbose=False)
    if svg_file == "":           
        out, (obj, sol) = VPSolver.script(script, instance, verbose=verbose)    
    else:
        afg = AFG(instance, verbose=verbose)
        afg.graph().draw(svg_file)
        mps_model = MPS(afg, verbose=verbose)
        out, (obj, sol) = VPSolver.script(script, mps_model, afg, verbose=verbose)
    return obj, sol

def print_solution_mvbp(obj, lst_sol, f=sys.stdout):
    print >>f, "Objective:", obj
    for i, sol in enumerate(lst_sol):
        cnt = sum(m for m,p in sol)
        print >>f, "Bins of type %d: %d" % (i+1, cnt)
        for mult, patt in sol:
            print >>f, "%d x [%s]" % (mult, ", ".join(["i=%d opt=%d" % (it+1, opt+1) for it, opt in patt]))    
    
def print_solution_vbp(obj, sol, f=sys.stdout):    
    print >>f, "Objective:", obj
    for mult, patt in sol:
        print >>f, "%d x [%s]" % (mult, ", ".join(["i=%d" % (it+1) for it in patt]))
    
    
