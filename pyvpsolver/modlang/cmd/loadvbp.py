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

from ...vpsolver import VBP
from .. import utils
from .base import CmdBase


class CmdLoadVBP(CmdBase):
    """Command for loading VBP instances."""

    def _evalcmd(self, name, fname, i0=0, d0=0):
        """Evalutates CMD[arg1](*arg2)."""
        name, index = utils.parse_indexed(name)
        index_I, index_D = "%s_I" % name, "%s_D" % name
        if index is not None:
            assert 1 <= len(index) <= 2
            if len(index) == 2:
                index_I, index_D = index
            elif len(index) == 1:
                index_I = index[0]

        instance = VBP.fromFile(fname, verbose=False)

        W = {
            i0+i: instance.W[i]
            for i in xrange(instance.ndims)
        }
        w = {
            (i0+i, d0+d): instance.w[i][d]
            for i in xrange(instance.m)
            for d in xrange(instance.ndims)
        }
        b = {
            i0+i: instance.b[i]
            for i in xrange(instance.m)
        }

        assert "_%s" % name not in self._pyvars
        self._pyvars["_%s" % name] = instance
        sets, params = self._sets, self._params

        self._defs += "#BEGIN_DEFS: Instance[%s]\n" % name
        self._data += "#BEGIN_DATA: Instance[%s]\n" % name
        defs, data = utils.ampl_param(
            "%s_m" % name, None, instance.m, sets, params
        )
        self._defs += defs
        self._data += data
        defs, data = utils.ampl_param(
            "%s_n" % name, None, sum(instance.b), sets, params
        )
        self._defs += defs
        self._data += data
        defs, data = utils.ampl_param(
            "%s_p" % name, None, instance.ndims, sets, params
        )
        self._defs += defs
        self._data += data
        defs, data = utils.ampl_set(
            index_I, range(i0, i0+instance.m), sets, sets
        )
        self._defs += defs
        self._data += data
        defs, data = utils.ampl_set(
            index_D, range(i0, d0+instance.ndims), sets, params
        )
        self._defs += defs
        self._data += data
        defs, data = utils.ampl_param(
            "%s_W" % name, index_D, W, sets, params
        )
        self._defs += defs
        self._data += data
        defs, data = utils.ampl_param(
            "%s_b" % name, index_I, b, sets, params
        )
        self._defs += defs
        self._data += data
        defs, data = utils.ampl_param(
            "%s_w" % name, "%s,%s" % (index_I, index_D), w, sets, params
        )
        self._defs += defs
        self._data += data
        self._defs += "#END_DEFS: Instance[%s]\n" % name
        self._data += "#END_DATA: Instance[%s]\n" % name
