#!/bin/sh
# This code is part of the Arc-flow Vector Packing Solver (VPSolver).
#
# Copyright (C) 2013, Filipe Brandao
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

set -e
echo "Copyright (C) 2013, Filipe Brandao"
echo "Usage: vpsolver_lpsolve.sh instance.vbp"

BASEDIR=`dirname $0`
TMP_DIR=$BASEDIR/tmp/
BIN_DIR=$BASEDIR/bin/
if [ "$#" -eq 1 ]; then
    instance=$1
    fname=`basename $instance`  
    
    echo "\n>>> vbp2afg..."
    $BIN_DIR/vbp2afg $instance $TMP_DIR/$fname.afg -2 

    echo "\n>>> afg2mps..."
    $BIN_DIR/afg2mps $TMP_DIR/$fname.afg $TMP_DIR/$fname.mps

    echo "\n>>> solving the MIP model using lp_solve..."
    echo "Note: different parameter settings may improve the performance substantially!"
    lp_solve -mps $TMP_DIR/$fname.mps > $TMP_DIR/$fname.out    
    sed -e '1,/variables:/d' < $TMP_DIR/$fname.out > $TMP_DIR/$fname.sol

    echo "\n>>> vbpsol..."
    $BIN_DIR/vbpsol $TMP_DIR/$fname.afg $TMP_DIR/$fname.sol
fi
