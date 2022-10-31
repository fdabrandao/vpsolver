#!/bin/bash
# This code is part of the Arc-flow Vector Packing Solver (VPSolver).
set -e
echo "Copyright (C) 2013-2022, Filipe Brandao"

solve_model(){
    echo -e "\n>>> solving the MIP model using GLPK..."
    echo -e "Note: different parameter settings may improve the performance substantially!"
    if [[ $model_file =~ \.mps$ ]]; then
        glpsol --mps $model_file $options -o $TMP_DIR/sol.out &
        local pid=$!
        trap "kill $pid &> /dev/null" SIGHUP SIGINT SIGTERM
        wait $pid
    else
        glpsol --lp $model_file $options -o $TMP_DIR/sol.out &
        local pid=$!
        trap "kill $pid &> /dev/null" SIGHUP SIGINT SIGTERM
        wait $pid
    fi
    sed -n '/Column name/,/^$/p' $TMP_DIR/sol.out > $TMP_DIR/sol.out2
    mv $TMP_DIR/sol.out2 $TMP_DIR/sol.out
    sed '1,2d' $TMP_DIR/sol.out > $TMP_DIR/sol.out2
    mv $TMP_DIR/sol.out2 $TMP_DIR/sol.out
    sed ':a;N;$!ba;s/\n\s\{20\}/ /g' $TMP_DIR/sol.out > $TMP_DIR/sol.out2
    mv $TMP_DIR/sol.out2 $TMP_DIR/sol.out
    sed 's/\*/ /g' $TMP_DIR/sol.out > $TMP_DIR/sol.out2
    mv $TMP_DIR/sol.out2 $TMP_DIR/sol.out
    tr '\n' '$' < $TMP_DIR/sol.out | sed 's/$        //g' | tr '$' '\n' > $TMP_DIR/sol.out2
    mv $TMP_DIR/sol.out2 $TMP_DIR/sol.out
    awk '{ if ( $3 ~ /^[0-9][^\s]*$/  ){ print $2, $3 }else{ print $2, $4 } }' $TMP_DIR/sol.out > $TMP_DIR/vars.sol
}

BASEDIR="`dirname "$0"`"
source $BASEDIR/vpsolver_base.sh
init_vars
options="--seed 1234"
parse_args $*
generate_model
solve_model
extract_solution
