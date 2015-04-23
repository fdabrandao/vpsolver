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

from writelp import write_lp
from writemps import write_mps
from collections import Iterable

inf = float('inf')

def transform_lincomb(left, sign, right):
    assert type(left) != int or type(right) != int
    lincomb = []
    def add_entry(x, sign = 1):
        assert type(x) in [str, tuple]
        if type(x) == str:
            lincomb.append((x, sign))
        if type(x) in [tuple, list]:
            assert len(x) == 2
            assert type(x[0]) == int or type(x[1]) == int
            assert type(x[0]) == str or type(x[1]) == str
            if type(x[0]) == str:
                lincomb.append((x[0], sign*x[1]))
            else:
                lincomb.append((x[1], sign*x[0]))

    rhs = 0

    if type(left) == int:
        rhs -= left
    elif type(left) == str:
        lincomb.append((left, 1))
    else:
        assert isinstance(left, Iterable)
        for x in left:
            if type(x) not in [float, int]:
                add_entry(x, 1)
            else:
                rhs -= x

    if type(right) == int:
        rhs += right
    elif type(right) == str:
        lincomb.append((right, -1))
    else:
        assert isinstance(right, Iterable)
        for x in right:
            if type(x) not in [float, int]:
                add_entry(x, -1)
            else:
                rhs -= x

    return (lincomb, sign, rhs)

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
            assert coef != inf and coef != -inf
        self.obj = lincomb

    def genConsName(self):
        name = "RC%x" % len(self.cons)
        assert name not in self.cons
        return name

    def genVarName(self):
        name = "RV%x" % len(self.vars)
        assert name not in self.vars
        return name

    def addVar(self, lb=None, ub=None, name=None, vtype="C"):
        if name == None: name = self.genVarName()
        assert lb != inf and ub != -inf
        if lb == -inf: lb = None
        if ub == inf: ub = None
        assert name not in self.vars
        assert vtype in ["C", "I"]
        self.vars[name] = {}
        self.vars[name]["lb"] = lb
        self.vars[name]["ub"] = ub
        self.vars[name]["vtype"] = vtype
        return name

    def addCons(self, left, sign, right, name=None):
        sign = sign[:1]
        assert sign in ["<", "=", ">"]
        lincomb, sign, rhs = transform_lincomb(left, sign, right)
        assert rhs != inf and rhs != -inf
        if lincomb == []:
            return
        if name == None:
            name = self.genConsName()
        for var, coef in lincomb:
            assert var in self.vars
            assert coef != inf and coef != -inf
        assert name not in self.cons
        self.cons[name] = (lincomb, sign, rhs)

    def writeLP(self, lp_file):
        write_lp(self, lp_file)

    def writeMPS(self, mps_file):
        write_mps(self, mps_file)

    def write(self, model_file):
        if model_file.endswith(".lp"):
            self.writeLP(model_file)
        elif model_file.endswith(".mps"):
            self.writeMPS(model_file)
        else:
            raise Exception("Invalid file extension!")


