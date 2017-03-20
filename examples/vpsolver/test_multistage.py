#!/usr/bin/env python
"""
This code is part of the Arc-flow Vector Packing Solver (VPSolver).

Copyright (C) 2013-2016, Filipe Brandao
Faculdade de Ciencias, Universidade do Porto
Porto, Portugal. All rights reserved. E-mail: <fdabrandao@dcc.fc.up.pt>.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from __future__ import print_function
from pyvpsolver.solvers import multistage
import os


def read2d(fname):
    f = open(fname, "r")
    text = f.read()
    text = text[text.find("\n"):]
    text = text.replace("\t", " ").replace("\r", "").replace("\n", " ")
    lst = text.split()
    lst = [x for x in lst if x.isdigit()]
    lst = map(int, lst)
    W, H = lst[:2]
    lst = lst[2:]
    m = lst[0]
    lst.pop(0)
    w, h, b = [], [], []
    for i in xrange(m):
        w.append(lst.pop(0))
        h.append(lst.pop(0))
        b.append(lst.pop(0))
    return W, H, w, h, b


def readall(path):
    path += "/"
    f = open(path+"instances.txt", "r")
    lst = f.read().split()
    instances = []
    for fname in sorted(lst):
        f = open(path+fname, "r")
        inst = (fname, read2d(path+fname))
        instances.append(inst)
    return instances


def main():
    """Example: Multi-stage Cutting Stock."""
    from pyvpsolver.solvers.multistage import onecut, solve
    os.chdir(os.path.dirname(__file__) or os.curdir)

    path = "instances/2D/"
    folders = ["set_c", "set_d"]
    # set_c: Hifi (2001)
    # set_d: Alvarez-Valdes (2002)
    for folder in folders:
        lst = readall(path+folder)
        print(">>", folder)
        for name, instance in lst:
            # if name != "A2.txt": continue
            # if name != "OF2.txt": continue
            # if name != "ATP33.txt": continue
            # if name != "CU1.txt": continue
            # if name != "ATP49.txt":
            # if name != "A2.txt":
            # if name != "CW1.txt":
            #    continue
            print(">>>", folder, name)
            W, H, w, h, b = instance

            """
            W, H = 6, 6
            w = [4,2]
            h = [3,2]
            b = [5,5]
            """
            stage3 = True
            exact = False
            allow_rotation = False

            obj1, obj2 = None, None

            obj1 = onecut(
                W, H, w, h, b,
                stage3=stage3, exact=exact, allow_rotation=allow_rotation,
                script="vpsolver_gurobi.sh",
                script_options="""
                Threads=1
                Presolve=1 Method=2 MIPFocus=1 Heuristics=1 MIPGap=0
                MIPGapAbs=0.99999 Seed=1234 TimeLimit=600
                """,
            )

            print("W: {}, H: {}".format(W, H))
            print("items: {}".format(zip(range(1, len(w)+1), w, h, b)))

            obj2 = solve(
                W, H, w, h, b,
                stage3=stage3, exact=exact, allow_rotation=allow_rotation,
                restricted=True, simple=False,
                script="vpsolver_gurobi.sh",
                script_options="""
                Threads=1 Presolve=1 Method=2 MIPFocus=1 Heuristics=1 MIPGap=0
                MIPGapAbs=0.99999 Seed=1234 TimeLimit=600
                """,
            )

            print(">>", obj1, obj2)
            assert obj1 == obj2 or obj1 == obj2+1


if __name__ == "__main__":
    main()
