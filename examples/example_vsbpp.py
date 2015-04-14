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

""" Variable-sized Bin Packing Example """

"""
Uses the method proposed in:
Brandao, F. and Pedroso, J. P. (2013). Multiple-choice Vector Bin Packing:
Arc-flow Formulation with Graph Compression. Technical Report DCC-2013-13, 
Faculdade de Ciencias da Universidade do Porto, Universidade do Porto, Portugal.
"""

from pyvpsolver import *

inf = float('inf')

Ws = [[100], [120], [150]] # capacities
Cs = [100, 120, 150] # costs
Qs = [inf, 1, 30] # number of bins available of each type (note: the model may become infeasible)
ws = [[[10]], [[14]], [[17]], [[19]], [[24]], [[29]], [[32]], [[33]], [[36]], 
      [[38]], [[40]], [[50]], [[54]], [[55]], [[63]], [[66]], [[71]], [[77]], 
      [[79]], [[83]], [[92]], [[95]], [[99]]]
b = [1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1]

obj, sol = solve_mvbp(Ws, Cs, Qs, ws, b, svg_file="tmp/graph_vsbpp.svg", verbose=True, script="vpsolver_glpk.sh")
print "obj:", obj
print "sol:", sol
print_solution_mvbp(obj, sol)

