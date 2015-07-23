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

import os
sdir = os.path.dirname(__file__)
if sdir != "":
    os.chdir(sdir)

import equivknapsack01
import equivknapsack
import graph
import instance

if __name__ == "__main__":
    print "equivknapsack:"
    equivknapsack.main()

    print "equivknapsack01:"
    equivknapsack01.main()

    print "graph:"
    graph.main()

    print "instance:"
    instance.main()
