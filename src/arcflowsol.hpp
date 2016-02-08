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
#ifndef SRC_ARCFLOWSOL_HPP_
#define SRC_ARCFLOWSOL_HPP_

#include <ctime>
#include <set>
#include <map>
#include <vector>
#include <utility>
#include "graph.hpp"
#include "common.hpp"
#include "instance.hpp"
using namespace std;

typedef pair<int, vector<int>> pattern_int;
typedef pair<int, vector<int_pair>> pattern_pair;

class ArcflowSol {
 private:
    Instance inst;
    map<Arc, int> flow;
    int S;
    vector<int> Ts;
    int LOSS;
    bool binary;

    vector<pattern_pair> remove_excess(const vector<pattern_int> &sol,
                                       vector<int> &dem) const;

    bool is_valid(const vector<pattern_pair> &sol, const Instance &inst,
                  vector<int> dem, int btype) const;

 public:
    ArcflowSol(const Instance &_inst, const map<Arc, int> &_flow, int _S,
               const vector<int> &_Ts, int _LOSS, bool _binary = false):
        inst(_inst), flow(_flow), S(_S), Ts(_Ts), LOSS(_LOSS),
        binary(_binary) {}

    vector<pattern_pair> extract_solution(vector<int> &dem, int T);

    void print_solution(
        const Instance &inst, bool print_inst, bool pyout, bool validate);
};

#endif  // SRC_ARCFLOWSOL_HPP_
