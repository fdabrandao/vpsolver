#!/bin/bash
# This code is part of the Arc-flow Vector Packing Solver (VPSolver).
set -e
echo "Copyright (C) 2013-2022, Filipe Brandao"

solve_model(){
    echo -e "\n>>> solving the MIP model using SCIP..."
    echo -e "Note: different parameter settings may improve the performance substantially!"
    rm -rf $TMP_DIR/vars.sol;
    (
        echo "read $model_file"
        echo -e "$options"
        echo "optimize"
        echo "write solution $TMP_DIR/vars.sol"
    ) | scip &
    local pid=$!
    trap "kill $pid &> /dev/null" SIGHUP SIGINT SIGTERM
    wait $pid
    echo ""
    tail -n+3 $TMP_DIR/vars.sol | awk '{ print $1, $2 }' > $TMP_DIR/vars.sol2
    mv $TMP_DIR/vars.sol2 $TMP_DIR/vars.sol
}

BASEDIR="`dirname "$0"`"
source $BASEDIR/vpsolver_base.sh
init_vars
options=""
parse_args $*
generate_model
solve_model
extract_solution
