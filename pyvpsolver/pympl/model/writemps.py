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

# MPS format
#
# Field:     1          2          3         4         5         6
# Columns:  2-3        5-12      15-22     25-36     40-47     50-61
#
# http://web.mit.edu/lpsolve/doc/mps-format.htm

FIELD_START = [None, 1, 4, 14, 24, 39, 49]
FIELD_SIZE = [None, 2, 8, 8, 12, 8, 12]


def mps_row(lst):
    """Formats MPS rows."""
    line = " "
    for (field, value) in lst:
        assert 1 <= field <= 6
        value = str(value)
        if len(value) > FIELD_SIZE[field]:
            raise Exception("Failed to print the model in mps format")
        line += " " * (FIELD_START[field]-len(line))
        line += value
    return line


def write_mps(model, filename):
    """Writes models to files in MPS format."""
    fout = open(filename, "w")
    print >>fout, "NAME          MODEL"

    # Constraints:

    print >>fout, "ROWS"
    print >>fout, mps_row([(1, "N"), (2, "OBJ")])

    for cname in model.cons_list:
        lincomb, sign, rhs = model.cons[cname]
        if sign[0] == ">":
            s = "G"
        elif sign[0] == "<":
            s = "L"
        else:
            s = "E"
        print >>fout, mps_row([(1, s), (2, cname)])

    # A-matrix:

    columns = {var: [] for var in model.vars}
    for var, coef in model.obj:
        columns[var].append(("OBJ", coef))
    for cname in model.cons_list:
        lincomb, sign, rhs = model.cons[cname]
        for var, coef in lincomb:
            columns[var].append((cname, coef))

    Ivars = [v for v in model.vars_list if model.vars[v]["vtype"] == "I"]
    Cvars = [v for v in model.vars_list if model.vars[v]["vtype"] != "I"]

    if len(Ivars) != 0:
        print >>fout, "COLUMNS"
        print >>fout, mps_row(
            [(2, "MARKER"), (3, "\'MARKER\'"), (5, "\'INTORG\'")]
        )

        for vname in Ivars:
            for con, coef in columns[vname]:
                print >>fout, mps_row([(2, vname), (3, con), (4, coef)])

        print >>fout, mps_row(
            [(2, "MARKER"), (3, "\'MARKER\'"), (5, "\'INTEND\'")]
        )

    if len(Cvars) != 0:
        for vname in Cvars:
            for con, coef in columns[vname]:
                print >>fout, mps_row([(2, vname), (3, con), (4, coef)])

    # Right-hand-side vector:

    print >>fout, "RHS"
    for cname in model.cons_list:
        lincomb, sign, rhs = model.cons[cname]
        print >>fout, mps_row([(2, "RHS1"), (3, cname), (4, rhs)])

    # Bounds:

    print >>fout, "BOUNDS"

    for vname in model.vars_list:
        lb = model.vars[vname]["lb"]
        ub = model.vars[vname]["ub"]
        if lb is not None:
            print >>fout, mps_row(
                [(1, "LO"), (2, "BND1"), (3, vname), (4, lb)]
            )
        # else:
        #     print >>fout, mps_row([(1, "MI"), (2, "BND1"), (3, vname)])

        if ub is not None:
            print >>fout, mps_row(
                [(1, "UP"), (2, "BND1"), (3, vname), (4, ub)]
            )
        # else:
        #     print >>fout, mps_row([(1, "PL"), (2, "BND1"), (3, vname)])

    print >>fout, "ENDATA"

    fout.close()
