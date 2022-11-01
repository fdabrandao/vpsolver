#!/bin/bash
# This code is part of the Arc-flow Vector Packing Solver (VPSolver).
set -e
echo "Copyright (C) 2013-2022, Filipe Brandao"

solve_model(){
    if [[ -z "$solver" ]]; then
        error
    fi
    echo -e "\n>>> solving the MIP model using AMPL..."
    echo -e "Note: different parameter settings may improve the performance substantially!"
    rm -rf $TMP_DIR/vars.sol;
    (
        echo "model $model_file;"
        echo "data $data_file;"
        echo "option solver $solver;"
        echo "option ${solver}_options '$options';"
        echo "solve;"
        echo "for {i in 1.._nvars: _var[i] > 0} {printf '%d %g\n', i-1, _var[i] > $TMP_DIR/vars.sol;}"
    ) | ampl &
    local pid=$!
    trap "kill $pid &> /dev/null" SIGHUP SIGINT SIGTERM
    wait $pid
    echo ""
}

BASEDIR="`dirname "$0"`"
source $BASEDIR/vpsolver_base.sh
usage(){
    basename=`basename $0`
    echo -e "Usage:"
    echo -e "  $basename --vbp instance.vbp --solver <solver> --options <options>"
    echo -e "  $basename --mvp instance.mvp --solver <solver> --options <options>"
    echo -e "  $basename --afg graph.afg  --solver <solver> --options <options>"
}
init_vars
parse_args $*
generate_ampl_model
solve_model
extract_solution
