#!/bin/bash
# This code is part of the Arc-flow Vector Packing Solver (VPSolver).
#
# Copyright (C) 2013-2021, Filipe Brandao <fdabrandao@gmail.com>
BASEDIR=`dirname $0`
cd $BASEDIR
CMD="$0 $*"

usage(){
    echo -e "Usage:"
    echo -e "  $0 [--venv venv_dir] [--port app_port]"
}

error(){
    echo "Command line: "$CMD
    echo "Error: invalid arguments."
    usage
    exit 1
}

venv=""
port=5555

while true;
do
    case "$1" in
    --venv)
        if [[ -n "$2" ]]; then venv=$2; else error; fi
        shift 2;;
    --port)
        if [[ -n "$2" ]]; then port=$2; else error; fi
        shift 2;;
    *)
        if [[ -n "$1" ]]; then error; else break; fi
    esac
done

if [[ -n "$venv" ]]; then
    source $venv/bin/activate;
fi;

ifconfig eth0 || exit 1
python --version || exit 1
python -m pyvpsolver.webapp.app $port || exit 1
