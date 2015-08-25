"""
This code is part of the Mathematical Modelling Toolbox PyMPL.

Copyright (C) 2015-2015, Filipe Brandao
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

from .base import SubModelBase
from ..model import Model, writemod
from .. import utils


def add_sos1(model, varl, ub=1, prefix=""):
    """Adds SOS1 constraints to model."""
    def yvar(i):
        return prefix+"y_{0}".format(i)

    for i in xrange(len(varl)):
        model.add_var(name=yvar(i), vtype="B")

    for i, var in enumerate(varl):
        model.add_con(var, "<=", (yvar(i), ub))

    model.add_con([yvar(i) for i in xrange(len(varl))], "=", 1)


def add_sos2(model, varl, ub=1, prefix=""):
    """Adds SOS2 constraints to model."""
    def yvar(i):
        return prefix+"y_{0}".format(i)

    for i in xrange(len(varl)-1):
        model.add_var(name=yvar(i), vtype="B")

    for i, var in enumerate(varl):
        if i == 0:
            model.add_con(var, "<=", (yvar(i), ub))
        elif i == len(varl)-1:
            model.add_con(var, "<=", (yvar(i-1), ub))
        else:
            model.add_con(var, "<=", [(yvar(i-1), ub), (yvar(i), ub)])

    model.add_con([yvar(i) for i in xrange(len(varl)-1)], "=", 1)


class SubSOS1Model(SubModelBase):
    """Command for creating SOS1 constraints."""

    def __init__(self, *args, **kwargs):
        SubModelBase.__init__(self, *args, **kwargs)
        self._cnt = 0

    def _evalcmd(self, arg1, varl, ub=1):
        """Evalutates CMD[arg1](*args)."""
        assert arg1 is None
        self._cnt += 1
        prefix = "_sos1{0}_".format(self._cnt)

        model = Model()
        for var in varl:
            model.add_var(name=var)
        add_sos1(model, varl, ub, prefix)
        model.rename_cons(lambda name: prefix+name)

        declared_vars = set(varl)
        self._pyvars["_model"] += writemod.model2ampl(model, declared_vars)


class SubSOS2Model(SubModelBase):
    """Command for creating SOS2 constraints."""

    def __init__(self, *args, **kwargs):
        SubModelBase.__init__(self, *args, **kwargs)
        self._cnt = 0

    def _evalcmd(self, arg1, varl, ub=1):
        """Evalutates CMD[arg1](*args)."""
        assert arg1 is None
        self._cnt += 1
        prefix = "_sos2{0}_".format(self._cnt)

        model = Model()
        for var in varl:
            model.add_var(name=var)
        add_sos2(model, varl, ub, prefix)
        model.rename_cons(lambda name: prefix+name)

        declared_vars = set(varl)
        self._pyvars["_model"] += writemod.model2ampl(model, declared_vars)


class SubPWLModel(SubModelBase):
    """Command for modeling Piecewise Linear Functions."""

    def __init__(self, *args, **kwargs):
        SubModelBase.__init__(self, *args, **kwargs)
        self._cnt = 0

    def _evalcmd(self, varnames, xyvalues):
        """Evalutates CMD[arg1](*args)."""
        match = utils.parse_symblist(varnames, allow_index="[]")
        assert match is not None
        xvar, yvar = match

        self._cnt += 1
        prefix = "_pwl{0}_".format(self._cnt)

        n = len(xyvalues)
        xvalues, yvalues = zip(*xyvalues)

        model = Model()
        # var x;
        model.add_var(name=xvar, lb=min(xvalues), ub=max(xvalues), vtype="C")
        # var y;
        model.add_var(name=yvar, lb=min(yvalues), ub=max(yvalues), vtype="C")
        def zvar(i):
            return prefix+"z_{0}".format(i)
        # var z{I}, >= 0;
        for i in xrange(n):
            model.add_var(name=zvar(i), lb=0, ub=1, vtype="C")
        # s.t. convexity: sum{i in I} z[i] = 1;
        model.add_con([zvar(i) for i in xrange(n)], "=", 1)
        # SOS2{z};
        add_sos2(model, [zvar(i) for i in xrange(n)], 1, prefix)
        # s.t. fix_x: x = sum{i in I} X[i] * z[i];
        # s.t. fix_y: y = sum{i in I} Y[i] * z[i];
        model.add_con([(zvar(i), xvalues[i]) for i in xrange(n)], "=", xvar)
        model.add_con([(zvar(i), yvalues[i]) for i in xrange(n)], "=", yvar)
        model.rename_cons(lambda name: prefix+name)

        self._pyvars["_model"] += writemod.model2ampl(model)
