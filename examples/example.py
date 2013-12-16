#!/usr/bin/python
"""
This code is part of the Arc-flow Vector Packing Solver (VPSolver).

Copyright (C) 2013, Filipe Brandao
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
if sdir != "": os.chdir(sdir)

""" Add VPSolver folders to path """

#add vpsolver folder to sys.path
sys.path.insert(0, "../")

#add vpsolver/bin folder to path
os.environ["PATH"] = "../bin"+":"+os.environ["PATH"]

#add vpsolver/scripts folder to path
os.environ["PATH"] = "../scripts"+":"+os.environ["PATH"]

""" Example """

## load all the vpsolver utils ##
from pyvpsolver import *

## Creating instanceA ##
instanceA = VBP([5180], [1120, 1250, 520, 1066, 1000, 1150], 
                        [9, 5, 91, 18, 11, 64], verbose=False)

## Creating instanceB from a .vbp file ##
instanceB = VBP.fromFile("instance.vbp", verbose=False)

## Creating an arc-flow graph for instanceA ##
afg = AFG(instanceA, verbose=False)

## Creating .mps and .lp models for instanceA ##
mps_model = MPS(afg, verbose=False)
lp_model = LP(afg, verbose=False)

## Drawing an arc-flow graph (requires pygraphviz) ##
afg.graph().draw("tmp/graph.svg")

## Solving instanceA using bin/vpsolver (requires Gurobi) ##
## The input must be an instance.                         ##
out, sol = VPSolver.vpsolver(instanceA, verbose=True)

## Solving instanceA using any vpsolver script (i.e., any MIP solver) ##
## The scripts accept models with and without the underlying graphs.  ##
## However, the graphs are required to extract the solution.          ##
out, sol = VPSolver.script("vpsolver_glpk.sh", lp_model, afg, verbose=True)
out, sol = VPSolver.script("vpsolver_gurobi.sh", mps_model, verbose=True)

# solving an instance directly without creating AFG, MPS or LP objects
out, sol = VPSolver.script("vpsolver_glpk.sh", instanceB, verbose=True)

## printing the solution ##
obj, patterns = sol
print "Objective:", obj
print "Solution:", patterns

## pretty print for solutions ##
print_solution_vbp(obj, patterns)

