#!/bin/bash
# This code is part of the Arc-flow Vector Packing Solver (VPSolver).
#
# Copyright (C) 2013-2015, Filipe Brandao
# Faculdade de Ciencias, Universidade do Porto
# Porto, Portugal. All rights reserved. E-mail: <fdabrandao@dcc.fc.up.pt>.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
BASEDIR=`dirname $0`
cd $BASEDIR

make clean >compile.log 2>&1 

echo "mandatory:"

echo -n "  vbp2afg "
make bin/vbp2afg >>compile.log 2>&1 
if [[ $? == 0 ]]; then echo "[OK]";
else echo "[Failed]"; fi

echo -n "  afg2mps "
make bin/afg2mps >>compile.log 2>&1
if [[ $? == 0 ]]; then echo "[OK]";
else echo "[Failed]"; fi

echo -n "  afg2lp  "
make bin/afg2lp >>compile.log 2>&1
if [[ $? == 0 ]]; then echo "[OK]";
else echo "[Failed]"; fi

echo -n "  vbpsol  "
make bin/vbpsol >>compile.log 2>&1
if [[ $? == 0 ]]; then echo "[OK]";
else echo "[Failed]"; fi

echo "optional:"

echo -n "  vpsolver "
make bin/vpsolver >>compile.log 2>&1 
if [[ $? == 0 ]]; then echo "[OK]";
else echo "[Failed]"; fi

echo -n "  gg_afg   "
make bin/gg_afg >>compile.log 2>&1
if [[ $? == 0 ]]; then echo "[OK]";
else echo "[Failed]"; fi

echo -n "  solve_gurobi "
make bin/solve_gurobi >>compile.log 2>&1
if [[ $? == 0 ]]; then echo "[OK]";
else echo "[Failed]"; fi

echo -n "  solve_glpk   "
make bin/solve_glpk >>compile.log 2>&1
if [[ $? == 0 ]]; then echo "[OK]";
else echo "[Failed]"; fi



