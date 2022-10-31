#!/bin/bash
# This code is part of the Arc-flow Vector Packing Solver (VPSolver).
set -e
echo "Copyright (C) 2013-2022, Filipe Brandao"

solve_model(){
    echo -e "\n>>> solving the MIP model using COIN-OR CBC..."
    echo -e "Note: different parameter settings may improve the performance substantially!"
    if ! [ -x "$(command -v stdbuf)" ]; then
        cbc $model_file $options -solve -solu $TMP_DIR/sol.out &
    else
        stdbuf -i0 -o0 -e0 cbc $model_file $options -solve -solu $TMP_DIR/sol.out &
    fi
    local pid=$!
    trap "kill $pid &> /dev/null" SIGHUP SIGINT SIGTERM
    wait $pid
    tail -n +2 $TMP_DIR/sol.out | awk '{ print $2, $3 }' > $TMP_DIR/vars.sol
}

BASEDIR="`dirname "$0"`"
source $BASEDIR/vpsolver_base.sh
init_vars
options="-cuts off -randomSeed 1234 -randomCbcSeed 1234"
parse_args $*
generate_model
solve_model
extract_solution
