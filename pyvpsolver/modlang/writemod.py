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


def lincomb2str(lincomb):
    """Returns the linear combination as a string."""
    expr = ""
    for var, coef in lincomb:
        if abs(coef) != 1:
            if coef >= 0:
                expr += " + %g %s" % (coef, var)
            elif coef < 0:
                expr += " - %g %s" % (abs(coef), var)
        else:
            if coef >= 0:
                expr += " + %s" % (var)
            elif coef < 0:
                expr += " - %s" % (var)
    return expr


def write_mod(model, filename):
    """Exports the model in AMPL format."""
    fout = open(filename, "w")

    # variables

    for var in model.vars:
        lb = model.vars[var]["lb"]
        ub = model.vars[var]["ub"]
        typ = ""
        if model.vars[var]["vtype"] == "I":
            typ = ", integer"
        if lb is not None and ub is not None:
            print >>fout, "var %s%s, >= %g, <= %g;" % (var, typ, lb, ub)
        elif lb is not None:
            print >>fout, "var %s%s, >= %g;" % (var, typ, lb)
        elif ub is not None:
            print >>fout, "var %s%s, <= %g;" % (var, typ, ub)
        else:
            print >>fout, "var %s%s;" % (var, typ)

    # objective

    if model.obj != []:
        if model.objdir == "min":
            print >>fout, "minimize obj:",
        else:
            print >>fout, "maximize obj:",
        print >>fout, lincomb2str(model.obj)+";"

    # constraints

    for name in model.cons_list:
        lincomb, sign, rhs = model.cons[name]
        if sign in (">", "<"):
            sign += "="
        print >>fout, "s.t. %s:%s %s %s;" % (
            name, lincomb2str(lincomb), sign, rhs
        )

    print >>fout, "end;"
    fout.close()


def model2ampl(model, zvar, ztype, excluded_vars=[], prefix=""):
    """Returns the model in AMPL format as a string."""
    res = ""

    # variables

    excluded_vars = set(excluded_vars)
    for var in model.vars:
        if var in excluded_vars:
            continue
        lb = model.vars[var]["lb"]
        ub = model.vars[var]["ub"]
        typ = ""
        pref = prefix
        if model.vars[var]["vtype"] == "I":
            typ = ", integer"
        if var == zvar:
            pref = ""
            if any(x in ztype for x in ("integer", "binary", ">", "<")):
                typ = ztype
                lb, ub = None, None
        if lb is not None and ub is not None:
            res += "var %s%s%s, >= %g, <= %g;" % (pref, var, typ, lb, ub)
        elif lb is not None:
            res += "var %s%s%s, >= %g;" % (pref, var, typ, lb)
        elif ub is not None:
            res += "var %s%s%s, <= %g;" % (pref, var, typ, ub)
        else:
            res += "var %s%s%s;" % (pref, var, typ)

    # constraints

    for name in model.cons_list:
        lincomb, sign, rhs = model.cons[name]
        if sign in [">", "<"]:
            sign += "="
        for i in xrange(len(lincomb)):
            if lincomb[i][0] != zvar and lincomb[i][0] not in excluded_vars:
                lincomb[i] = (prefix+lincomb[i][0], lincomb[i][1])
        res += "s.t. %s%s:%s %s %s;" % (
            prefix, name, lincomb2str(lincomb), sign, rhs
        )

    return res
