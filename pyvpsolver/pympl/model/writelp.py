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
from __future__ import print_function

# LP format example:
#
# Maximize
#  obj: x1 + 2 x2 + 3 x3 + x4
# Subject To
#  c1: - x1 + x2 + x3 + 10 x4 <= 20
#  c2: x1 - 3 x2 + x3 <= 30
#  c3: x2 - 3.5 x4 = 0
# Bounds
#  0 <= x1 <= 40
#  2 <= x4 <= 3
# General
#  x4
# End

from ..utils import lincomb2str


def write_lp(model, filename):
    """Writes models to files in LP format."""
    fout = open(filename, "w")

    # Objective:

    if model.objdir == "min":
        print("Minimize", file=fout)
    else:
        print("Maximize", file=fout)

    obj = model.obj
    if obj == []:
        obj = [(var, 0) for var in model.vars]
    print("\tobjective:{0}".format(lincomb2str(obj, mult=" ")), file=fout)

    # Constraints:

    print("Subject To", file=fout)

    for name in model.cons_list:
        lincomb, sign, rhs = model.cons[name]
        if sign in (">", "<"):
            sign += "="
        print(
            "\t{0}:{1} {2} {3}".format(
                name, lincomb2str(lincomb, mult=" "), sign, rhs
            ), file=fout
        )

    # Bounds:

    bounds = []
    for name in model.vars_list:
        lb = model.vars[name].get("lb", None)
        ub = model.vars[name].get("ub", None)
        if lb is not None or ub is not None:
            bounds.append((name, lb, ub))

    if bounds != []:
        print("Bounds", file=fout)
        for name, lb, ub in bounds:
            if lb is not None and ub is not None:
                print(
                    "\t{0} <= {1} <= {2}".format(repr(lb), name, repr(ub)),
                    file=fout
                )
            elif lb is not None:
                print(
                    "\t{0} <= {1}".format(repr(lb), name), file=fout
                )
            elif ub is not None:
                print(
                    "\t{0} <= {1}".format(name, repr(ub)), file=fout
                )

    # Integer variables:

    print("General", file=fout)
    for name in sorted(model.vars):
        if model.vars[name]["vtype"] == "I":
            print("\t{0}".format(name), file=fout)

    print("End", file=fout)

    fout.close()
