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
using namespace std;

class Arcflow {
 private:
    bool ready;
    set<Arc> AS;
    NodeSet NS;
    vector<int> maxW;
    map<vector<int>, int> dp;
    int go(vector<int> su);
    inline vector<int> hash(const vector<int> &su);
    vector<int> max_label;
    vector<int> hash_bits;
    vector<int> max_rep;
    vector<vector<int>> weights;
    int label_size;

    vector<int> count_max_rep(const vector<int> &space, int i0,
                              int sub_i0) const;
    void lift_state(const vector<int> &valid_opts, vector<int> &u, int it,
                    int ic) const;
    int min_slack(const vector<int> &b, int i0, int d,
                  const vector<int> &caps) const;
    bool is_valid(const vector<int> &u, const vector<int> &W) const;
    bool is_full(const vector<int> &u, const vector<int> &W) const;
    void relabel_graph(const vector<int> &labels);
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
    vector<int> Ts;
    vector<Arc> A;
    int LOSS;
    explicit Arcflow(const Instance &_inst);
    explicit Arcflow(const char *fname);
    void write(const char *fname);
    void write(FILE *fout);
};

#endif  // SRC_ARCFLOW_HPP_
