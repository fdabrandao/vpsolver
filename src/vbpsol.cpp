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
#include <cstdio>
#include <cstdlib>
#include <cassert>
#include <cstring>
#include <cmath>
#include <map>
#include "config.hpp"
#include "common.hpp"
#include "instance.hpp"
#include "arcflowsol.hpp"
using namespace std;

int swig_main(int argc, char *argv[]){
    printf(PACKAGE_STRING", Copyright (C) 2013-2016, Filipe Brandao\n");
    setvbuf(stdout, NULL, _IONBF, 0);
    if(argc < 3 || argc > 5){
        printf("Usage: vbpsol graph.afg vars.sol [print_instance:0] [pyout:0]\n");
        return 1;
    }



    FILE *fafg = fopen(argv[1], "r");
    if(fafg == NULL) perror("fopen");
    assert(fafg != NULL);

    FILE *fsol = fopen(argv[2], "r");
    if(fsol == NULL) perror("fopen");
    assert(fsol != NULL);

    bool print_inst = false;
    if(argc >= 4){
        print_inst = atoi(argv[3]) != 0;
    }
    bool pyout = false;
    if(argc >= 5){
        pyout = atoi(argv[4]) != 0;
    }

    assert(fscanf(fafg, " #INSTANCE_BEGIN# ")==0);
    Instance inst(fafg, MVP);
    assert(fscanf(fafg, " #GRAPH_BEGIN# ")==0);
    assert(fscanf(fafg, " #GRAPH_BEGIN# ")==0);

    int S;
    vector<int> Ts(inst.nbtypes);
    assert(fscanf(fafg, " S: %d ", &S)==1);
    assert(fscanf(fafg, " Ts: ") >= 0);
    for(int t = 0; t < inst.nbtypes; t++){
        assert(fscanf(fafg, " %d ", &Ts[t])==1);
    }

    int LOSS;
    assert(fscanf(fafg, " LOSS: ") >= 0);
    assert(fscanf(fafg, " %d ", &LOSS)==1);

    int NV, NA;
    assert(fscanf(fafg, " NV: %d ", &NV)==1);
    assert(fscanf(fafg, " NA: %d ", &NA)==1);

    vector<int> a_u(NA), a_v(NA), a_l(NA);
    for(int i = 0; i < NA; i++)
        assert(fscanf(fafg, " %d %d %d ", &a_u[i], &a_v[i], &a_l[i])==3);
    fclose(fafg);

    int ind;
    double x;
    char buf[MAX_LEN];
    map<Arc, int> flow;
    while(fscanf(fsol, "%s %lf", buf, &x) != EOF){
        if(strlen(buf) <= 1) continue;
        sscanf(&buf[1], "%x", &ind);
        assert(ind < NA);
        int rx = (int)round(x);
        assert(x - rx <= EPS);
        if(rx > 0){
            int u = a_u[ind];
            int v = a_v[ind];
            int lbl = a_l[ind];
            Arc a(u, v, lbl);
            flow[a] = rx;
        }
    }

    ArcflowSol sol(inst, flow, S, Ts, LOSS, inst.binary);
    sol.print_solution(inst, print_inst, pyout, true);
    return 0;
}

int main(int argc, char *argv[]){
    return swig_main(argc, argv);
}
