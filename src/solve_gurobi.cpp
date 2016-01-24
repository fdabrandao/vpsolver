/**
This code is part of the Arc-flow Vector Packing Solver (VPSolver).

Copyright (C) 2013-2016, Filipe Brandao
Faculdade de Ciencias, Universidade do Porto
Porto, Portugal. All rights reserved. E-mail: <fdabrandao@dcc.fc.up.pt>.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
**/
#include <cstdio>
#include <cassert>
#include <string>
#include "gurobi_c.h"
#include "gurobi_c++.h"
using namespace std;

int main(int argc, char *argv[]){
    printf("Copyright (C) 2013-2016, Filipe Brandao\n");
    setvbuf(stdout, NULL, _IONBF, 0);
    if(argc < 2 || argc > 3){
        printf("Usage: solve_gurobi model.mps|model.lp [vars.sol]\n");
        return 1;
    }

    GRBEnv env = GRBEnv();
    GRBModel model = GRBModel(env, argv[1]);

    model.getEnv().set(GRB_IntParam_OutputFlag, 1);
    model.getEnv().set(GRB_IntParam_Threads, 1);
    model.getEnv().set(GRB_IntParam_Presolve, 1);
    model.getEnv().set(GRB_IntParam_Method, 2);
    model.getEnv().set(GRB_IntParam_MIPFocus, 1);
    //model.getEnv().set(GRB_IntParam_RINS, 10);
    model.getEnv().set(GRB_DoubleParam_Heuristics, 1);
    model.getEnv().set(GRB_DoubleParam_MIPGap, 0);
    model.getEnv().set(GRB_DoubleParam_MIPGapAbs, 1-1e-5);
    //model.getEnv().set(GRB_DoubleParam_ImproveStartTime, 60);
    //model.getEnv().set(GRB_DoubleParam_ImproveStartGap, 1);

    model.optimize();

    if(argc == 3){
        FILE *fout = fopen(argv[2], "w");
        assert(fout != NULL);

        GRBVar* v = model.getVars();
        int nvars = model.get(GRB_IntAttr_NumVars);
        for (int i = 0; i < nvars; i++){
            double value = v[i].get(GRB_DoubleAttr_X);
            if(value != 0){
                string name = v[i].get(GRB_StringAttr_VarName);
                fprintf(fout, "%s %.6f\n", name.c_str(), value);
            }
        }
        fclose(fout);
    }
    return 0;
}
