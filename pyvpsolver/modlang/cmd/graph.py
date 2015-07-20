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

from ...vpsolver import VBP, AFG
from .. import utils
from .base import CmdBase


class CmdGraph(CmdBase):
    """Command for creating arc-flow graphs."""

    def _evalcmd(self, names, W, w, labels, bounds=None):
        """Evalutates CMD[arg1](*arg2)."""
        match = utils.parse_varlist(names)
        assert match is not None
        Vname, Aname = match

        if isinstance(W, dict):
            W = [W[k] for k in sorted(W)]
        if isinstance(w, dict):
            i0 = min(i for i, d in w)
            d0 = min(d for i, d in w)
            m = max(i for i, d in w)-i0+1
            p = max(d for i, d in w)-d0+1
            ww = [
                [w[i0+i, d0+d] for d in xrange(p)] for i in xrange(m)
            ]
            w = ww
        if isinstance(bounds, dict):
            bounds = [bounds[k] for k in sorted(bounds)]

        graph = self._generate_graph(W, w, labels, bounds)

        self._defs += utils.ampl_set(
            Vname, graph.V, self._sets, self._params
        )[0]
        self._defs += utils.ampl_set(
            Aname, graph.A, self._sets, self._params
        )[0]

    def _generate_graph(self, W, w, labels, bounds):
        """Generates an arc-flow graph."""
        m = len(w)
        ndims = len(W)
        if isinstance(bounds, list):
            b = bounds
        else:
            b = [
                min(W[d]/w[i][d] for d in xrange(ndims) if w[i][d] != 0)
                for i in xrange(m)
            ]
        instance = VBP(W, w, b, verbose=False)
        graph = AFG(instance, verbose=False).graph()
        graph.relabel(
            lambda u: u if isinstance(u, str) else str(u),
            lambda i: labels[i] if isinstance(i, int) and i < m else "LOSS"
        )
        return graph
