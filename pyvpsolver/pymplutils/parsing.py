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

t_SYMBNAME = r'\^?[a-zA-Z_][a-zA-Z0-9_]*'
t_INDEX1 = r'(?:\s*\[[^\]]*\])?' # [] index
t_INDEX2 = r'(?:\s*{[^}]*})?' # {} index
t_SYMBNAME_INDEX1 = t_SYMBNAME + t_INDEX1
t_SYMBNAME_INDEX2 = t_SYMBNAME + t_INDEX2


def parse_symbname(expr, allow_index=""):
    """Matches and returns a symbolic name."""
    assert allow_index in ("", "[]", "{}")
    if allow_index == "[]":
        t_symb = t_SYMBNAME_INDEX1
    elif allow_index == "{}":
        t_symb = t_SYMBNAME_INDEX2
    else:
        t_symb = t_SYMBNAME
    match = re.match(r'\s*('+t_symb+r')\s*$', expr)
    if match is None:
        return None
    name = match.groups()[0]
    return name


def parse_symblist(expr, allow_index=""):
    """Matches and returns a list of symbolic names."""
    assert allow_index in ("", "[]", "{}")
    if allow_index == "[]":
        t_symb = t_SYMBNAME_INDEX1
    elif allow_index == "{}":
        t_symb = t_SYMBNAME_INDEX2
    else:
        t_symb = t_SYMBNAME
    match = re.match(
        r'\s*(\s*'+t_symb+r'\s*(?:,\s*'+t_symb+r'\s*)*)\s*$', expr
    )
    if match is None:
        return None
    lst = match.groups()[0].split(",")
    lst = [x.strip() for x in lst]
    return lst


def parse_indexed(expr, index_type):
    """Matches and returns an indexed symbolic name (i.e., name{index})."""
    assert index_type in ("[]", "{}")
    if index_type == "[]":
        match = re.match(
            r'\s*('+t_SYMBNAME+r')\s*'
            r'(\[\s*'+t_SYMBNAME+r'\s*(?:,'
            r'\s*'+t_SYMBNAME+r'\s*)*\])?\s*$',
            expr
        )
    elif index_type == "{}":
        match = re.match(
            r'\s*('+t_SYMBNAME+r')\s*'
            r'({\s*'+t_SYMBNAME+r'\s*(?:,\s*'+t_SYMBNAME+r'\s*)*})?\s*$',
            expr
        )
    if match is None:
        return None
    name, index = match.groups()
    if index is not None:
        index = index.strip(index_type+" ")
        index = index.split(",")
        index = [x.strip() for x in index]
    return name, index
