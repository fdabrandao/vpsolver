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
#include <set>
#include <climits>
#include <cstring>
#include <cassert>
#include <algorithm>
#include "graph.hpp"
#include "common.hpp"
using namespace std;

/* Class NodeSet */

int NodeSet::get_index(const vector<int> &lbl){    
    if(index.count(lbl)){
        return index[lbl];
    }else{
        int ind = labels.size();
        labels.push_back(lbl);
        index[lbl] = ind;
        return ind;     
    }
}

vector<int> NodeSet::get_label(int ind) const{
    assert(ind < (int)labels.size());
    return labels[ind];
}

int NodeSet::size() const{
    return labels.size();
}

void NodeSet::clear(){
    index.clear();
    labels.clear();
}    

void NodeSet::sort(){
    index.clear();
    ::sort(All(labels));
    int pos = 0;        
    ForEach(itr, labels)
        index[*itr] = pos++;
}

vector<int> NodeSet::topological_order() const{
    vector<pair<vector<int>, int> > tmp(All(index));
    vector<int> ord(tmp.size());
    int pos = 0;
    ForEach(itr, tmp)
        ord[itr->second] = pos++;
    return ord;        
}


/* Class Arc */

bool Arc::operator<(const Arc &o) const{
    return (u < o.u) || 
           (u == o.u && v < o.v) || 
           (u == o.u && v == o.v && label < o.label);
}

bool Arc::operator==(const Arc &o) const{
    return u == o.u && v == o.v && label < o.label;
}


/* Additional Functions  */

adj_list get_adj(int nv, const vector<Arc> &arcs, bool transpose){
    adj_list adj(nv);    
    ForEach(itr, arcs){
        const int u = itr->u;
        const int v = itr->v;  
        assert(u < nv && v < nv);
        if(!transpose)
            adj[u].push_back(MP(v, itr->label));
        else
            adj[v].push_back(MP(u, itr->label));
    }    
    return adj;
}

