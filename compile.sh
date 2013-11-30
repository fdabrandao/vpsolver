#!/bin/sh

make clean

echo "\ncompiling bin/vpsolver..."
make bin/vpsolver 

echo "\ncompiling bin/vbp2afg..."
make bin/vbp2afg

echo "\ncompiling bin/afg2mps..."
make bin/afg2mps

echo "\ncompiling bin/afg2lp..."
make bin/afg2lp

echo "\ncompiling bin/solve_gurobi..."
make bin/solve_gurobi

echo "\ncompiling bin/solve_glpk..."
make bin/solve_glpk

echo "\ncompiling bin/vbpsol..."
make bin/vbpsol

echo "\ncompiling bin/gg_afg..."
make bin/gg_afg

