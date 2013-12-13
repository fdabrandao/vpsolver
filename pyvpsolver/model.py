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

from writelp import write_lp

class Model:
    def __init__(self):
        self.vars = {}
        self.cons = {}
        self.obj = []
        self.objdir = "min"

    def setObj(self, objdir, lincomb):
        assert objdir in ["min", "max"]
        self.objdir = objdir
        for var, coef in lincomb: 
            assert var in self.vars
        self.obj = lincomb

    def genConsName(self):
        name = "RC%x" % len(self.cons)
        assert name not in self.cons
        return name
        
    def genVarName(self):
        name = "RV%x" % len(self.vars)
        assert name not in self.vars
        return name

    def addCons(self, lincomb, sign, rhs, name=None):        
        sign = sign[:1]
        assert sign in ["<", "=", ">"]
        if lincomb == []:
            return
        if name == None: 
            name = self.genConsName()
        for var, coef in lincomb:
            assert var in self.vars
        assert name not in self.cons
        self.cons[name] = (lincomb, sign, rhs)       
    
    def addVar(self, lb=None, ub=None, name=None):
        if name == None: name = self.genVarName()
        assert name not in self.vars
        self.vars[name] = {}
        if lb != None: self.vars[name]['lb'] = lb
        if ub != None: self.vars[name]['ub'] = ub
        return name 
        
    def writeLP(self, lp_file):
        write_lp(self, lp_file)

