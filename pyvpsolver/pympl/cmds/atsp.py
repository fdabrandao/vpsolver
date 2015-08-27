"""
This code is part of the Mathematical Programming Toolbox PyMPL.

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
from builtins import zip

from .base import SubmodBase
from ..model import Model, writemod
from .atsputils import add_assign_constraints
from .atsputils import add_cut_variables
from .atsputils import add_mtz_constraints
from .atsputils import add_scf_constraints
from .atsputils import add_mcf_constraints
from .atsputils import tsp_cut_generator


class SubmodATSPMTZ(SubmodBase):
    """Command for creating MTZ constraints for TSP."""

    def __init__(self, *args, **kwargs):
        SubmodBase.__init__(self, *args, **kwargs)
        self._cnt = 0
        self._graph_lst = []
        self._cutvars_lst = []

    def _evalcmd(self, arg1, xvars, cuts=False, DL=False):
        """Evalutates CMD[arg1](*args)."""
        assert arg1 is None
        self._cnt += 1
        prefix = "_atspmtz{0}_".format(self._cnt)

        A = sorted(xvars.keys())
        V = sorted(set(u for u, v in A) | set(v for u, v in A))
        start = V[0]
        graph = (V, A, start)

        model = Model()
        add_assign_constraints(model, xvars, graph)
        add_mtz_constraints(model, xvars, graph, DL, prefix)
        if cuts:
            cutvars = add_cut_variables(model, xvars, graph, prefix)
            self._graph_lst.append(graph)
            self._cutvars_lst.append(cutvars)
        model.rename_cons(lambda name: prefix+name)

        declared_vars = set(xvars.values())
        self._pyvars["_model"] += writemod.model2ampl(model, declared_vars)

    def separate(self, get_var_value):
        """Computes valid inequalities for TSP submodels."""
        cuts = []
        for graph, cutvars in zip(self._graph_lst, self._cutvars_lst):
            cuts += tsp_cut_generator(graph, cutvars, get_var_value)
        return cuts


class SubmodATSPSCF(SubmodBase):
    """Command for creating Single-Commodity Flow Model models for TSP."""

    def __init__(self, *args, **kwargs):
        SubmodBase.__init__(self, *args, **kwargs)
        self._cnt = 0
        self._graph_lst = []
        self._cutvars_lst = []

    def _evalcmd(self, arg1, xvars, cuts=False):
        """Evalutates CMD[arg1](*args)."""
        assert arg1 is None
        self._cnt += 1
        prefix = "_atspscf{0}_".format(self._cnt)

        A = sorted(xvars.keys())
        V = sorted(set(u for u, v in A) | set(v for u, v in A))
        start = V[0]
        graph = (V, A, start)

        model = Model()
        add_assign_constraints(model, xvars, graph)
        add_scf_constraints(model, xvars, graph, prefix)
        if cuts:
            cutvars = add_cut_variables(model, xvars, graph, prefix)
            self._graph_lst.append(graph)
            self._cutvars_lst.append(cutvars)
        model.rename_cons(lambda name: prefix+name)

        declared_vars = set(xvars.values())
        self._pyvars["_model"] += writemod.model2ampl(model, declared_vars)

    def separate(self, get_var_value):
        """Computes valid inequalities for TSP submodels."""
        cuts = []
        for graph, cutvars in zip(self._graph_lst, self._cutvars_lst):
            cuts += tsp_cut_generator(graph, cutvars, get_var_value)
        return cuts


class SubmodATSPMCF(SubmodBase):
    """Command for creating Multi-Commodity Flow Model models for TSP."""

    def __init__(self, *args, **kwargs):
        SubmodBase.__init__(self, *args, **kwargs)
        self._cnt = 0
        self._graph_lst = []
        self._cutvars_lst = []

    def _evalcmd(self, arg1, xvars, cuts=False):
        """Evalutates CMD[arg1](*args)."""
        assert arg1 is None
        self._cnt += 1
        prefix = "_atspmcf{0}_".format(self._cnt)

        A = sorted(xvars.keys())
        V = sorted(set(u for u, v in A) | set(v for u, v in A))
        start = V[0]
        graph = (V, A, start)

        model = Model()
        add_assign_constraints(model, xvars, graph)
        add_mcf_constraints(model, xvars, graph, prefix)
        if cuts:
            cutvars = add_cut_variables(model, xvars, graph, prefix)
            self._graph_lst.append(graph)
            self._cutvars_lst.append(cutvars)
        model.rename_cons(lambda name: prefix+name)

        declared_vars = set(xvars.values())
        self._pyvars["_model"] += writemod.model2ampl(model, declared_vars)

    def separate(self, get_var_value):
        """Computes valid inequalities for TSP submodels."""
        cuts = []
        for graph, cutvars in zip(self._graph_lst, self._cutvars_lst):
            cuts += tsp_cut_generator(graph, cutvars, get_var_value)
        return cuts
