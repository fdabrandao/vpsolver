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

from .... import *
from .utils import *


class CmdSet(object):
    def __init__(self, pyvars, sets, params):
        self.defs = ""
        self.data = ""
        self.pyvars = pyvars
        self.sets = sets
        self.params = params

    def __getitem__(self, name):
        return lambda *args, **kwargs: self.evalcmd(name, *args, **kwargs)

    def evalcmd(self, name, values):
        self.defs += ampl_set(name, values, self.pyvars)[0]


class CmdParam(object):
    def __init__(self, pyvars, sets, params):
        self.defs = ""
        self.data = ""
        self.pyvars = pyvars
        self.sets = sets
        self.params = params

    def __getitem__(self, arg1):
        return lambda *args, **kwargs: self.evalcmd(arg1, *args, **kwargs)

    def evalcmd(self, arg1, values, i0=None):
        name, index = parse_index(arg1)

        if type(values) == list:
            if i0 is None:
                i0 = 0
            values = list2dict(values, i0)
            if index is not None:
                assert len(index) == 1
                index = index[0]
        else:
            assert i0 is None

        if type(values) == dict:
            if index is not None:
                assert len(index) == 1
                index = index[0]
        else:
            assert i0 is None
            assert index is None

        if type(values) == dict:
            if index is None:
                index = "%s_I" % name
            self.defs += ampl_set(index, values.keys(), self.sets)[0]

        pdefs, pdata = ampl_param(name, index, values, self.params)
        self.defs += pdefs
        self.data += pdata
