/**
Copyright (C) 2013, Filipe Brandao
Faculdade de Ciencias, Universidade do Porto
Porto, Portugal. All rights reserved. E-mail: <fdabrandao@dcc.fc.up.pt>.
**/
#include <cstdio>
#include <cassert>
#include <string>
#include "gurobi_c.h"
#include "gurobi_c++.h"
using namespace std;

int main(int argc, char *argv[]){     
    printf("Copyright (C) 2013, Filipe Brandao\n");
    printf("Usage: solve_gurobi model.mps|model.lp [vars.sol]\n");    
    setvbuf(stdout, NULL, _IONBF, 0);
    assert(argc == 2 || argc == 3);
                
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

