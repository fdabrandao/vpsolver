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
#include <set>
#include <vector>
#include <climits>
#include <cstring>
#include <algorithm>
#include "graph.hpp"
#include "common.hpp"

/* Class NodeSet */

int NodeSet::get_index(const std::vector<int> &lbl) {
    if (index.count(lbl)) {
        return index[lbl];
    } else {
        int ind = labels.size();
        labels.push_back(lbl);
        index[lbl] = ind;
        return ind;
    }
}

std::vector<int> NodeSet::get_label(int ind) const {
    throw_assert(ind < static_cast<int>(labels.size()));
    return labels[ind];
}

int NodeSet::size() const {
    return labels.size();
}

void NodeSet::clear() {
    index.clear();
    labels.clear();
}

void NodeSet::sort() {
    index.clear();
    std::sort(all(labels));
    int pos = 0;
    for (const std::vector<int> &lbl : labels) {
        index[lbl] = pos++;
    }
}

std::vector<int> NodeSet::topological_order() const {
    std::vector<int> ord(index.size());
    int pos = 0;
    for (const auto &kvpair : index) {
        ord[kvpair.second] = pos++;
    }
    return ord;
}


/* Class Arc */

bool Arc::operator<(const Arc &o) const {
    return (u < o.u) ||
           (u == o.u && v < o.v) ||
           (u == o.u && v == o.v && label < o.label);
}

bool Arc::operator==(const Arc &o) const {
    return u == o.u && v == o.v && label == o.label;
}


/* Additional Functions  */

adj_list get_adj(int nv, const std::vector<Arc> &arcs, bool transpose) {
    adj_list adj(nv);
    for (const Arc &a : arcs) {
        throw_assert(a.u < nv && a.v < nv);
        if (!transpose) {
            adj[a.u].push_back(MP(a.v, a.label));
        } else {
            adj[a.v].push_back(MP(a.u, a.label));
        }
    }
    return adj;
}
