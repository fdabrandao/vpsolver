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
#include <cassert>
#include <cstring>
#include <cmath>
#include <algorithm>
#include "common.hpp"
#include "instance.hpp"
using namespace std;

#define NORM_PRECISION 10000

/* Class Item */

bool Item::operator<(const Item &o) const{
    assert(ndims == o.ndims);
    if(abs(key-o.key) >= 1e-5) return key < o.key;
    for(int i = 0; i < ndims; i++){
        if(w[i] != o.w[i]) return w[i] < o.w[i];
    }
    return demand < o.demand;
}

int Item::operator[](int i) const{
    assert(i < ndims);
    return w[i];
}

int &Item::operator[](int i){
    assert(i < ndims);
    return w[i];
}


/* Class Instance */

void Instance::init(){
    relax_domains = false;
    binary = false;
    sort = true;
    method = -2;
    vtype = 'I';
    ndims = 0;
    m = 0;
}

Instance::Instance(){
    init();
}

Instance::Instance(FILE *fin, ftype type){
    init();
    read(fin, type);
}

Instance::Instance(const char *fname){
    init();
    read(fname);
}

void Instance::read(const char *fname){
    FILE *fin = fopen(fname, "r");
    assert(fin != NULL);
    if(check_ext(fname, ".vbp")){
        read(fin, VBP);
    } else if(check_ext(fname, ".mvp")){
        read(fin, MVP);
    } else {
        exit_error("Invalid file extension!");
    }
    fclose(fin);
}

void Instance::read(FILE *fin, ftype type){
    assert(fscanf(fin, " NDIMS: ") >= 0);
    assert(fscanf(fin, "%d", &ndims) == 1);

    if(type == MVP){
        assert(fscanf(fin, " NBTYPES: ") >= 0);
        assert(fscanf(fin, "%d", &nbtypes) == 1);
    }else{
        nbtypes = 1;
    }

    Cs.resize(nbtypes);
    Ws.resize(nbtypes);
    for(int t = 0; t < nbtypes; t++){
        Ws[t].resize(ndims);
        assert(fscanf(fin, " Wi: ") >= 0);
        for(int d = 0; d < ndims; d++)
            assert(fscanf(fin, "%d", &Ws[t][d])==1);
        if(type == MVP){
            assert(fscanf(fin, " Ci: ") >= 0);
            assert(fscanf(fin, "%d", &Cs[t])==1);
        } else {
            Cs[t] = 1;
        }
    }

    assert(fscanf(fin, " M: ") >= 0);
    assert(fscanf(fin, "%d", &m) == 1);

    items.clear();
    nopts.clear();
    ctypes.clear();
    demands.clear();
    int it_count = 0;
    for(int it_type = 0; it_type < m; it_type++){

        int qi, bi;
        if(type == MVP){
            assert(fscanf(fin, " qi: ") >= 0);
            assert(fscanf(fin, "%d", &qi) == 1);
            assert(fscanf(fin, " bi: ") >= 0);
            assert(fscanf(fin, "%d", &bi) == 1);
            demands.push_back(bi);
        } else {
            qi = 1;
            bi = -1;
        }
        nopts.push_back(qi);
        ctypes.push_back('*');

        for(int t = 0; t < qi; t++){
            items.push_back(Item(ndims));
            Item &item = items.back();
            if(qi > 1){
                item.opt = t;
            }else{
                item.opt = -1;
            }

            assert(fscanf(fin, " wi: ") >= 0);
            for(int d = 0; d < ndims; d++){
                assert(fscanf(fin, "%d", &item[d])==1);
                if(item[d] != 0)
                    item.nonzero.push_back(d);
            }
            assert(!item.nonzero.empty());

            if(type == VBP){
                assert(fscanf(fin, " bi: ") >= 0);
                assert(fscanf(fin, "%d", &bi)==1);
                demands.push_back(bi);
            }
            item.demand = bi;

            int S = 0;
            vector<int> maxW(ndims, 0);
            for(int d = 0; d < ndims; d++){
                for(int t = 0; t < nbtypes; t++)
                    maxW[d] = max(maxW[d], Ws[t][d]);
            }
            for(int d = 0; d < ndims; d++){
                if(maxW[d] > 0){
                    S += round(item[d]/double(maxW[d])*NORM_PRECISION);
                }
            }
            if(item.demand > 0){
                bool fits;
                for(int t = 0; t < nbtypes; t++){
                    fits = true;
                    for(int d = 0; d < ndims; d++){
                        if(item[d] > Ws[t][d]){
                            fits = false;
                            break;
                        }
                    }
                    if(fits) break;
                }
                assert(fits == true);
            }
            item.key = S;
            item.type = it_type;
            item.id = it_count++;
        }
    }

    char buf[MAX_LEN];
    while(fscanf(fin, "%s", buf) != EOF){
        if(!strcmp(buf, "#INSTANCE_END#")) break;
        else if(!strcmp(buf, "VTYPE:")){
            assert(fscanf(fin, "%s", buf)==1);
            vtype = buf[0];
            assert(vtype == 'C' || vtype == 'I');
        }else if(!strcmp(buf, "CTYPE:")){
            ctypes.clear();
            for(int i = 0; i < m; i++){
                assert(fscanf(fin, "%s", buf)==1);
                if(!strcmp(buf, ">")){
                    ctypes.push_back('>');
                }else if(!strcmp(buf, "=")){
                    ctypes.push_back('=');
                }else{
                    assert(!strcmp(buf, "*"));
                    ctypes.push_back('*');
                }
            }
        }else if(!strcmp(buf, "IDS:")){
            for(int i = 0; i < (int)items.size(); i++)
                assert(fscanf(fin, "%d", &items[i].id)==1);
        }else if(!strcmp(buf, "SORT:")){
            int tsort;
            assert(fscanf(fin, "%d", &tsort)==1);
            assert(tsort == 0 || tsort == 1);
            sort = tsort;
        }else if(!strcmp(buf, "METHOD:")){
            assert(fscanf(fin, "%d", &method)==1);
            assert(method >= MIN_METHOD && method <= MAX_METHOD);
        }else if(!strcmp(buf, "RELAX:")){
            int trelax;
            assert(fscanf(fin, "%d", &trelax)==1);
            assert(trelax == 0 || trelax == 1);
            relax_domains = trelax;
        }else if(!strcmp(buf, "BINARY:")){
            int tbinary;
            assert(fscanf(fin, "%d", &tbinary)==1);
            assert(tbinary == 0 || tbinary == 1);
            binary = tbinary;
        }else{
            printf("Invalid option '%s'!\n", buf);
            exit(1);
        }
    }

    for(int i = 0; i < m; i++)
        if(ctypes[i] == '*')
            ctypes[i] = (demands[i] <= 1) ? '=' : '>';

    if(sort){
        stable_sort(All(items));
        reverse(All(items));
    }
}

void Instance::write(FILE *fout) const{
    fprintf(fout, "NDIMS: %d\n", ndims);

    fprintf(fout, "NBTYPES: %d\n", nbtypes);

    for(int t = 0; t < nbtypes; t++){
        fprintf(fout, "Wi:");
        for(int i = 0; i < ndims; i++){
            fprintf(fout, " %d", Ws[t][i]);
        }
        fprintf(fout, " Ci: %d\n", Cs[t]);
    }

    fprintf(fout, "M: %d\n", m);
    int p = 0;
    vector<int> rid(items.size());
    for(int it = 0; it < (int)items.size(); it++) rid[items[it].id] = it;
    for(int i = 0; i < m; i++){
        fprintf(fout, "qi: %d bi: %d\n", nopts[i], demands[i]);
        for(int q = 0; q < nopts[i]; q++){
            fprintf(fout, "wi:");
            for(int j = 0; j < ndims; j++){
                fprintf(fout, " %d", items[rid[p]][j]);
            }
            fprintf(fout, "\n");
            p++;
        }
    }

    fprintf(fout, "VTYPE: %c\n", vtype);

    fprintf(fout, "CTYPE:");
    for(int i = 0; i < m; i++)
        fprintf(fout, " %c", ctypes[i]);
    fprintf(fout, "\n");

    fprintf(fout, "SORT: %d\n", sort);

    fprintf(fout, "METHOD: %d\n", method);

    fprintf(fout, "RELAX: %d\n", relax_domains);

    fprintf(fout, "BINARY: %d\n", binary);

    fprintf(fout, "IDS:");
    for(int i = 0; i < (int)items.size(); i++)
        fprintf(fout, " %d", items[i].id);
    fprintf(fout, "\n");
}
