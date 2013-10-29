/**
Copyright (C) 2013, Filipe Brandao
Faculdade de Ciencias, Universidade do Porto
Porto, Portugal. All rights reserved. E-mail: <fdabrandao@dcc.fc.up.pt>.
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

