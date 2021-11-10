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
#ifndef SRC_GRAPH_HPP_
#define SRC_GRAPH_HPP_

#include <ctime>
#include <set>
#include <map>
#include <vector>
#include "common.hpp"

typedef std::vector<std::vector<int_pair>> adj_list;

class NodeSet {
 private:
    std::map<std::vector<int>, int> index;
    std::vector<std::vector<int>> labels;
 public:
    int get_index(const std::vector<int> &lbl);
    std::vector<int> get_label(int ind) const;
    int size() const;
    void clear();
    void sort();
    std::vector<int> topological_order() const;
};

class Arc {
 public:
    int u;
    int v;
    int label;
    explicit Arc(const int &_u = -1, const int &_v = -1, int _label = -1):
        u(_u), v(_v), label(_label) {}
    bool operator<(const Arc &o) const;
    bool operator==(const Arc &o) const;
};

adj_list get_adj(int nv, const std::vector<Arc> &arcs, bool transpose = false);

#endif  // SRC_GRAPH_HPP_
