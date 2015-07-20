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


class CmdSet(CmdBase):
    """Command for creating a new AMPL set."""

    def _evalcmd(self, name, values):
        """Evalutates CMD[arg1](*arg2)."""
        match = utils.parse_var(name)
        assert match is not None
        name = match

        self._defs += utils.ampl_set(name, values, self._sets, self._params)[0]


class CmdParam(CmdBase):
    """Command for creating a new AMPL parameter."""

    def _evalcmd(self, arg1, values, i0=None):
        """Evalutates CMD[arg1](*arg2)."""
        match = utils.parse_indexed(arg1)
        assert match is not None
        name, index = match

        if isinstance(values, list):
            if i0 is None:
                i0 = 0
            values = utils.list2dict(values, i0)
            if index is not None:
                assert len(index) == 1
                index = index[0]
        else:
            assert i0 is None

        if isinstance(values, dict):
            if index is not None:
                assert len(index) == 1
                index = index[0]
        else:
            assert i0 is None
            assert index is None

        if isinstance(values, dict):
            if index is None:
                index = "{0}_I".format(name)
            self._defs += utils.ampl_set(
                index, values.keys(), self._sets, self._params
            )[0]

        pdefs, pdata = utils.ampl_param(
            name, index, values, self._sets, self._params
        )
        self._defs += pdefs
        self._data += pdata
