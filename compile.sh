#!/bin/bash
BASEDIR=`dirname $0`
cd $BASEDIR

make clean >compile.log 2>&1 

echo "mandatory:"

echo -n "  bin/vbp2afg"
make bin/vbp2afg >>compile.log 2>&1 
if [[ $? == 0 ]] ; then
    echo " [OK]"
else    
    echo " [Failed]"
fi

echo -n "  bin/afg2mps"
make bin/afg2mps >>compile.log 2>&1
if [[ $? == 0 ]] ; then
    echo " [OK]"
else    
    echo " [Failed]"
fi

echo -n "  bin/afg2lp"
make bin/afg2lp >>compile.log 2>&1
if [[ $? == 0 ]] ; then
    echo " [OK]"
else    
    echo " [Failed]"
fi

echo -n "  bin/vbpsol"
make bin/vbpsol >>error.log 2>&1
if [[ $? == 0 ]] ; then
    echo " [OK]"
else    
    echo " [Failed]"
fi

echo "nonmandatory:"

echo -n "  bin/vpsolver"
make bin/vpsolver >>compile.log 2>&1 
if [[ $? == 0 ]] ; then
    echo " [OK]"
else    
    echo " [Failed]"
fi

echo -n "  bin/solve_gurobi"
make bin/solve_gurobi >>compile.log 2>&1
if [[ $? == 0 ]] ; then
    echo " [OK]"
else    
    echo " [Failed]"
fi

echo -n "  bin/solve_glpk"
make bin/solve_glpk >>compile.log 2>&1
if [[ $? == 0 ]] ; then
    echo " [OK]"
else    
    echo " [Failed]"
fi

echo -n "  bin/gg_afg"
make bin/gg_afg >>error.log 2>&1
if [[ $? == 0 ]] ; then
    echo " [OK]"
else    
    echo " [Failed]"
fi

