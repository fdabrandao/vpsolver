#!/bin/sh
BASEDIR=`dirname $0`
cd $BASEDIR

echo "******************************"
echo "* Example 1:                 *"
echp "* > bin/vpsolver example.vbp *"
echo "******************************"
bin/vpsolver example.vbp
echo "\n\n"

echo "*****************************************"
echo "* Example 2:                            *"
echo "* > bin/vbp2afg example.vbp graph.afg   *"
echo "* > bin/afg2mps graph.afg model.mps     *"
echo "* > bin/solve_gurobi model.mps vars.sol *"
echo "* > bin/vbpsol graph.afg vars.sol       *"
echo "*****************************************"
bin/vbp2afg example.vbp tmp/graph.afg
bin/afg2mps tmp/graph.afg tmp/model.mps
bin/solve_gurobi tmp/model.mps tmp/vars.sol
bin/vbpsol tmp/graph.afg tmp/vars.sol

echo "\n\n"

echo "***************************************"
echo "* Example 3:                          *"
echo "* > bin/vbp2afg example.vbp graph.afg *"
echo "* > bin/afg2lp graph.afg model.lp     *"
echo "* > bin/solve_glpk model.lp vars.sol  *"
echo "* > bin/vbpsol graph.afg vars.sol     *"
echo "***************************************"
bin/vbp2afg example.vbp tmp/graph.afg
bin/afg2lp tmp/graph.afg tmp/model.lp
bin/solve_glpk tmp/model.lp tmp/vars.sol
bin/vbpsol tmp/graph.afg tmp/vars.sol


