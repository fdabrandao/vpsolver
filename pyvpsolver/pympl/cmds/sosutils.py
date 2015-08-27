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
from builtins import range


def add_sos1(model, varl, ub=1, prefix=""):
    """Adds SOS1 constraints to model."""
    def yvar(i):
        return prefix+"y_{0}".format(i)

    for i in range(len(varl)):
        model.add_var(name=yvar(i), vtype="B")

    for i, var in enumerate(varl):
        model.add_con(var, "<=", (yvar(i), ub))

    model.add_con([yvar(i) for i in range(len(varl))], "=", 1)


def add_sos2(model, varl, ub=1, prefix=""):
    """Adds SOS2 constraints to model."""
    def yvar(i):
        return prefix+"y_{0}".format(i)

    for i in range(len(varl)-1):
        model.add_var(name=yvar(i), vtype="B")

    for i, var in enumerate(varl):
        if i == 0:
            model.add_con(var, "<=", (yvar(i), ub))
        elif i == len(varl)-1:
            model.add_con(var, "<=", (yvar(i-1), ub))
        else:
            model.add_con(var, "<=", [(yvar(i-1), ub), (yvar(i), ub)])

    model.add_con([yvar(i) for i in range(len(varl)-1)], "=", 1)
