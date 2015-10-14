#!/bin/bash
# This code is part of the Arc-flow Vector Packing Solver (VPSolver).
#
# Copyright (C) 2013-2015, Filipe Brandao
# Faculdade de Ciencias, Universidade do Porto
# Porto, Portugal. All rights reserved. E-mail: <fdabrandao@dcc.fc.up.pt>.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
BASEDIR=`dirname $0`
cd $BASEDIR

if ! [[ -x bin/vbp2afg && -x bin/afg2mps && -x bin/afg2lp && -x bin/vbpsol ]];
then
    bash build.sh
fi;
pip install -r requirements.txt
pip install --upgrade .
