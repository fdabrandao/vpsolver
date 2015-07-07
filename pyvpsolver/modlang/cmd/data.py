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

from .utils import ampl_set, ampl_param
from .utils import parse_index, list2dict


class CmdSet(object):
    def __init__(self, pyvars, sets, params):
        self._defs = ""
        self._data = ""
        self._pyvars = pyvars
        self._sets = sets
        self._params = params

    @property
    def defs(self):
        return self._defs

    @property
    def data(self):
        return self._data

    def __getitem__(self, name):
        return lambda *args, **kwargs: self._evalcmd(name, *args, **kwargs)

    def _evalcmd(self, name, values):
        self._defs += ampl_set(name, values, self._sets)[0]


class CmdParam(object):
    def __init__(self, pyvars, sets, params):
        self._defs = ""
        self._data = ""
        self._pyvars = pyvars
        self._sets = sets
        self._params = params

    @property
    def defs(self):
        return self._defs

    @property
    def data(self):
        return self._data

    def __getitem__(self, arg1):
        return lambda *args, **kwargs: self._evalcmd(arg1, *args, **kwargs)

    def _evalcmd(self, arg1, values, i0=None):
        name, index = parse_index(arg1)

        if isinstance(values, list):
            if i0 is None:
                i0 = 0
            values = list2dict(values, i0)
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
                index = "%s_I" % name
            self._defs += ampl_set(index, values.keys(), self._sets)[0]

        pdefs, pdata = ampl_param(name, index, values, self._params)
        self._defs += pdefs
        self._data += pdata
