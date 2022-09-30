#!/bin/bash
# This code is part of the Arc-flow Vector Packing Solver (VPSolver).
#
# Copyright (C) 2013-2016, Filipe Brandao <fdabrandao@gmail.com>
BASEDIR=`dirname $0`
cd $BASEDIR
CMD="$0 $*"

usage(){
    echo -e "Usage:"
    echo -e "  $0 --venv venv_dir [-p python_exe]"
}

error(){
    echo "Command line: "$CMD
    echo "Error: invalid arguments."
    usage
    exit 1
}

pyexec="";
venv="venv";

while true;
do
  case "$1" in
    -p)
        if [[ -n "$2" ]]; then pyexec=$2; else error; fi
        shift 2;;
    --venv)
        if [[ -n "$2" ]]; then venv=$2; else error; fi
        shift 2;;
    *)
        if [[ -n "$1" ]]; then error; else break; fi
  esac
done

if [[ -z "$venv" ]]; then
    error
fi

if [[ -n "$pyexec" ]]; then
    virtualenv --system-site-packages -p $pyexec $venv || exit 1;
else
    virtualenv --system-site-packages $venv || exit 1;
fi

rm -rf build *.egg-info
source $venv/bin/activate || exit 1
python --version || exit 1
pip install --upgrade --ignore-installed -r requirements.txt || exit 1
pip install --upgrade --ignore-installed --pre pympl || exit 1
pip install --upgrade --ignore-installed --no-deps . || exit 1
cd examples || exit 1
py.test -v --cov pyvpsolver || exit 1
deactivate || exit 1
