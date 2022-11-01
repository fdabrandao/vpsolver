#!/bin/bash
BASEDIR=`dirname "$0"`
cd $BASEDIR

TMP_DIR=`mktemp -d -t XXXXXXXXXX`
trap "rm -rf $TMP_DIR" EXIT

PATH="../bin/:../scripts/:$PATH"

echo "**********************************************************"
echo "* Example 1:                                             *"
echo "* > vpsolver instance.vbp                                *"
echo "**********************************************************"
vpsolver instance.vbp

echo -e "\n\n"

echo "**********************************************************"
echo "* Example 2:                                             *"
echo "* > vbp2afg instance.vbp graph.afg                       *"
echo "* > afg2mps graph.afg model.mps                          *"
echo "* > vpsolver_coinor.sh --mps model.mps --wsol vars.sol   *"
echo "* > vbpsol graph.afg vars.sol                            *"
echo "**********************************************************"
vbp2afg instance.vbp $TMP_DIR/graph.afg
afg2mps $TMP_DIR/graph.afg $TMP_DIR/model.mps
vpsolver_coinor.sh --mps $TMP_DIR/model.mps --wsol $TMP_DIR/vars.sol
vbpsol $TMP_DIR/graph.afg $TMP_DIR/vars.sol

echo -e "\n\n"

echo "**********************************************************"
echo "* Example 3:                                             *"
echo "* > vbp2afg instance.vbp graph.afg                       *"
echo "* > afg2lp graph.afg model.lp                            *"
echo "* > vpsolver_coinor.sh --lp model.lp --wsol vars.sol       *"
echo "* > vbpsol graph.afg vars.sol                            *"
echo "**********************************************************"
vbp2afg instance.vbp $TMP_DIR/graph.afg
afg2lp $TMP_DIR/graph.afg $TMP_DIR/model.lp
vpsolver_coinor.sh --lp $TMP_DIR/model.lp --wsol $TMP_DIR/vars.sol
vbpsol $TMP_DIR/graph.afg $TMP_DIR/vars.sol

echo -e "\n\n"

echo "**********************************************************"
echo "* Example 4:                                             *"
echo "* > vbp2afg instance.vbp graph.afg                       *"
echo "* > afg2lp graph.afg model.lp                            *"
echo "* > vpsolver_coinor.sh --lp model.lp --afg graph.afg       *"
echo "**********************************************************"
vbp2afg instance.vbp $TMP_DIR/graph.afg
afg2lp $TMP_DIR/graph.afg $TMP_DIR/model.lp
vpsolver_coinor.sh --lp $TMP_DIR/model.lp --afg $TMP_DIR/graph.afg

echo -e "\n\n"

echo "**********************************************************"
echo "* Example 5:                                             *"
echo "* > vbp2afg instance.vbp graph.afg                       *"
echo "* > afg2mps graph.afg model.mps                          *"
echo "* > vpsolver_coinor.sh --mps model.mps --afg graph.afg   *"
echo "**********************************************************"
vbp2afg instance.vbp $TMP_DIR/graph.afg
afg2mps $TMP_DIR/graph.afg $TMP_DIR/model.mps
vpsolver_coinor.sh --mps $TMP_DIR/model.mps --afg $TMP_DIR/graph.afg

echo -e "\n\n"

echo "**********************************************************"
echo "* Example 6:                                             *"
echo "* > ./vpsolver_coinor.sh --vbp instance.vbp              *"
echo "**********************************************************"
vpsolver_coinor.sh --vbp instance.vbp
