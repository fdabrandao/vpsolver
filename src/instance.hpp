/**
This code is part of the Arc-flow Vector Packing Solver (VPSolver).

Copyright (C) 2013-2017, Filipe Brandao
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
#ifndef SRC_INSTANCE_HPP_
#define SRC_INSTANCE_HPP_

#include <vector>
#include <cstdio>
using namespace std;

enum ftype {VBP, MVP};

class Item {
 public:
    vector<int> w;
    vector<int> nonzero;
    int id;
    int type;
    int opt;
    int ndims;
    int demand;
    int key;

    explicit Item(int _ndims): ndims(_ndims) {
        w = vector<int>(_ndims);
    }
    void add_dim(int dw) {
        ndims++;
        w.push_back(dw);
    }
    bool operator<(const Item &o) const;
    int operator[](int i) const;
    int &operator[](int i);
};

class Instance {
 private:
    void init();

 public:
    int ndims;
    int nbtypes;
    int nsizes;
    int m, n;
    vector<vector<int>> Ws;  // bin types
    vector<int> Cs;  // costs
    vector<int> Qs;  // quantities
    vector<Item> items;
    int method;
    bool binary;
    bool relax_domains;

    char vtype;
    vector<char> ctypes;
    vector<int> nopts;
    vector<int> demands;

    Instance();
    explicit Instance(const char *fname);
    explicit Instance(FILE *fin, ftype type = MVP);

    vector<Item> sorted_items();
    void print() const;
    void read(const char *fname);
    void read(FILE *fin, ftype type = MVP);
    void write(FILE *fout) const;
};

#endif  // SRC_INSTANCE_HPP_
