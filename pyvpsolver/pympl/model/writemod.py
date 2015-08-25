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

# AMPL format example:
#
# var x1;
# var x2;
# maximize obj: 0.6 * x1 + 0.5 * x2;
# s.t. c1: x1 + 2 * x2 <= 1;
# s.t. c2: 3 * x1 + x2 <= 2;

from ..utils import lincomb2str, ampl_var, ampl_con


def write_mod(model, filename):
    """Writes models to files in AMPL format."""
    fout = open(filename, "w")

    # Variables:

    for var in model.vars:
        typ = model.vars[var]["vtype"]
        lb = model.vars[var]["lb"]
        ub = model.vars[var]["ub"]
        print >>fout, ampl_var(name=var, typ=typ, lb=lb, ub=ub)

    # Objective:

    if model.obj != []:
        if model.objdir == "min":
            print >>fout, "minimize obj:{0};".format(lincomb2str(model.obj))
        else:
            print >>fout, "maximize obj:{0};".format(lincomb2str(model.obj))

    # Constraints:

    for name in model.cons_list:
        lincomb, sign, rhs = model.cons[name]
        print >>fout, ampl_con(name, lincomb, sign, rhs)

    print >>fout, "end;"
    fout.close()


def model2ampl(model, declared_vars=None):
    """Returns models as a string in AMPL format."""
    res = ""

    # Variables:

    if declared_vars is not None:
        declared_vars = set(declared_vars)
    else:
        declared_vars = set()

    def format_var(name):
        typ = model.vars[name]["vtype"]
        lb = model.vars[name]["lb"]
        ub = model.vars[name]["ub"]
        return ampl_var(name=name, typ=typ, lb=lb, ub=ub)

    res += "".join(
        format_var(name)
        for name in model.vars
        if name not in declared_vars
    )

    # Constraints:

    def format_con(name):
        lincomb, sign, rhs = model.cons[name]
        lincomb = [(var, coef) for (var, coef) in lincomb]
        return ampl_con(name, lincomb, sign, rhs)

    res += "".join(
        format_con(name)
        for name in model.cons_list
    )

    return res
