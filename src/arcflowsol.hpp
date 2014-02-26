/**
This code is part of the Arc-flow Vector Packing Solver (VPSolver).

Copyright (C) 2013-2014, Filipe Brandao
Faculdade de Ciencias, Universidade do Porto
Porto, Portugal. All rights reserved. E-mail: <fdabrandao@dcc.fc.up.pt>.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
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

