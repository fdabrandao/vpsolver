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
#ifndef SRC_ARCFLOW_HPP_
#define SRC_ARCFLOW_HPP_

#include <ctime>
#include <set>
#include <map>
#include <vector>
#include "graph.hpp"
#include "common.hpp"
#include "instance.hpp"

class Arcflow {
 private:
    bool ready;
    std::set<Arc> AS;
    NodeSet NS;
    std::vector<int> maxW;
    std::map<std::vector<int>, int> dp;
    int go(std::vector<int> su);
    inline std::vector<int> hash(const std::vector<int> &su);
    std::vector<int> max_label;
    std::vector<int> hash_bits;
    std::vector<int> max_rep;
    std::vector<Item> sitems;
    std::vector<std::vector<int>> weights;
    int label_size;

    std::vector<int> count_max_rep(const std::vector<int> &space, int i0,
                              int sub_i0) const;
    void lift_state(const std::vector<int> &valid_opts, std::vector<int> &u, int it,
                    int ic) const;
    int min_slack(const std::vector<int> &b, int i0, int d,
                  const std::vector<int> &caps) const;
    bool is_valid(const std::vector<int> &u, const std::vector<int> &W) const;
    bool is_full(const std::vector<int> &u, const std::vector<int> &W) const;
    void relabel_graph(const std::vector<int> &labels);
    void init(const Instance &_inst);
    void init(const char *fname);
    void read(const char *fname);
    void read(FILE *fin);
    void build();
    void final_compression_step();
    void reduce_redundancy();
    void finalize();

 public:
    clock_t tstart;
    Instance inst;
    int NV;
    int NA;
    int S;
    std::vector<int> Ts;
    std::vector<Arc> A;
    int LOSS;
    explicit Arcflow(const Instance &_inst);
    explicit Arcflow(const char *fname);
    void write(const char *fname);
    void write(FILE *fout);
};

#endif  // SRC_ARCFLOW_HPP_
