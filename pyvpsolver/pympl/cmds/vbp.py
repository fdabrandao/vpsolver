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
from __future__ import division
from builtins import zip
from builtins import str
from builtins import range
import six

import re
from .base import CmdBase, SubmodBase
from ..model import Model, writemod
from .. import utils


class CmdVBPLoad(CmdBase):
    """Command for loading VBP instances."""

    def _evalcmd(self, name, fname, i0=0, d0=0):
        """Evalutates CMD[name](*args)."""
        from pyvpsolver import VBP
        name, index = utils.parse_indexed(name, "{}")
        index_I = "{0}_I".format(name)
        index_D = "{0}_D".format(name)
        if index is not None:
            assert 1 <= len(index) <= 2
            if len(index) == 2:
                index_I, index_D = index
            elif len(index) == 1:
                index_I = index[0]

        instance = VBP.from_file(fname, verbose=False)

        W = {
            i0+i: instance.W[i]
            for i in range(instance.ndims)
        }
        w = {
            (i0+i, d0+d): instance.w[i][d]
            for i in range(instance.m)
            for d in range(instance.ndims)
        }
        b = {
            i0+i: instance.b[i]
            for i in range(instance.m)
        }

        assert "_{0}".format(name.lstrip("^")) not in self._pyvars
        self._pyvars["_{0}".format(name.lstrip("^"))] = instance
        sets, params = self._sets, self._params

        defs, data = "", ""

        pdefs, pdata = utils.ampl_param(
            "{0}_m".format(name), None, instance.m, sets, params
        )
        defs += pdefs
        data += pdata

        pdefs, pdata = utils.ampl_param(
            "{0}_n".format(name), None, sum(instance.b), sets, params
        )
        defs += pdefs
        data += pdata

        pdefs, pdata = utils.ampl_param(
            "{0}_p".format(name), None, instance.ndims, sets, params
        )
        defs += pdefs
        data += pdata

        sdefs, sdata = utils.ampl_set(
            index_I, list(range(i0, i0+instance.m)), sets, sets
        )
        defs += sdefs
        data += sdata

        sdefs, sdata = utils.ampl_set(
            index_D, list(range(d0, d0+instance.ndims)), sets, params
        )
        defs += sdefs
        data += sdata

        pdefs, pdata = utils.ampl_param(
            "{0}_W".format(name), index_D, W, sets, params
        )
        defs += pdefs
        data += pdata

        pdefs, pdata = utils.ampl_param(
            "{0}_b".format(name), index_I, b, sets, params
        )
        defs += pdefs
        data += pdata

        pdefs, pdata = utils.ampl_param(
            "{0}_w".format(name),
            "{0},{1}".format(index_I, index_D),
            w, sets, params
        )
        defs += pdefs
        data += pdata

        self._pyvars["_defs"] += defs
        self._pyvars["_data"] += "#BEGIN_DATA: Instance[{0}]\n".format(name)
        self._pyvars["_data"] += data
        self._pyvars["_data"] += "#END_DATA: Instance[{0}]\n".format(name)


class CmdVBPGraph(CmdBase):
    """Command for creating arc-flow graphs."""

    def _evalcmd(self, names, W, w, labels, bounds=None):
        """Evalutates CMD[names](*args)."""
        match = utils.parse_symblist(names)
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
                [w[i0+i, d0+d] for d in range(p)] for i in range(m)
            ]
            w = ww
        if isinstance(bounds, dict):
            bounds = [bounds[k] for k in sorted(bounds)]

        graph = self._generate_graph(W, w, labels, bounds)

        defs = ""
        defs += utils.ampl_set(
            Vname, graph.V, self._sets, self._params
        )[0]
        defs += utils.ampl_set(
            Aname, graph.A, self._sets, self._params
        )[0]
        self._pyvars["_defs"] += defs

    def _generate_graph(self, W, w, labels, bounds):
        """Generates an arc-flow graph."""
        from pyvpsolver import VBP, AFG
        m = len(w)
        ndims = len(W)
        if isinstance(bounds, list):
            b = bounds
        else:
            b = [
                min(W[d]//w[i][d]) for d in range(ndims) if w[i][d] != 0
                for i in range(m)
            ]
        instance = VBP(W, w, b, verbose=False)
        graph = AFG(instance, verbose=False).graph()
        graph.relabel(
            lambda u: u if isinstance(u, six.string_types) else str(u),
            lambda i: labels[i] if isinstance(i, int) and i < m else "LOSS"
        )
        return graph


class SubmodVBPFlow(SubmodBase):
    """Command for creating arc-flow models."""

    def __init__(self, *args, **kwargs):
        SubmodBase.__init__(self, *args, **kwargs)
        self._zvars = []
        self._models = []
        self._graphs = []
        self._prefixes = []

    def _evalcmd(self, zvar, W, w, b, bounds=None):
        """Evalutates CMD[zvar](*args)."""
        match = utils.parse_symbname(zvar, allow_index="[]")
        assert match is not None
        zvar = match

        if isinstance(W, dict):
            W = [W[k] for k in sorted(W)]
        if isinstance(w, dict):
            i0 = min(i for i, d in w)
            d0 = min(d for i, d in w)
            m = max(i for i, d in w)-i0+1
            p = max(d for i, d in w)-d0+1
            ww = [
                [w[i0+i, d0+d] for d in range(p)] for i in range(m)
            ]
            w = ww
        if isinstance(b, dict):
            b = [b[k] for k in sorted(b)]
        if isinstance(bounds, dict):
            bounds = [bounds[k] for k in sorted(bounds)]

        prefix = "_{0}_".format(zvar.lstrip("^"))
        prefix = prefix.replace("[", "_").replace("]", "_")

        graph, model, declared_vars = self._generate_model(
            zvar, W, w, b, bounds, prefix
        )

        self._zvars.append(zvar.lstrip("^"))
        self._models.append(model)
        self._graphs.append(graph)
        self._prefixes.append(prefix)

        self._pyvars["_model"] += writemod.model2ampl(model, declared_vars)

    def _generate_model(self, zvar, W, w, b, bounds=None, prefix=""):
        """Generates a arc-flow model."""
        from pyvpsolver import VBP, AFG
        m = len(w)
        bb = [0]*m
        bvars = []
        for i in range(m):
            if isinstance(b[i], six.string_types):
                bb[i] = min(
                    W[d]//w[i][d] for d in range(len(w[i])) if w[i][d] != 0
                )
                if bounds is not None:
                    bb[i] = min(bb[i], bounds[i])
                bvars.append(b[i])
            else:
                bb[i] = b[i]

        instance = VBP(W, w, bb, verbose=False)
        graph = AFG(instance, verbose=False).graph()
        feedback = (graph.T, graph.S, "Z")
        graph.A.append(feedback)

        vnames = {}
        vnames[feedback] = zvar
        ub = {}
        varl, cons = graph.get_flow_cons(vnames)
        assocs = graph.get_assocs(vnames)
        graph.names = vnames

        labels = {
            (u, v, i): ["i={0}".format(i+1)]
            for (u, v, i) in graph.A
            if isinstance(i, int) and i < m
        }
        graph.set_labels(labels)

        for i in range(m):
            if i not in assocs:
                assocs[i] = []
            if bounds is not None:
                for var in assocs[i]:
                    ub[var] = bounds[i]
            if isinstance(b[i], six.string_types):
                varl.append(b[i])
                cons.append((assocs[i], "=", b[i]))
            else:
                if b[i] > 1:
                    cons.append((assocs[i], ">=", b[i]))
                else:
                    cons.append((assocs[i], "=", b[i]))

        model = Model()
        for var in varl:
            model.add_var(name=var, lb=0, ub=ub.get(var, None), vtype="I")
        for lincomb, sign, rhs in cons:
            model.add_con(lincomb, sign, rhs)

        model.add_var(name="_total_flow", vtype="I")
        model.add_con("_total_flow", "=", vnames[feedback])

        declared_vars = set(bvars)

        def var_name(name):
            if name == zvar:
                return name
            elif name in declared_vars:
                return name
            else:
                return prefix+name

        def con_name(name):
            return prefix+name

        model.rename_vars(var_name)
        model.rename_cons(con_name)

        return graph, model, declared_vars

    def extract(self, get_var_value, verbose=False):
        """Extracts arc-flow solutions."""
        lst_sol = []
        for zvar, model, graph, prefix in zip(
                self._zvars, self._models, self._graphs, self._prefixes):
            varvalues = {
                var.replace(prefix, "", 1): get_var_value(var)
                for var in model.vars if var.startswith(prefix)
            }
            graph.set_flow(varvalues)
            sol = graph.extract_solution(graph.S, "<-", graph.T)
            lst_sol.append((zvar, varvalues.get(zvar, 0), sol))
            if verbose:
                print ("Graph: {0} (flow={1:d})\n\t{2}".format(
                    zvar, varvalues.get("_total_flow", 0), sol
                ))
        return lst_sol
