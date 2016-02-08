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
#include <cstring>
#include <cmath>
#include <map>
#include "config.hpp"
#include "common.hpp"
#include "arcflow.hpp"
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
    try {
        throw_assert(check_ext(argv[1], ".afg"));
        Arcflow afg(argv[1]);
        Instance &inst = afg.inst;

        FILE *fsol = fopen(argv[2], "r");
        if(fsol == NULL) perror("fopen");
        throw_assert(fsol != NULL);

        bool print_inst = false;
        if(argc >= 4){
            print_inst = atoi(argv[3]) != 0;
        }
        bool pyout = false;
        if(argc >= 5){
            pyout = atoi(argv[4]) != 0;
        }

        int ind;
        double x;
        char buf[MAX_LEN];
        map<Arc, int> flow;
        while(fscanf(fsol, "%s %lf", buf, &x) != EOF){
            if(strlen(buf) <= 1) continue;
            sscanf(&buf[1], "%x", &ind);
            throw_assert(ind < afg.NA);
            int rx = (int)round(x);
            throw_assert(x - rx <= EPS);
            if(rx > 0) flow[afg.A[ind]] = rx;
        }
        fclose(fsol);

        ArcflowSol sol(inst, flow, afg.S, afg.Ts, afg.LOSS, inst.binary);
        sol.print_solution(inst, print_inst, pyout, true);
        return 0;
    } catch(const char *e) {
        printf("%s\n", e);
        return -1;
    } catch (...) {
        printf("UnknownError\n");
        return -1;
    }
}

int main(int argc, char *argv[]){
    return swig_main(argc, argv);
}
