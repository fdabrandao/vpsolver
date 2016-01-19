/**
This code is part of the Arc-flow Vector Packing Solver (VPSolver).

Copyright (C) 2013-2015, Filipe Brandao
Faculdade de Ciencias, Universidade do Porto
Porto, Portugal. All rights reserved. E-mail: <fdabrandao@dcc.fc.up.pt>.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
**/
#include <cstdio>
#include <cassert>
#include <cstring>
#include <cstdarg>
#include <map>
#include "common.hpp"
#include "instance.hpp"
using namespace std;

/*
    LP format example:

    Maximize
        obj: x1 + 2 x2 + 3 x3 + x4
    Subject To
        c1: - x1 + x2 + x3 + 10 x4 <= 20
        c2: x1 - 3 x2 + x3 <= 30
        c3: x2 - 3.5 x4 = 0
    Bounds
        0 <= x1 <= 40
        2 <= x4 <= 3
    General
        x4
    End
*/

int main(int argc, char *argv[]){
    printf("Copyright (C) 2013-2015, Filipe Brandao\n");
    setvbuf(stdout, NULL, _IONBF, 0);
    if(argc != 3){
        printf("Usage: afg2mps graph.afg model.lp\n");
        return 1;
    }

    FILE *fin = fopen(argv[1], "r");
    FILE *fout = fopen(argv[2], "w");
    assert(fin != NULL);
    assert(fout != NULL);

    printf("Generating the .LP model...");

    assert(fscanf(fin, " #INSTANCE_BEGIN# ")==0);
    Instance inst(fin, MVP);

    assert(fscanf(fin, " #GRAPH_BEGIN# ")==0);

    int S;
    vector<int> Ts(inst.nbtypes);
    assert(fscanf(fin, " S: %d ", &S)==1);
    assert(fscanf(fin, " Ts: ") >= 0);
    for(int t = 0; t < inst.nbtypes; t++){
        assert(fscanf(fin, " %d ", &Ts[t])==1);
    }

    int NV, NA;
    assert(fscanf(fin, " NV: %d ", &NV)==1);
    assert(fscanf(fin, " NA: %d ", &NA)==1);

    map<int, vector<int> > Ai;
    map<int, vector<int> > in;
    map<int, vector<int> > out;

    /* objective */

    fprintf(fout, "Minimize");
    for(int i = 0; i < NA; i++){
        int i_u, i_v, label;
        assert(fscanf(fin, " %d %d %d ", &i_u, &i_v, &label)==3);
        Ai[label].push_back(i);
        in[i_v].push_back(i);
        out[i_u].push_back(i);
        if(i_v == S) {
            for(int j = 0; j < (int)Ts.size(); j++){
                if(Ts[j] == i_u){
                    if(inst.Cs[j] >= 0)
                        fprintf(fout, " +%d X%x", inst.Cs[j], i);
                    else
                        fprintf(fout, " -%d X%x", abs(inst.Cs[j]), i);
                    break;
                }
            }
        }
    }
    fprintf(fout, "\n");

    /* constraints */

    fprintf(fout, "Subject To\n");

    // demand constraints

    for(int i = 0; i < inst.m; i++){
        if(inst.items[i].demand == 0) continue;
        fprintf(fout, "\tB%d:", i);
        for(int j = 0; j < (int)inst.items.size(); j++){
            if(inst.items[j].type == i)
                ForEach(ai, Ai[j]) fprintf(fout, " + X%x", *ai);
        }
        if(inst.ctypes[i] == '=' && !inst.relax_domains)
            fprintf(fout, " = %d", inst.demands[i]);
        else
            fprintf(fout, " >= %d", inst.demands[i]);
        fprintf(fout, "\n");
    }

    // flow conservation constraints

    for(int i = 0; i < NV; i++){
        fprintf(fout, "\tF%x:", i);
        ForEach(ai, in[i])
            fprintf(fout, " + X%x", *ai);
        ForEach(ai, out[i])
            fprintf(fout, " - X%x", *ai);
        fprintf(fout, " = 0\n");
    }

    /* bounds */

    int n = 0;
    for(int i = 0; i < inst.m; i++)
        n += inst.demands[i];

    fprintf(fout, "Bounds\n");
    ForEach(e, Ai){
        int i = e->first;
        ForEach(ai, e->second){
            if(i < (int)inst.items.size() && !inst.relax_domains)
                fprintf(fout, "0 <= X%x <= %d\n", *ai, inst.items[i].demand);
            else
                fprintf(fout, "0 <= X%x <= %d\n", *ai, n);
        }
    }

    /* integer variables */

    if(inst.vtype == 'I'){
        fprintf(fout, "General\n");

        fprintf(fout, "\t");
        for(int i = 0; i < NA; i++){
            if(!i)
                fprintf(fout, "X%x", i);
            else
                fprintf(fout, " X%x", i);
        }
    }

    fprintf(fout, "\nEnd\n");

    fclose(fin);
    fclose(fout);
    printf("DONE!\n");
    return 0;
}
