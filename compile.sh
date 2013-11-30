#!/bin/bash
BASEDIR=`dirname $0`
cd $BASEDIR

make clean >compile.log 2>&1 

echo "mandatory:"

echo -n "  vbp2afg "
make bin/vbp2afg >>compile.log 2>&1 
if [[ $? == 0 ]]; then echo "[OK]";
else echo "[Failed]"; fi

echo -n "  afg2mps "
make bin/afg2mps >>compile.log 2>&1
if [[ $? == 0 ]]; then echo "[OK]";
else echo "[Failed]"; fi

echo -n "  afg2lp  "
make bin/afg2lp >>compile.log 2>&1
if [[ $? == 0 ]]; then echo "[OK]";
else echo "[Failed]"; fi

echo -n "  vbpsol  "
make bin/vbpsol >>compile.log 2>&1
if [[ $? == 0 ]]; then echo "[OK]";
else echo "[Failed]"; fi

echo "optional:"

echo -n "  vpsolver "
make bin/vpsolver >>compile.log 2>&1 
if [[ $? == 0 ]]; then echo "[OK]";
else echo "[Failed]"; fi

echo -n "  gg_afg   "
make bin/gg_afg >>compile.log 2>&1
if [[ $? == 0 ]]; then echo "[OK]";
else echo "[Failed]"; fi

echo -n "  solve_gurobi "
make bin/solve_gurobi >>compile.log 2>&1
if [[ $? == 0 ]]; then echo "[OK]";
else echo "[Failed]"; fi

echo -n "  solve_glpk   "
make bin/solve_glpk >>compile.log 2>&1
if [[ $? == 0 ]]; then echo "[OK]";
else echo "[Failed]"; fi



