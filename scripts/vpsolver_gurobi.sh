#!/bin/bash
# This code is part of the Arc-flow Vector Packing Solver (VPSolver).
set -e
echo "Copyright (C) 2013-2022, Filipe Brandao"

solve_model(){
    echo -e "\n>>> solving the MIP model using Gurobi..."
    echo -e "Note: different parameter settings may improve the performance substantially!"
    gurobi_cl $options ResultFile=$TMP_DIR/vars.sol $model_file &
    local pid=$!
    trap "kill $pid &> /dev/null" SIGHUP SIGINT SIGTERM
    wait $pid
    sed '/#/d' $TMP_DIR/vars.sol > $TMP_DIR/vars.sol2
    mv $TMP_DIR/vars.sol2 $TMP_DIR/vars.sol
}

BASEDIR="`dirname "$0"`"
source $BASEDIR/vpsolver_base.sh
init_vars
options="Threads=1 Presolve=1 Method=2 MIPFocus=1 Heuristics=1 MIPGap=0 MIPGapAbs=0.99999 Seed=1234"
parse_args $*
generate_model
solve_model
extract_solution
