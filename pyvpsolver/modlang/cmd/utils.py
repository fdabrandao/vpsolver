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
    assert match is not None
    name = match.groups()[0]
    return name


def parse_varlist(expr):
    """Matches and returns a list of variable names."""
    match = re.match(
        "\\s*(\\s*"+RGX_VARNAME+"\\s*(?:,\\s*"+RGX_VARNAME+"\\s*)*)\\s*$", expr
    )
    assert match is not None
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
    assert match is not None
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
    return ",".join(
        [str(x) if not isinstance(x, str) else "'%s'" % x for x in tuple_]
    )


def ampl_set(name, values, sets):
    """Generates a definition for an AMPL set."""
    assert name not in sets
    sets[name] = deepcopy(values)

    def format_entry(x):
        if isinstance(x, str):
            return "'%s'" % x
        elif isinstance(x, (tuple, list)):
            return "(%s)" % tuple2str(x)
        else:
            return str(x)

    defs = "set %s := {" % name
    defs += ",".join(format_entry(x) for x in values)
    defs += "};\n"
    return defs, ""


def ampl_param(name, index, value, params):
    """Generates a definition for an AMPL parameter."""
    assert name not in params
    params[name] = deepcopy(value)
    if isinstance(value, dict):
        defs = "param %s{%s};\n" % (name, index)

        def format_entry(k, v):
            if isinstance(k, str):
                k = "'%s'" % k
            elif isinstance(k, tuple):
                k = tuple2str(k)
            else:
                k = str(k)
            if isinstance(v, str):
                v = "'%s'" % v
            else:
                v = str(v)
            return "[%s]%s" % (k, v)

        data = "param %s := " % name
        data += "".join(format_entry(k, v) for k, v in value.items())
        data += ";\n"
        return defs, data
    else:
        assert index is None
        assert isinstance(value, (str, float, int))
        if isinstance(value, str):
            value = "'%s'" % value
        defs = "param %s := %s;\n" % (name, str(value))
        return defs, ""
