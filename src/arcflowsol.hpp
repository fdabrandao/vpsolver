/**
Copyright (C) 2013, Filipe Brandao
Faculdade de Ciencias, Universidade do Porto
Porto, Portugal. All rights reserved. E-mail: <fdabrandao@dcc.fc.up.pt>.
**/
#ifndef _ARCFLOWSOL_HPP_
#define _ARCFLOWSOL_HPP_

#include <ctime>
#include <set>
#include <map>
#include <vector>
#include "graph.hpp"
#include "common.hpp"
#include "instance.hpp"
using namespace std; 

class ArcflowSol{
private:
    map<Arc, int> flow;     
    int S, T;
    bool binary;
    
    vector<pair<int, vector<int_pair> > > remove_excess(
        const vector<pair<int, vector<int> > > &sol, vector<int> dem) const;
        
    bool is_valid(vector<pair<int, vector<int_pair> > > sol,
        const Instance &inst) const;        

public:
    ArcflowSol(const map<Arc, int> &_flow, int _S, int _T, bool _binary = false):
        flow(_flow), S(_S), T(_T), binary(_binary){}

    vector<pair<int, vector<int_pair> > > extract_solution(
        const vector<int> &dem);
        
    void print_solution(const Instance &inst, bool print_inst, bool validate);        
};

#endif

