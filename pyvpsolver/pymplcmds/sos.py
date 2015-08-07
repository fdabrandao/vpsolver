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


class CmdSOS1Model(CmdBase):
    """Command for creating SOS1 constraints."""

    def __init__(self, *args, **kwargs):
        CmdBase.__init__(self, *args, **kwargs)
        self._cnt = 0

    def _evalcmd(self, arg1, varl, ub=1):
        """Evalutates CMD[arg1](*args)."""
        assert arg1 is None
        self._cnt += 1
        prefix = "_sos1{0}_".format(self._cnt)

        def yvar(i):
            return prefix+"y_{0}".format(i)

        model = Model()

        for i, var in enumerate(varl):
            model.add_var(name=var)
            model.add_var(name=yvar(i), lb=0, ub=1, vtype="B")

        for i, var in enumerate(varl):
            model.add_con(var, "<=", [(yvar(i), ub)])

        model.add_con([yvar(i) for i in xrange(len(varl))], "=", 1)

        declared_vars = set(varl)
        model.rename_cons(lambda name: prefix+name)
        self._pyvars["_model"] += writemod.model2ampl(model, declared_vars)


class CmdSOS2Model(CmdBase):
    """Command for creating SOS2 constraints."""

    def __init__(self, *args, **kwargs):
        CmdBase.__init__(self, *args, **kwargs)
        self._cnt = 0

    def _evalcmd(self, arg1, varl, ub=1):
        """Evalutates CMD[arg1](*args)."""
        assert arg1 is None
        self._cnt += 1
        prefix = "_sos2{0}_".format(self._cnt)

        def yvar(i):
            return prefix+"y_{0}".format(i)

        model = Model()

        for var in varl:
            model.add_var(name=var)

        for i in xrange(len(varl)-1):
            model.add_var(name=yvar(i), lb=0, ub=1, vtype="B")

        for i, var in enumerate(varl):
            if i == 0:
                model.add_con(var, "<=", [(yvar(i), ub)])
            elif i == len(varl)-1:
                model.add_con(var, "<=", [(yvar(i-1), ub)])
            else:
                model.add_con(var, "<=", [(yvar(i-1), ub), (yvar(i), ub)])

        model.add_con([yvar(i) for i in xrange(len(varl)-1)], "=", 1)

        declared_vars = set(varl)
        model.rename_cons(lambda name: prefix+name)
        self._pyvars["_model"] += writemod.model2ampl(model, declared_vars)
