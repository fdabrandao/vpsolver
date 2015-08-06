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
from .base import CmdBase
from .. import pymplutils
from ..model import Model
from ..modelutils import writemod


class CmdTSPScf(CmdBase):
    """Command for creating single commodity flow models for TSP."""

    def __init__(self, *args, **kwargs):
        CmdBase.__init__(self, *args, **kwargs)
        self._cnt = 0

    def _evalcmd(self, arg1, xvars):
        """Evalutates CMD[arg1](*args)."""
        """
        Single Commodity Flow Model
        Gavish and Graves (1978)

        set E;
        set V;
        var x{E}, binary;
        s.t. leave{i in V}: sum{(i,j) in E} x[i,j] = 1;
        s.t. enter{j in V}: sum{(i,j) in E} x[i,j] = 1;
        var y{(i,j) in E}, >= 0;
        s.t. vub1{(i,j) in E: j == n}: y[i,j] <= (n-1) * x[i,j];
        s.t. vub2{(i,j) in E: j != n}: y[i,j] <= (n-2) * x[i,j];
        s.t. afg{i in V}:
        sum{(j,i) in E} y[j,i] - sum{(i,j) in E} y[i,j] = if i == n then n-1
                                                          else -1;
        """
        assert arg1 is None
        self._cnt += 1
        prefix = "_tspscf{0}_".format(self._cnt)

        A = sorted(xvars.keys())
        V = sorted(set(u for u, v in A) | set(v for u, v in A))
        start = V[0]

        declared_vars = set(xvars.values())

        def yvar(u, v):
            return "{0}y_{1}_{2}".format(prefix, u, v)

        model = Model()

        # var x{E}, binary;
        for var in declared_vars:
            model.add_var(name=var, lb=0, ub=1, vtype="B")

        # var y{(i,j) in E}, >= 0;
        for (u, v) in A:
            model.add_var(name=yvar(u, v), lb=0, vtype="C")

        # s.t. leave{i in V}: sum{(i,j) in E} x[i,j] = 1;
        # s.t. enter{j in V}: sum{(i,j) in E} x[i,j] = 1;
        for k in V:
            vars_in = [xvars[u, v] for u, v in A if v == k]
            vars_out = [xvars[u, v] for u, v in A if u == k]
            model.add_con(vars_in, "=", 1)
            model.add_con(vars_out, "=", 1)

        # s.t. vub1{(i,j) in E: j == n}: y[i,j] <= (n-1) * x[i,j];
        # s.t. vub2{(i,j) in E: j != n}: y[i,j] <= (n-2) * x[i,j];
        for (u, v) in A:
            if v == start:
                model.add_con(yvar(u, v), "<=", [(len(V)-1, xvars[u, v])])
            else:
                model.add_con(yvar(u, v), "<=", [(len(V)-2, xvars[u, v])])

        # s.t. afg{i in V}:
        # sum{(j,i) in E} y[j,i] - sum{(i,j) in E} y[i,j]
        # = if i == n then n-1
        #   else -1;
        for k in V:
            lincomb = [(yvar(u, v), 1) for u, v in A if v == k]
            lincomb += [(yvar(u, v), -1) for u, v in A if u == k]
            if k == start:
                model.add_con(lincomb, "=", len(V)-1)
            else:
                model.add_con(lincomb, "=", -1)

        def con_name(name):
            return prefix+name

        model.rename_cons(con_name)

        self._pyvars["_model"] += writemod.model2ampl(
            model, declared_vars
        )
