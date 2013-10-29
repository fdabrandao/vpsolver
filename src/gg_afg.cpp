/**
Copyright (C) 2013, Filipe Brandao
Faculdade de Ciencias, Universidade do Porto
Porto, Portugal. All rights reserved. E-mail: <fdabrandao@dcc.fc.up.pt>.
**/
#include <cstdio>
#include <cassert>
#include <cstring>
#include <cstdlib>
#include "gurobi_c.h"
#include "gurobi_c++.h"
#include "common.hpp"
#include "arcflow_mkp.hpp"
using namespace std;

#define EPSILON 1e-6

void solve(Instance inst, bool hsol = false){    
    clock_t t0 = CURTIME;
    
    ArcflowMKP graph(inst);    
    const vector<Item> &items = inst.items;   
    
    GRBEnv* env = new GRBEnv();
    GRBModel master = GRBModel(*env);    
    master.set(GRB_StringAttr_ModelName, "GG");
    master.getEnv().set(GRB_IntParam_OutputFlag, 0);
    master.getEnv().set(GRB_IntParam_Threads, 1);          
    master.getEnv().set(GRB_IntParam_Method, 0); 

    GRBConstr rows[inst.m];
    for(int i = 0; i < inst.m; i++){
        GRBLinExpr lin = 0;
        rows[i] = master.addConstr(lin >= items[i].demand);
    }
    master.update();
        
    vector<GRBVar> vars;
    for(int i = 0; i < inst.m; i++){        
        GRBColumn col = GRBColumn();        
        col.addTerm(1, rows[i]);
        vars.push_back(master.addVar(0, GRB_INFINITY, 1, GRB_CONTINUOUS, col));
    }    
    
    printf("m: %d\n", inst.m);
    vector<double> values(inst.m);
    for(int itr = inst.m; ; itr++){
        master.optimize();
        printf("%d: %.6f (%.2fs)\n", itr, master.get(GRB_DoubleAttr_ObjVal), TIMEDIF(t0));        
        for(int i = 0; i < inst.m; i++)
            values[i] = rows[i].get(GRB_DoubleAttr_Pi);            

        vector<int_pair> sol = graph.knapsack(values, 1+EPSILON);
        if(sol.empty()) break;
        
        GRBColumn col = GRBColumn();        
        ForEach(itr, sol) col.addTerm(itr->second, rows[itr->first]);
        
        vars.push_back(master.addVar(0, GRB_INFINITY, 1, GRB_CONTINUOUS, col));
        master.update();
    }
        
    printf("zlp: %.6f\n", master.get(GRB_DoubleAttr_ObjVal));
    printf("nvars: %d\n", master.get(GRB_IntAttr_NumVars));
    printf("time: %.2fs\n", TIMEDIF(t0));
    
    if(hsol){ // find an heuristic solution if hsol = true
        ForEach(itr, vars)
            itr->set(GRB_CharAttr_VType, GRB_INTEGER);
        
        master.getEnv().set(GRB_IntParam_OutputFlag, 1);
        master.getEnv().set(GRB_IntParam_Threads, 1);
        //master.getEnv().set(GRB_IntParam_Presolve, 1);       
        //master.getEnv().set(GRB_IntParam_Method, 2);
        master.getEnv().set(GRB_IntParam_MIPFocus, 1);
        master.getEnv().set(GRB_DoubleParam_Heuristics, 1);
        master.getEnv().set(GRB_DoubleParam_MIPGap, 0);
        master.getEnv().set(GRB_DoubleParam_MIPGapAbs, 1-1e-5);  
        
        master.optimize();
        printf("Total run time: %.2f seconds\n", TIMEDIF(t0));
    }
    
    free(env);
}

int main(int argc, char *argv[]){
    printf("Copyright (C) 2013, Filipe Brandao\n");
    printf("Usage: gg_afg instance.vbp [method:-2] [binary:0] [htlimit:0]\n");
    setvbuf(stdout, NULL, _IONBF, 0);
    assert(argc >= 2 && argc <= 5);    

    Instance inst(argv[1]);                      
    if(argc >= 3) {
        inst.method = atoi(argv[2]);
        assert(inst.method >= MIN_METHOD && inst.method <= MAX_METHOD);
    }
    if(argc >= 4){
        inst.binary = atoi(argv[3]);        
    }
    
    if(argc >= 5){
        int t = atoi(argv[4]);
        solve(inst, t != 0);        
    }else{
        solve(inst);    
    }
    return 0;
}


