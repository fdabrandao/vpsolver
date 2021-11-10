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

typedef std::pair<int, std::vector<int>> pattern_int;
typedef std::pair<int, std::vector<int_pair>> pattern_pair;

class ArcflowSol {
 private:
    Instance inst;
    std::map<Arc, int> flow;
    int S;
    std::vector<int> Ts;
    int LOSS;
    int objvalue;
    std::vector<int> nbins;
    std::vector<std::vector<pattern_pair>> sols;

    std::vector<pattern_pair> extract_solution(std::vector<int> *_dem, int T);

    std::vector<pattern_pair> remove_excess(const std::vector<pattern_int> &sol,
                                       std::vector<int> *_dem) const;

    bool is_valid(const std::vector<pattern_pair> &sol, int btype) const;

 public:
    ArcflowSol(const Instance &_inst, const std::map<Arc, int> &_flow, int _S,
               const std::vector<int> &_Ts, int _LOSS);

    void print_solution(bool print_inst, bool pyout);
};

#endif  // SRC_ARCFLOWSOL_HPP_
