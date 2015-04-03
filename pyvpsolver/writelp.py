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

"""
LP format example:

Maximize
 obj: x1 + 2 x2 + 3 x3 + x4
Subject To
 c1: - x1 + x2 + x3 + 10 x4 <= 20
 c2: x1 - 3 x2 + x3 <= 30
 c3: x2 - 3.5 x4 = 0
Bounds
 0 <= x1 <= 40
 2 <= x4 <= 3
General
 x4
End
"""

from model import *

def lincomb2str(lincomb):
    expr = ""
    for var, coef in lincomb:
        if coef >= 0:
            expr += " + %g %s" % (coef, var)
        elif coef < 0:
            expr += " - %g %s" % (abs(coef), var) 
    return expr

def write_lp(model, filename):                   
    f = open(filename, "w")               
    
    ### objective
    
    if model.objdir == "min":
        print >>f, "Minimize"
    else:
        print >>f, "Maximize"
    
    obj = model.obj
    if obj == []:
        obj = [(var, 0) for var in model.vars]
    print >>f, "\tobjective:%s" % lincomb2str(obj)

    ### constraints            
            
    print >>f, "Subject To"          
        
    # demand constraints        
        
    for name in sorted(model.cons):    
        lincomb, sign, rhs = model.cons[name]
        if sign in [">","<"]:
            sign += "="
        print >>f, "\t%s:%s %s %s" % (name, lincomb2str(lincomb), sign, rhs)                   
    
    ### bounds

    bounds = []
    for name in sorted(model.vars):
        lb = model.vars[name].get('lb', None)
        ub = model.vars[name].get('ub', None)   
        if lb != None or ub != None:
            bounds.append((name, lb, ub))
        else:
            free.append(name)
    
    if bounds != []:
        print >>f, "Bounds"                
        for name, lb, ub in bounds:
            if lb != None and ub != None:
                print >>f, "\t%f <= %s <= %f" % (lb, name, ub)
            elif lb != None:
                print >>f, "\t%f <= %s" % (lb, name)
            elif ub != None:
                print >>f, "\t%s <= %f" % (name, ub)                        
    
    ### free variables
    
    print >>f, "General"
    for name in sorted(model.vars):
        if model.vars[name]["vtype"]=="I":
            print >>f, "\t%s" % name
    
    print >>f, "End"
    
    f.close()


