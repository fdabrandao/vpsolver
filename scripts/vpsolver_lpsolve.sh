#!/bin/bash
# This code is part of the Arc-flow Vector Packing Solver (VPSolver).
set -e
echo "Copyright (C) 2013-2022, Filipe Brandao"

solve_model(){
    echo -e "\n>>> solving the MIP model using lp_solve..."
    echo -e "Note: different parameter settings may improve the performance substantially!"
    if [[ $model_file =~ \.mps$ ]]; then
        lp_solve -mps $model_file $options > $TMP_DIR/sol.out  &
        local pid=$!
        trap "kill $pid &> /dev/null" SIGHUP SIGINT SIGTERM
        wait $pid
    else
        echo -e "Note: lp_solve requires xli_CPLEX to read CPLEX lp models"
        lp_solve -rxli xli_CPLEX $model_file $options > $TMP_DIR/sol.out &
        local pid=$!
        trap "kill $pid &> /dev/null" SIGHUP SIGINT SIGTERM
        wait $pid
    fi
    sed -e '1,/variables:/d' $TMP_DIR/sol.out > $TMP_DIR/vars.sol
}

BASEDIR="`dirname "$0"`"
source $BASEDIR/vpsolver_base.sh
init_vars
options=""
parse_args $*
generate_model
solve_model
extract_solution
