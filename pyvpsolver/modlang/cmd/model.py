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

from .. import utils
from .base import CmdBase
from ..utils import ampl_var, ampl_con


class CmdVar(CmdBase):
    """Command for creating a new AMPL variable."""

    def _evalcmd(self, name, typ="", lb=None, ub=None):
        """Evalutates CMD[name](*args)."""
        match = utils.parse_var(name)
        assert match is not None
        name = match
        self._pyvars["_model"] += ampl_var(name, typ, lb, ub)


class CmdCon(CmdBase):
    """Command for creating a new AMPL constraint."""

    def _evalcmd(self, name, lincomb, sign, rhs):
        """Evalutates CMD[name](*args)."""
        match = utils.parse_var(name)
        assert match is not None
        name = match
        self._pyvars["_model"] += ampl_con(name, lincomb, sign, rhs)


class CmdStmt(CmdBase):
    """Command for creating new AMPL statements."""

    def _evalcmd(self, arg1, statement):
        """Evalutates CMD(*args)."""
        assert arg1 is None
        self._pyvars["_model"] += statement
