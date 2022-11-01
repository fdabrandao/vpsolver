#!/bin/bash
BASEDIR=`dirname "$0"`
cd $BASEDIR

TMP_DIR=`mktemp -d -t XXXXXXXXXX`
trap "rm -rf $TMP_DIR" EXIT

PATH="../bin/:../scripts/:$PATH"

echo "**********************************************************"
echo "* Example 6:                                             *"
echo "* > ./vpsolver_ampl.sh --vbp instance.vbp              *"
echo "**********************************************************"
vpsolver_ampl.sh --vbp instance.vbp --solver gurobi --options "outlev=1"
