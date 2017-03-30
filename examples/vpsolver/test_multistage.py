#!/usr/bin/env python
"""
This code is part of the Arc-flow Vector Packing Solver (VPSolver).

Copyright (C) 2013-2017, Filipe Brandao
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
import sys


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
    from time import time

    assert len(sys.argv) >= 2
    test = sys.argv[1]
    assert test in ("arcflow", "onecut")
    exact = "exact" in sys.argv
    stage3 = "stage3" in sys.argv
    rotation = "rotation" in sys.argv

    path = "instances/2D/"
    folders = ["set_c", "set_d"]
    log_folder = "tmp/logs/multistage/{}".format(test)
    try:
        os.makedirs(log_folder)
    except OSError:
        pass
    # set_c: Hifi (2001)
    # set_d: Alvarez-Valdes (2002)
    for folder in folders:
        lst = readall(path+folder)
        print(">>", folder)
        for name, instance in lst:
            print(">>>", folder, name)
            W, H, w, h, b = instance

            stdout_org = sys.stdout
            probtype = "{}{}{}".format(
                "3" if stage3 else "2",
                "E" if exact else "NE",
                "R" if rotation else "",
            )
            log_file = "{}/{}_{}_{}".format(log_folder, folder, probtype, name)
            with open(log_file, "w") as f:
                sys.stdout = f
                t0 = time()
                if test == "onecut":
                    obj1 = onecut(
                        W, H, w, h, b,
                        stage3=stage3, exact=exact, allow_rotation=rotation,
                        script="vpsolver_gurobi.sh",
                        script_options="""
                        Threads=1 Presolve=1 Method=2
                        MIPGap=0 MIPGapAbs=0.99999 Seed=1234 TimeLimit=300
                        """,
                    )

                elif test == "arcflow":
                    obj2 = solve(
                        W, H, w, h, b,
                        stage3=stage3, exact=exact, allow_rotation=rotation,
                        restricted=True, simple=False,
                        script="vpsolver_gurobi.sh",
                        script_options="""
                        Threads=1 Presolve=1 Method=2
                        MIPGap=0 MIPGapAbs=0.99999 Seed=1234 TimeLimit=300
                        """,
                    )
                t1 = time()
            sys.stdout = stdout_org
            print("### {} {} {} ({})".format(folder, name, t1-t0, log_file))


if __name__ == "__main__":
    main()
