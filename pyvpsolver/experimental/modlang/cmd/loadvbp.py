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
from utils import *


class CmdLoadVBP:
    def __init__(self, pyvars, sets, params):
        self.defs = ""
        self.data = ""
        self.pyvars = pyvars
        self.sets = sets
        self.params = params

    def __getitem__(self, name):
        return lambda *args: self.evalcmd(name, args)

    def evalcmd(self, name, args):
        name, index = parse_index(name)
        index_I, index_D = "%s_I" % name, "%s_D" % name
        if index is not None:
            assert 1 <= len(index) <= 2
            if len(index) == 2:
                index_I, index_D = index
            elif len(index) == 1:
                index_I = index[0]

        assert 1 <= len(args) <= 3
        fname = args[0]
        i0 = args[1] if len(args) > 1 else 0
        d0 = args[2] if len(args) > 2 else 0
        instance = VBP.fromFile(fname, verbose=False)

        W = {}
        for i in xrange(instance.ndims):
            W[i0+i] = instance.W[i]
        w = {}
        for i in xrange(instance.m):
            for d in xrange(instance.ndims):
                w[i0+i, d0+d] = instance.w[i][d]
        b = {}
        for i in xrange(instance.m):
            b[i0+i] = instance.b[i]

        self.pyvars["_%s" % name] = instance
        sets, params = self.sets, self.params

        self.defs += "#BEGIN_DEFS: Instance[%s]\n" % name
        self.data += "#BEGIN_DATA: Instance[%s]\n" % name
        defs, data = ampl_param("%s_m" % name, None, instance.m, params)
        self.defs += defs
        self.data += data
        defs, data = ampl_param("%s_n" % name, None, sum(instance.b), params)
        self.defs += defs
        self.data += data
        defs, data = ampl_param("%s_p" % name, None, instance.ndims, params)
        self.defs += defs
        self.data += data
        defs, data = ampl_set(index_I, range(i0, i0+instance.m), sets)
        self.defs += defs
        self.data += data
        defs, data = ampl_set(index_D, range(i0, d0+instance.ndims), sets)
        self.defs += defs
        self.data += data
        defs, data = ampl_param("%s_W" % name, index_D, W, params)
        self.defs += defs
        self.data += data
        defs, data = ampl_param("%s_b" % name, index_I, b, params)
        self.defs += defs
        self.data += data
        defs, data = ampl_param(
            "%s_w" % name, "%s,%s" % (index_I, index_D), w, params
        )
        self.defs += defs
        self.data += data
        self.defs += "#END_DEFS: Instance[%s]\n" % name
        self.data += "#END_DATA: Instance[%s]\n" % name
