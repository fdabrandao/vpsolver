/**
Copyright (C) 2013, Filipe Brandao
Faculdade de Ciencias, Universidade do Porto
Porto, Portugal. All rights reserved. E-mail: <fdabrandao@dcc.fc.up.pt>.
**/
#ifndef _GRAPH_HPP_
#define _GRAPH_HPP_

#include <map>
#include <ctime>
#include <set>
#include <map>
#include <vector>
#include "common.hpp"
using namespace std;

typedef vector<vector<int_pair> > adj_list;

class NodeSet{
private:
    map<vector<int>, int> index;
    vector<vector<int> > labels;
public:
    int get_index(const vector<int> &lbl);
    vector<int> get_label(int ind) const;    
    int size() const;
    void clear();    
    void sort();    
    vector<int> topological_order() const;
};

class Arc{
public:
    int u;
    int v;
    int label;
    Arc(const int &_u = -1, const int &_v = -1, int _label = -1):
        u(_u), v(_v), label(_label){}
    bool operator<(const Arc &o) const;
    bool operator==(const Arc &o) const;
};

adj_list get_adj(int nv, const vector<Arc> &arcs, bool transpose = false);

#endif

