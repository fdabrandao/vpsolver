#!/bin/bash
# This code is part of the Arc-flow Vector Packing Solver (VPSolver).
#
# Copyright (C) 2013-2017, Filipe Brandao
# Faculdade de Ciencias, Universidade do Porto
# Porto, Portugal. All rights reserved. E-mail: <fdabrandao@dcc.fc.up.pt>.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
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
