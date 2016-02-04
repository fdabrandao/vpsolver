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
#include <cassert>
#include <cstring>
#include <cstdarg>
#include <map>
#include "config.hpp"
#include "instance.hpp"
using namespace std;

/*
MPS format

Field:     1          2          3         4         5         6
Columns:  2-3        5-12      15-22     25-36     40-47     50-61
*/

#define MAX_LEN 80
#define NFIELDS 7

int field_start[NFIELDS] = {0, 1, 4, 14, 24, 39, 49};

class Mps{
private:

    FILE *fout;
    int p;
    int cur_field;
    char buf[MAX_LEN];

    void clear(){
        p = 0;
        cur_field = 0;
        memset(buf, ' ', sizeof(buf));
    }

    void add_field(const char *str){
        assert(cur_field < NFIELDS);
        p = field_start[cur_field];
        for(int i = 0; str[i]; i++){
            buf[p++] = str[i];
        }
        cur_field++;
    }

public:

    Mps(FILE *_fout = stdout): fout(_fout){}

    void write(int count, ...){
        clear();

        va_list v;
        va_start(v, count);
        for(int i = 0; i < count; i++)
            add_field(va_arg(v, const char *));
        va_end(v);

        assert(p < MAX_LEN);
        buf[p] = 0;
        fprintf(fout, "%s\n", buf);
        clear();
    }
};

int swig_main(int argc, char *argv[]){
    printf(PACKAGE_STRING", Copyright (C) 2013-2016, Filipe Brandao\n");
    setvbuf(stdout, NULL, _IONBF, 0);
    if(argc != 3){
        printf("Usage: afg2mps graph.afg model.mps\n");
        return 1;
    }

    FILE *fin = fopen(argv[1], "r");
    if(fin == NULL) perror("fopen");
    assert(fin != NULL);

    FILE *fout = fopen(argv[2], "w");
    if(fout == NULL) perror("fopen");
    assert(fout != NULL);

    printf("Generating the .MPS model...");

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

    int LOSS;
    assert(fscanf(fin, " LOSS: ") >= 0);
    assert(fscanf(fin, " %d ", &LOSS)==1);

    int NV, NA;
    assert(fscanf(fin, " NV: %d ", &NV)==1);
    assert(fscanf(fin, " NA: %d ", &NA)==1);

    Mps mps(fout);
    mps.write(4, "NAME", "", "", "ARCFLOW");
    mps.write(1, "ROWS");
    mps.write(3, "", "N", "OBJ");

    char buf[MAX_LEN];
    char buf1[MAX_LEN];
    char buf2[MAX_LEN];

    /* demand constraints */

    for(int i = 0; i < inst.m; i++){
        char ctype = inst.ctypes[i];
        assert(ctype == '>' || ctype == '=');
        sprintf(buf, "B%d", i);
        if(ctype == '=' && !inst.relax_domains)
            mps.write(3, "", "E", buf);
        else
            mps.write(3, "", "G", buf);
    }

    /* flow conservation constraints */

    for(int i = 0; i < NV; i++){
        sprintf(buf, "F%x", i);
        mps.write(3, "", "E", buf);
    }

    /* A-matrix */

    mps.write(1, "COLUMNS");

    if(inst.vtype == 'I')
        mps.write(6, "", "", "MARKER", "'MARKER'", "", "'INTORG'");

    vector<int> labels;
    vector<int> ub(NA);
    for(int i = 0; i < NA; i++){
        int i_u, i_v, label;
        assert(fscanf(fin, " %d %d %d ", &i_u, &i_v, &label)==3);
        labels.push_back(label);
        sprintf(buf, "X%x", i);
        sprintf(buf1, "F%x", i_u);
        sprintf(buf2, "F%x", i_v);
        mps.write(7, "", "", buf, buf1, "-1", buf2, "1");
        if(label != LOSS){
            sprintf(buf1, "B%d", inst.items[label].type);
            mps.write(5, "", "", buf, buf1, "1");
        }
        if(i_v == S) {
            for(int j = 0; j < (int)Ts.size(); j++){
                if(Ts[j] == i_u){
                    ub[i] = (inst.Qs[j] >= 0) ? inst.Qs[j] : inst.n;
                    sprintf(buf1, "%d", inst.Cs[j]);
                    mps.write(5, "", "", buf, "OBJ", buf1);
                    break;
                }
            }
        }else{
            if(label != LOSS && !inst.relax_domains)
                ub[i] = inst.items[label].demand;
            else
                ub[i] = inst.n;
        }
    }

    if(inst.vtype == 'I')
        mps.write(6, "", "", "MARKER", "'MARKER'", "", "'INTEND'");

    /* right-hand-side vector */

    mps.write(1, "RHS");

    for(int i = 0; i < inst.m; i++){
        sprintf(buf, "B%d", i);
        sprintf(buf1, "%d", inst.demands[i]);
        mps.write(5, "", "", "RHS1", buf, buf1);
    }

    /* bounds */

    mps.write(1, "BOUNDS");

    for(int i = 0; i < NA; i++){
        sprintf(buf, "X%x", i);
        mps.write(5, "", "LO", "BND1", buf, "0");
        sprintf(buf1, "%d", ub[i]);
        mps.write(5, "", "UP", "BND1", buf, buf1);
    }

    mps.write(1, "ENDATA");

    fclose(fin);
    fclose(fout);
    printf("DONE!\n");
    return 0;
}

int main(int argc, char *argv[]){
    return swig_main(argc, argv);
}
