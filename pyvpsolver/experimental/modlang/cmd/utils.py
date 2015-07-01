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
from copy import deepcopy
import re

rgx_varname = "[a-zA-Z_][a-zA-Z0-9_]*"

def parse_varname(expr):
    match = re.match("\s*("+rgx_varname+")\s*$", expr)
    assert match != None
    name = match.groups()[0]
    return name

def parse_varlist(expr):
    match = re.match("\s*(\s*"+rgx_varname+"\s*(?:,\s*"+rgx_varname+"\s*)*)\s*$", expr)
    assert match != None
    lst = match.groups()[0].split(',')
    lst = [x.strip() for x in lst]
    return lst

def parse_index(expr):
    match = re.match("\s*("+rgx_varname+")\s*({\s*"+rgx_varname+"\s*(?:,\s*"+rgx_varname+"\s*)*})?\s*$", expr)
    assert match != None
    name, index = match.groups()
    if index != None:
        index = index.strip('{} ')
        index = index.split(',')
        index = [x.strip() for x in index]
    return name, index

def list2dict(lst, i0 = 0):
    d = {}
    def f(key, lst):
        for i in xrange(len(lst)):
            if type(lst[i]) != list:
                if key == []:
                    d[i0+i] = lst[i]
                else:
                    d[tuple(key+[i0+i])] = lst[i]
            else:
                f(key+[i0+i], lst[i])
    f([],lst)
    return d

def tuple2str(tp):
    return ','.join(map(lambda x: str(x) if type(x) != str else "'%s'"%x, tp))

def ampl_set(name, values, sets):
    assert name not in sets
    sets[name] = deepcopy(values)
    defs = "set %s := {" % name
    first = True
    for x in values:
        if type(x) == str: x = "'%s'"%x
        if type(x) in [tuple,list]: x = "(%s)"%tuple2str(x)
        if first: defs += "%s" % str(x)
        else: defs += ",%s" % str(x)
        first = False
    defs += "};\n"
    return defs, ""

def ampl_param(name, index, value, params):
    assert name not in params
    params[name] = deepcopy(value)
    if type(value) == dict:
        defs = "param %s{%s};\n" % (name, index)
        data = "param %s := " % name
        first = True
        for k in value:
            x = value[k]
            if type(x) == str: x = "'%s'"%x
            if type(k) == tuple: k = tuple2str(k)
            data += "[%s]%s" % (k,str(x))
        data += ";\n"
        return defs, data
    else:
        assert index == None
        assert type(value) in [str,float,int]
        if type(value) == str: value = "'%s'"%value
        defs = "param %s := %s;\n" % (name, str(value))
        return defs, ""
