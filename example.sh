#!/bin/sh
echo "***************************************"
echo "* Example 1:                          *"
echp "* > bin/vpsolver example.vbp            *"
echo "***************************************"
bin/vpsolver example.vbp
echo "\n\n"

echo "************************************************"
echo "* Example 2:                                   *"
echo "* > bin/vbp2afg example.vbp graph.afg          *"
echo "* > bin/afg2mps graph.afg model.mps            *"
echo "* > bin/solve_gurobi model.mps vars.sol        *"
echo "* > bin/vbpsol graph.afg vars.sol              *"
echo "************************************************"
bin/vbp2afg example.vbp graph.afg
bin/afg2mps graph.afg model.mps
bin/solve_gurobi model.mps vars.sol
bin/vbpsol graph.afg vars.sol

echo "\n\n"

echo "************************************************"
echo "* Example 3:                                   *"
echo "* > bin/vbp2afg example.vbp graph.afg          *"
echo "* > bin/afg2lp graph.afg model.lp              *"
echo "* > bin/solve_glpk model.lp vars.sol           *"
echo "* > bin/vbpsol graph.afg vars.sol              *"
echo "************************************************"
bin/vbp2afg example.vbp graph.afg
bin/afg2lp graph.afg model.lp
bin/solve_glpk model.lp vars.sol
bin/vbpsol graph.afg vars.sol


