#!/bin/bash
BASEDIR=`dirname $0`
cd $BASEDIR
TMP_DIR=`mktemp -d -t XXXXXXXXXX`
trap "rm -rf $TMP_DIR" EXIT

echo "**********************************************************"
echo "* Example 1:                                             *"
echo "* > bin/vpsolver instance.vbp                            *"
echo "**********************************************************"
../bin/bin/vpsolver instance.vbp

echo -e "\n\n"

echo "**********************************************************"
echo "* Example 2:                                             *"
echo "* > bin/vbp2afg instance.vbp graph.afg                   *"
echo "* > bin/afg2mps graph.afg model.mps                      *"
echo "* > bin/solve_gurobi model.mps vars.sol                  *"
echo "* > bin/vbpsol graph.afg vars.sol                        *"
echo "**********************************************************"
../bin/bin/vbp2afg instance.vbp $TMP_DIR/graph.afg
../bin/bin/afg2mps $TMP_DIR/graph.afg $TMP_DIR/model.mps
../bin/bin/solve_gurobi $TMP_DIR/model.mps $TMP_DIR/vars.sol
../bin/bin/vbpsol $TMP_DIR/graph.afg $TMP_DIR/vars.sol

echo -e "\n\n"

echo "**********************************************************"
echo "* Example 3:                                             *"
echo "* > bin/vbp2afg instance.vbp graph.afg                   *"
echo "* > bin/afg2lp graph.afg model.lp                        *"
echo "* > bin/solve_glpk model.lp vars.sol                     *"
echo "* > bin/vbpsol graph.afg vars.sol                        *"
echo "**********************************************************"
../bin/bin/vbp2afg instance.vbp $TMP_DIR/graph.afg
../bin/bin/afg2lp $TMP_DIR/graph.afg $TMP_DIR/model.lp
../bin/bin/solve_glpk $TMP_DIR/model.lp $TMP_DIR/vars.sol
../bin/bin/vbpsol $TMP_DIR/graph.afg $TMP_DIR/vars.sol

echo -e "\n\n"

echo "**********************************************************"
echo "* Example 4:                                             *"
echo "* > bin/vbp2afg instance.vbp graph.afg                   *"
echo "* > bin/afg2lp graph.afg model.lp                        *"
echo "* > ./vpsolver_glpk.sh --lp model.lp --afg graph.afg     *"
echo "**********************************************************"
../bin/bin/vbp2afg instance.vbp $TMP_DIR/graph.afg
../bin/bin/afg2lp $TMP_DIR/graph.afg $TMP_DIR/model.lp
scripts/vpsolver_glpk.sh --lp $TMP_DIR/model.lp --afg $TMP_DIR/graph.afg

echo -e "\n\n"

echo "**********************************************************"
echo "* Example 5:                                             *"
echo "* > bin/vbp2afg instance.vbp graph.afg                   *"
echo "* > bin/afg2mps graph.afg model.mps                      *"
echo "* > ./vpsolver_gurobi.sh --mps model.mps --afg graph.afg *"
echo "**********************************************************"
../bin/bin/vbp2afg instance.vbp $TMP_DIR/graph.afg
../bin/bin/afg2mps $TMP_DIR/graph.afg $TMP_DIR/model.mps
../bin/scripts/vpsolver_gurobi.sh --mps $TMP_DIR/model.mps --afg $TMP_DIR/graph.afg

echo -e "\n\n"

echo "**********************************************************"
echo "* Example 6:                                             *"
echo "* > ./vpsolver_gurobi.sh --vbp instance.vbp              *"
echo "**********************************************************"
../bin/scripts/vpsolver_gurobi.sh --vbp instance.vbp

