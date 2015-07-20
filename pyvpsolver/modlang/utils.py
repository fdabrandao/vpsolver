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

import re
from copy import deepcopy

RGX_VARNAME = "[a-zA-Z_][a-zA-Z0-9_]*"


def parse_var(expr):
    """Matches and returns a variable name."""
    match = re.match("\\s*("+RGX_VARNAME+")\\s*$", expr)
    if match is None:
        return None
    name = match.groups()[0]
    return name


def parse_varlist(expr):
    """Matches and returns a list of variable names."""
    match = re.match(
        "\\s*(\\s*"+RGX_VARNAME+"\\s*(?:,\\s*"+RGX_VARNAME+"\\s*)*)\\s*$", expr
    )
    if match is None:
        return None
    lst = match.groups()[0].split(",")
    lst = [x.strip() for x in lst]
    return lst


def parse_indexed(expr):
    """Matches and returns an indexed variable (i.e., variable{index})."""
    match = re.match(
        "\\s*("+RGX_VARNAME+")\\s*"
        "({\\s*"+RGX_VARNAME+"\\s*(?:,\\s*"+RGX_VARNAME+"\\s*)*})?\\s*$",
        expr
    )
    if match is None:
        return None
    name, index = match.groups()
    if index is not None:
        index = index.strip("{} ")
        index = index.split(",")
        index = [x.strip() for x in index]
    return name, index


def list2dict(lst, i0=0):
    """Converts a list to a dictionary."""
    dic = {}

    def conv_rec(key, lst):
        for i in xrange(len(lst)):
            if not isinstance(lst[i], list):
                if key == []:
                    dic[i0+i] = lst[i]
                else:
                    dic[tuple(key+[i0+i])] = lst[i]
            else:
                conv_rec(key+[i0+i], lst[i])

    conv_rec([], lst)
    return dic


def tuple2str(tuple_):
    """Converts a tuple to a AMPL tuple."""

    def format_entry(e):
        if not isinstance(e, str):
            return str(e)
        else:
            return "'{0}'".format(e)

    return ",".join(format_entry(e) for e in tuple_)


def ampl_set(name, values, sets, params):
    """Generates the definition for an AMPL set."""
    assert name not in sets
    assert name not in params
    sets[name] = deepcopy(values)

    def format_entry(e):
        if isinstance(e, str):
            return "'{0}'".format(e)
        elif isinstance(e, (tuple, list)):
            return "({0})".format(tuple2str(e))
        else:
            return str(e)

    defs = "set {0} := {{{1}}};\n".format(
        name, ",".join(format_entry(e) for e in values)
    )
    return defs, ""


def ampl_param(name, index, value, sets, params):
    """Generates the definition for an AMPL parameter."""
    assert name not in sets
    assert name not in params
    params[name] = deepcopy(value)
    if isinstance(value, dict):
        defs = "param {0}{{{1}}};\n".format(name, index)

        def format_entry(k, v):
            if isinstance(k, str):
                k = "'{0}'".format(k)
            elif isinstance(k, tuple):
                k = tuple2str(k)
            else:
                k = str(k)
            if isinstance(v, str):
                v = "'{0}'".format(v)
            else:
                v = str(v)
            return "[{0}]{1}".format(k, v)

        data = "param {0} := {1};\n".format(
            name, "".join(format_entry(k, v) for k, v in value.items())
        )
        return defs, data
    else:
        assert index is None
        assert isinstance(value, (str, float, int))
        if isinstance(value, str):
            value = "'{0}'".format(value)
        defs = "param {0} := {1};\n".format(name, str(value))
        return defs, ""


def lincomb2str(lincomb):
    """Returns the linear combination as a string."""

    def format_entry(var, coef):
        if abs(coef) != 1:
            if coef >= 0:
                return " + {0:g} {1}".format(coef, var)
            else:
                return " - {0:g} {1}".format(abs(coef), var)
        else:
            if coef >= 0:
                return " + {0}".format(var)
            else:
                return " - {0}".format(var)

    return "".join(format_entry(var, coef) for var, coef in lincomb)


def ampl_var(name, typ=None, lb=None, ub=None, explicit=None):
    """Generates the definition for an AMPL variable."""
    defs = "var {0}".format(name)
    if typ == "I":
        defs += ", integer"
    if typ == "B":
        defs += ", binary"
    if lb is not None:
        defs += ", >= {0:g}".format(lb)
    if ub is not None:
        defs += ", <= {0:g}".format(ub)
    if explicit is not None:
        defs += ", {0}".format(explicit)
    defs += ";"
    return defs


def ampl_con(name, lincomb, sign, rhs):
    """Generates the definition for an AMPL constraint."""
    if sign in (">", "<"):
        sign += "="
    defs = "s.t. {name}: {lin} {sign} {rhs};".format(
        name=name,
        lin=lincomb2str(lincomb),
        sign=sign,
        rhs=rhs
    )
    return defs
