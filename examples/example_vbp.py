#!/usr/bin/python
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
import sys, os
sdir = os.path.dirname(__file__)
if sdir != '': os.chdir(sdir)

""" Add VPSolver folders to path """

#add vpsolver folder to sys.path
sys.path.insert(0, "../")

#add vpsolver/bin folder to path
os.environ["PATH"] = "../bin"+":"+os.environ["PATH"]

#add vpsolver/scripts folder to path
os.environ["PATH"] = "../scripts"+":"+os.environ["PATH"]

""" Vector Packing Example """

from pyvpsolver import *

W = (5180, 2)
w = [(1120,1), (1250,1), (520,1), (1066,1), (1000,1), (1150,1)]
b = [9, 5, 91, 18, 11, 64]

#solve
obj, sol = solve_vbp(W, w, b, svg_file="tmp/graph_vbp.svg", verbose=False, script="vpsolver_gurobi.sh")
print "obj:", obj
print "sol:", sol
print_solution_vbp(obj, sol)

