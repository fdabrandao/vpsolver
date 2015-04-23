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

TMP_DIR=`mktemp -d -t XXXXXXXXXX`
trap "rm -rf $TMP_DIR" EXIT

PATH="../bin/:../scripts/:$PATH"

echo "**********************************************************"
echo "* Example 1:                                             *"
echo "* > vpsolver instance.vbp                                *"
echo "**********************************************************"
vpsolver instance.vbp

echo -e "\n\n"

echo "**********************************************************"
echo "* Example 2:                                             *"
echo "* > vbp2afg instance.vbp graph.afg                       *"
echo "* > afg2mps graph.afg model.mps                          *"
echo "* > solve_gurobi model.mps vars.sol                      *"
echo "* > vbpsol graph.afg vars.sol                            *"
echo "**********************************************************"
vbp2afg instance.vbp $TMP_DIR/graph.afg
afg2mps $TMP_DIR/graph.afg $TMP_DIR/model.mps
solve_gurobi $TMP_DIR/model.mps $TMP_DIR/vars.sol
vbpsol $TMP_DIR/graph.afg $TMP_DIR/vars.sol

echo -e "\n\n"

echo "**********************************************************"
echo "* Example 3:                                             *"
echo "* > vbp2afg instance.vbp graph.afg                       *"
echo "* > afg2lp graph.afg model.lp                            *"
echo "* > solve_glpk model.lp vars.sol                         *"
echo "* > vbpsol graph.afg vars.sol                            *"
echo "**********************************************************"
vbp2afg instance.vbp $TMP_DIR/graph.afg
afg2lp $TMP_DIR/graph.afg $TMP_DIR/model.lp
solve_glpk $TMP_DIR/model.lp $TMP_DIR/vars.sol
vbpsol $TMP_DIR/graph.afg $TMP_DIR/vars.sol

echo -e "\n\n"

echo "**********************************************************"
echo "* Example 4:                                             *"
echo "* > vbp2afg instance.vbp graph.afg                       *"
echo "* > afg2lp graph.afg model.lp                            *"
echo "* > vpsolver_glpk.sh --lp model.lp --afg graph.afg       *"
echo "**********************************************************"
vbp2afg instance.vbp $TMP_DIR/graph.afg
afg2lp $TMP_DIR/graph.afg $TMP_DIR/model.lp
vpsolver_glpk.sh --lp $TMP_DIR/model.lp --afg $TMP_DIR/graph.afg

echo -e "\n\n"

echo "**********************************************************"
echo "* Example 5:                                             *"
echo "* > vbp2afg instance.vbp graph.afg                       *"
echo "* > afg2mps graph.afg model.mps                          *"
echo "* > vpsolver_gurobi.sh --mps model.mps --afg graph.afg   *"
echo "**********************************************************"
vbp2afg instance.vbp $TMP_DIR/graph.afg
afg2mps $TMP_DIR/graph.afg $TMP_DIR/model.mps
vpsolver_gurobi.sh --mps $TMP_DIR/model.mps --afg $TMP_DIR/graph.afg

echo -e "\n\n"

echo "**********************************************************"
echo "* Example 6:                                             *"
echo "* > ./vpsolver_gurobi.sh --vbp instance.vbp              *"
echo "**********************************************************"
vpsolver_gurobi.sh --vbp instance.vbp
