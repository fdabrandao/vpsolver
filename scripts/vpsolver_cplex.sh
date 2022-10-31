#!/bin/bash
# This code is part of the Arc-flow Vector Packing Solver (VPSolver).
set -e
echo "Copyright (C) 2013-2022, Filipe Brandao"

solve_model(){
    echo -e "\n>>> solving the MIP model using CPLEX..."
    echo -e "Note: different parameter settings may improve the performance substantially!"
    rm -rf $TMP_DIR/vars.sol;
    (
        echo "read $model_file"
        echo -e "$options"
        echo "optimize"
        echo "write $TMP_DIR/vars.sol"
    ) | cplex &
    local pid=$!
    trap "kill $pid &> /dev/null" SIGHUP SIGINT SIGTERM
    wait $pid
    echo ""
    awk -F\" '/variable name/ {print $2, $6}' OFS=" " $TMP_DIR/vars.sol > $TMP_DIR/vars.sol2
    mv $TMP_DIR/vars.sol2 $TMP_DIR/vars.sol
}

BASEDIR="`dirname "$0"`"
source $BASEDIR/vpsolver_base.sh
init_vars
options="set randomseed 1234\n"
parse_args $*
generate_model
solve_model
extract_solution
