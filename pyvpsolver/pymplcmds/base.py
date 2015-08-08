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


class CmdBase(object):
    """Command for creating a new AMPL set."""

    def __init__(self, cmd_name, pyvars, sets, params):
        self.cmd_name = cmd_name
        self._defs = ""
        self._data = ""
        self._pyvars = pyvars
        self._sets = sets
        self._params = params

    @property
    def defs(self):
        """Returns definitions."""
        return self._defs

    @property
    def data(self):
        """Returns data."""
        return self._data

    def clear(self):
        """Clears definitions and data."""
        self._defs = ""
        self._data = ""

    def __call__(self, *args, **kwargs):
        """Evalutates CMD()."""
        self._evalcmd(None, *args, **kwargs)

    def __getitem__(self, arg1):
        """Evalutates CMD[arg1]."""
        return lambda *args, **kwargs: self._evalcmd(arg1, *args, **kwargs)

    def _evalcmd(self, arg1, *args, **kwargs):
        """Evalutates CMD[arg1](*arg2)."""
        pass

    def separate(self, get_var_value):
        """Computes valid inequalities."""
        pass
