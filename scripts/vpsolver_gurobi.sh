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

set -e
echo "Copyright (C) 2013-2015, Filipe Brandao"

BASEDIR=`dirname $0`
BIN_DIR=$BASEDIR/../bin/
TMP_DIR=`mktemp -d -t XXXXXXXXXX`
trap "rm -rf $TMP_DIR;" SIGHUP SIGINT SIGTERM EXIT

usage(){
    echo -e "Usage:"
    echo -e "  $0 --vbp instance.vbp"
    echo -e "  $0 --mps/--lp model.mps/.lp"
    echo -e "  $0 --mps/--lp model.mps/.lp --afg graph.afg"
}

error(){
    echo "Error: invalid arguments."
    usage
    exit 1
}

solve(){
    local model_file=$1
    GRB_PARAMS="Threads=1 Presolve=1 Method=2 MIPFocus=1 Heuristics=1 MIPGap=0 MIPGapAbs=0.99999"
    echo -e "\n>>> solving the MIP model using Gurobi..."
    echo -e "Note: different parameter settings may improve the performance substantially!"
    gurobi_cl $GRB_PARAMS ResultFile=$TMP_DIR/vars.sol $model_file &
    local pid=$!
    trap "kill $pid &> /dev/null" SIGHUP SIGINT SIGTERM
    wait $pid   
    sed '/#/d' < $TMP_DIR/vars.sol > $TMP_DIR/vars.sol2
    mv $TMP_DIR/vars.sol2 $TMP_DIR/vars.sol
}

model_file=""
afg_file=""
vbp_file=""
sol_file=""

while true;
do
  case "$1" in
    --mps)
        if [[ -n "$2" && -e "$2" && "$2" =~ \.mps$ ]]; then
            model_file=$2
        else
            error
        fi
        shift 2;;
        
    --lp)
        if [[ -n "$2" && -e "$2" && "$2" =~ \.lp$ ]]; then
            model_file=$2
        else
            error
        fi
        shift 2;;        

    --afg)
        if [[ -n "$2" && -e "$2" && "$2" =~ \.afg$ ]]; then
            afg_file=$2
        else
            error
        fi
        shift 2;;    
 
    --vbp)
        if [[ -n "$2" && -e "$2" && "$2" =~ \.vbp$ ]]; then
            vbp_file=$2
        else
            error            
        fi
        shift 2;;
        
    --wsol)        
        if [[ -n "$2" ]]; then
            sol_file=$2
        else
            error            
        fi
        shift 2;;        
            
    *)
        if [[ -n "$1" ]]; then
            error
        else
            break        
        fi
  esac
done

if [[ -z "$vbp_file" && -z "$model_file" ]]; then
    error
fi

if [[ -n "$vbp_file" ]]; then
    if [[ -n "$afg_file" || -n "$model_file" ]]; then
        error
    fi
    
    afg_file=$TMP_DIR/graph.afg
    model_file=$TMP_DIR/model.mps
    
    echo -e "\n>>> vbp2afg..."
    $BIN_DIR/vbp2afg $vbp_file $afg_file -2 &
    pid=$!
    trap "kill $pid &> /dev/null" SIGHUP SIGINT SIGTERM
    wait $pid 

    echo -e "\n>>> afg2mps..."
    $BIN_DIR/afg2mps $afg_file $model_file
fi

solve $model_file;

if [[ -n "$afg_file" && -z "$sol_file" ]]; then
    echo -e "\n>>> vbpsol..."
    $BIN_DIR/vbpsol $afg_file $TMP_DIR/vars.sol
fi      

if [[ -n "$sol_file" ]]; then
    cp $TMP_DIR/vars.sol $sol_file
fi

