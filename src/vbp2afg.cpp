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
#include "config.hpp"
#include "arcflow.hpp"
#include "instance.hpp"
using namespace std;

int swig_main(int argc, char *argv[]){
    printf(PACKAGE_STRING", Copyright (C) 2013-2016, Filipe Brandao\n");
    setvbuf(stdout, NULL, _IONBF, 0);
    if(argc < 3 || argc > 6){
        printf("Usage: vbp2afg instance.vbp/instance.mvp graph.afg [method:-2] [binary:0] [vtype:I]\n");
        return 1;
    }

    FILE *fout = fopen(argv[2], "w");
    if(fout == NULL) perror("fopen");
    assert(fout != NULL);

    Instance inst(argv[1]);
    if(argc >= 4) {
        inst.method = atoi(argv[3]);
        assert(inst.method >= MIN_METHOD && inst.method <= MAX_METHOD);
    }
    if(argc >= 5){
        inst.binary = atoi(argv[4]);
    }
    if(argc >= 6){
        inst.vtype = argv[5][0];
        assert(inst.vtype == 'I' || inst.vtype == 'C');
    }

    Arcflow graph(inst);

    fprintf(fout, "#INSTANCE_BEGIN#\n");
    inst.write(fout);
    fprintf(fout, "#INSTANCE_END#\n");

    fprintf(fout, "#GRAPH_BEGIN#\n");
    graph.write(fout);
    fprintf(fout, "#GRAPH_END#\n");

    fclose(fout);
    return 0;
}

int main(int argc, char *argv[]){
    return swig_main(argc, argv);
}
