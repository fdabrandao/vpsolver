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
from .. import pymplutils
from .. import utils


class CmdSet(CmdBase):
    """Command for creating a new AMPL set."""

    def _evalcmd(self, name, values):
        """Evalutates CMD[name](*args)."""
        match = pymplutils.parse_symbname(name)
        assert match is not None
        name = match

        self._defs += pymplutils.ampl_set(
            name, values, self._sets, self._params
        )[0]


class CmdParam(CmdBase):
    """Command for creating a new AMPL parameter."""

    def _evalcmd(self, arg1, values, i0=None):
        """Evalutates CMD[arg1](*args)."""
        match = pymplutils.parse_indexed(arg1, "{}")
        assert match is not None
        name, index = match

        if isinstance(values, list):
            if i0 is None:
                i0 = 0
            values = utils.list2dict(values, i0)
            if index is not None:
                assert len(index) == 1
                index = index[0]
        elif isinstance(values, dict):
            assert i0 is None
            if index is not None:
                assert len(index) == 1
                index = index[0]
        else:
            assert i0 is None
            assert index is None

        if isinstance(values, dict):
            if index is None:
                index = "{0}_I".format(name)
            self._defs += pymplutils.ampl_set(
                index, values.keys(), self._sets, self._params
            )[0]

        pdefs, pdata = pymplutils.ampl_param(
            name, index, values, self._sets, self._params
        )
        self._defs += pdefs
        self._data += pdata


class CmdVar(CmdBase):
    """Command for creating a new AMPL variable."""

    def _evalcmd(self, name, typ="", lb=None, ub=None):
        """Evalutates CMD[name](*args)."""
        match = pymplutils.parse_symbname(name)
        assert match is not None
        name = match
        self._pyvars["_model"] += pymplutils.ampl_var(name, typ, lb, ub)


class CmdCon(CmdBase):
    """Command for creating a new AMPL constraint."""

    def _evalcmd(self, name, left, sign, right):
        """Evalutates CMD[name](*args)."""
        match = pymplutils.parse_symbname(name)
        assert match is not None
        name = match
        lincomb, sign, rhs = utils.linear_constraint(left, sign, right)
        self._pyvars["_model"] += pymplutils.ampl_con(name, lincomb, sign, rhs)


class CmdStmt(CmdBase):
    """Command for creating new AMPL statements."""

    def _evalcmd(self, arg1, statement):
        """Evalutates CMD(*args)."""
        assert arg1 is None
        self._pyvars["_model"] += str(statement)
