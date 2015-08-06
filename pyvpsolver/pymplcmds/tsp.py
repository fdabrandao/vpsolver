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

from .base import CmdBase
from ..model import Model
from ..modelutils import writemod

class CmdATSP_MTZ(CmdBase):
    """Command for creating Single Commodity Flow models for TSP."""

    def __init__(self, *args, **kwargs):
        CmdBase.__init__(self, *args, **kwargs)
        self._cnt = 0

    def _evalcmd(self, arg1, xvars, DL=False):
        """Evalutates CMD[arg1](*args)."""
        """
        Miller, Tucker and Zemlin (MTZ) (1960)
        var u{i in V: i != n}, >= 0;
        s.t. MTZ{(i,j) in A: i != n}:
            u[i]-u[j]+(n-1)*x[i,j] <= n-2;

        Desrochers and Laporte (1991)
        var u{i in V: i != n}, >= 0;
        s.t. DL{(i,j) in A: i != n}:
            u[i]-u[j]+(n-1)*x[i,j]+(n-3)*x[j,i] <= n-2;
        """
        assert arg1 is None
        self._cnt += 1
        prefix = "_tspmtz{0}_".format(self._cnt)

        A = sorted(xvars.keys())
        V = sorted(set(u for u, v in A) | set(v for u, v in A))
        start = V[0]

        declared_vars = set(xvars.values())

        def uvar(u):
            return "{0}u_{1}".format(prefix, u)

        model = Model()

        # var x{A}, binary;
        for var in declared_vars:
            model.add_var(name=var, lb=0, ub=1, vtype="B")

        # s.t. leave{i in V}: sum{(i,j) in A} x[i,j] = 1;
        # s.t. enter{j in V}: sum{(i,j) in A} x[i,j] = 1;
        for k in V:
            vars_in = [xvars[u, v] for u, v in A if v == k]
            vars_out = [xvars[u, v] for u, v in A if u == k]
            model.add_con(vars_in, "=", 1)
            model.add_con(vars_out, "=", 1)

        # var u{i in V: i != n}, >= 0;
        for u in V:
            if u != start:
                model.add_var(name=uvar(u), lb=0, vtype="C")

        # Miller, Tucker and Zemlin (MTZ) (1960)
        # s.t. MTZ{(i,j) in A: i != n}:
        #   u[i]-u[j]+(n-1)*x[i,j] <= n-2;

        # Desrochers and Laporte (1991)
        # s.t. DL{(i,j) in A: i != n}:
        #   u[i]-u[j]+(n-1)*x[i,j]+(n-3)*x[j,i] <= n-2;
        for (u, v) in A:
            if u == start or v == start:
                continue
            lincomb = [(uvar(u), 1), (uvar(v), -1), (xvars[u, v], len(V)-1)]
            if DL and (v, u) in A:
                lincomb.append((xvars[v, u], len(V)-3))
            model.add_con(lincomb, "<=", len(V)-2)

        def con_name(name):
            return prefix+name

        model.rename_cons(con_name)

        self._pyvars["_model"] += writemod.model2ampl(model, declared_vars)


class CmdATSP_Flow(CmdBase):
    """Command for creating Flow models for TSP."""

    def __init__(self, *args, **kwargs):
        CmdBase.__init__(self, *args, **kwargs)
        self._cnt = 0

    def _evalcmd(self, arg1, xvars, multi=False):
        """Evalutates CMD[arg1](*args)."""
        assert arg1 is None
        self._cnt += 1
        prefix = "_tspscf{0}_".format(self._cnt)

        A = sorted(xvars.keys())
        V = sorted(set(u for u, v in A) | set(v for u, v in A))
        start = V[0]

        declared_vars = set(xvars.values())

        model = Model()
        self._common(model, xvars, V, A, start)
        if not multi:
            self._single(model, xvars, V, A, start)
        else:
            self._multi(model, xvars, V, A, start)

        def var_name(name):
            if name in declared_vars:
                return name
            else:
                return prefix+name

        def con_name(name):
            return prefix+name

        model.rename_vars(var_name)
        model.rename_cons(con_name)

        self._pyvars["_model"] += writemod.model2ampl(model, declared_vars)

    def _common(self, model, xvars, V, A, start):
        """Adds assignment constraints."""
        # var x{A}, binary;
        for var in xvars.values():
            model.add_var(name=var, lb=0, ub=1, vtype="B")

        # s.t. leave{i in V}: sum{(i,j) in A} x[i,j] = 1;
        # s.t. enter{j in V}: sum{(i,j) in A} x[i,j] = 1;
        for k in V:
            vars_in = [xvars[u, v] for u, v in A if v == k]
            vars_out = [xvars[u, v] for u, v in A if u == k]
            model.add_con(vars_in, "=", 1)
            model.add_con(vars_out, "=", 1)

    def _single(self, model, xvars, V, A, start):
        """Add a Single Commodity Flow Model. Gavish and Graves (1978)

        var y{(i,j) in A}, >= 0;
        s.t. vub1{(i,j) in A: j == n}: y[i,j] <= (n-1) * x[i,j];
        s.t. vub2{(i,j) in A: j != n}: y[i,j] <= (n-2) * x[i,j];
        s.t. afg{i in V}:
          sum{(j,i) in A} y[j,i] - sum{(i,j) in A} y[i,j]
          = if i == n then n-1
            else -1;
        """

        def yvar(u, v):
            return "y_{0}_{1}".format(u, v)

        # var y{A}, >= 0;
        for (u, v) in A:
            model.add_var(name=yvar(u, v), lb=0, vtype="C")

        # s.t. vub1{(i,j) in A: j == n}: y[i,j] <= (n-1) * x[i,j];
        # s.t. vub2{(i,j) in A: j != n}: y[i,j] <= (n-2) * x[i,j];
        for (u, v) in A:
            if v == start:
                model.add_con(yvar(u, v), "<=", [(len(V)-1, xvars[u, v])])
            else:
                model.add_con(yvar(u, v), "<=", [(len(V)-2, xvars[u, v])])

        # s.t. flowcon{i in V}:
        # sum{(j,i) in A} y[j,i] - sum{(i,j) in A} y[i,j]
        # = if i == n then n-1
        #   else -1;
        for k in V:
            lincomb = [(yvar(u, v), 1) for u, v in A if v == k]
            lincomb += [(yvar(u, v), -1) for u, v in A if u == k]
            if k == start:
                model.add_con(lincomb, "=", len(V)-1)
            else:
                model.add_con(lincomb, "=", -1)

    def _multi(self, model, xvars, V, A, start):
        """Adds a Multi Commodity Flow Model. Wong (1980) and Claus (1984)

        var y{(i,j) in A, k in V: k != n}, >= 0, <= 1;
        s.t. vub{(i,j) in A, k in V: k != n}: y[i,j,k] <= x[i,j];
        s.t. flowcon{i in V, k in V: k != n}:
          sum{(j,i) in A} y[j,i,k]
          - sum{(i,j) in A} y[i,j,k]
          = if i == k then 1 else
            if i == n then -1 else
            0;
        """

        def yvar(u, v, k):
            return "y_{0}_{1}_{2}".format(u, v, k)

        # var y{A}, >= 0;
        for (u, v) in A:
            for k in V:
                if k != start:
                    model.add_var(name=yvar(u, v, k), lb=0, vtype="C")

        # s.t. vub{(i,j) in A, k in V: k != n}: y[i,j,k] <= x[i,j];
        for (u, v) in A:
            for k in V:
                if k != start:
                    model.add_con(yvar(u, v, k), "<=", xvars[u, v])

        #s.t. flowcon{i in V, k in V: k != n}:
        #  sum{(j,i) in A} y[j,i,k]
        #  - sum{(i,j) in A} y[i,j,k]
        #  = if i == k then 1 else
        #    if i == n then -1 else
        #    0;
        for i in V:
            for k in V:
                if k == start:
                    continue
                lincomb = [(yvar(u, v, k), 1) for u, v in A if v == i]
                lincomb += [(yvar(u, v, k), -1) for u, v in A if u == i]
                if i == k:
                    model.add_con(lincomb, "=", 1)
                elif i == start:
                    model.add_con(lincomb, "=", -1)
                else:
                    model.add_con(lincomb, "=", 0)
