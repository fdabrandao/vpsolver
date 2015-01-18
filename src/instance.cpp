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
    if(key < o.key){
        return true;
    }else if(key == o.key){
        for(int i = 0; i < ndims; i++){
            if(w[i] == o.w[i]) continue;
            else return w[i] < o.w[i];
        }
    }
    return false;
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

Instance::Instance(FILE *fin){
    init();
    read(fin);
}

Instance::Instance(const char *fname){
    init();
    read(fname);
}

void Instance::read(FILE *fin){
    assert(fscanf(fin, " NDIMS: ") >= 0);       
    assert(fscanf(fin, "%d", &ndims) == 1);   

    W.resize(ndims);            
    for(int d = 0; d < ndims; d++)
        assert(fscanf(fin, "%d", &W[d])==1);

    assert(fscanf(fin, " M: ") >= 0);             
    assert(fscanf(fin, "%d", &m) == 1);     
              
    items.clear();
    for(int i = 0; i < m; i++){
        items.push_back(Item(ndims));
        for(int d = 0; d < ndims; d++){
            int &w = items[i][d];
            assert(fscanf(fin, "%d", &w)==1);               
            if(w != 0)
                items[i].nonzero.push_back(d);
        }
        assert(!items[i].nonzero.empty());
        assert(fscanf(fin, "%d", &items[i].demand)==1);
        int S = 0;
        for(int d = 0; d < ndims; d++){
            assert(items[i].demand == 0 || items[i][d] <= W[d]);
            S += W[d] > 0 ? round(items[i][d]/double(W[d])*NORM_PRECISION) : 0;
        }
        items[i].key = S;
        items[i].id = i;
    }

    char buf[MAX_LEN];                  
    while(fscanf(fin, "%s", buf) != EOF){
        if(!strcmp(buf, "#INSTANCE_END#")) break;
        else if(!strcmp(buf, "VTYPE:")){
            assert(fscanf(fin, "%s", buf)==1);
            vtype = buf[0];
            assert(vtype == 'C' || vtype == 'I');
        }else if(!strcmp(buf, "CTYPE:")){
            for(int i = 0; i < m; i++){
                assert(fscanf(fin, "%s", buf)==1);
                if(!strcmp(buf, ">")){
                    items[i].ctype = '>';
                }else if(!strcmp(buf, "=")){
                    items[i].ctype = '=';
                }else{
                    assert(!strcmp(buf, "*"));
                    items[i].ctype = '*';
                }
            }
        }else if(!strcmp(buf, "IDS:")){
            for(int i = 0; i < m; i++)
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
        if(items[i].ctype == '*')            
            items[i].ctype = (items[i].demand <= 1) ? '=' : '>';           
    
    if(sort){        
        stable_sort(All(items));
        reverse(All(items));
    }
}

void Instance::read(const char *fname){
    FILE *fin = fopen(fname, "r");
    assert(fin != NULL);
    read(fin);
    fclose(fin);
}

Instance::Instance(vector<int> W, vector<vector<int> > w, vector<int> b){
    vtype = 'I';
    this->W = W;
    ndims = (int)W.size();    
    
    items.clear();
    m = (int)w.size();
    for(int i = 0; i < m; i++){
        items.push_back(Item(ndims));
        for(int j = 0; j < ndims; j++)            
            items[i][j] = w[i][j];
        items[i].demand = b[i];            
        items[i].ctype = (items[i].demand <= 1) ? '=' : '>';
        double S = 0;
        for(int j = 0; j < ndims; j++){
            assert(items[i][j] <= W[j]);
            S += W[j] > 0 ? items[i][j]/double(W[j]) : 0;
        }
        assert(S > 0);
        items[i].key = S;
        items[i].id = i;
    }
    stable_sort(All(items));
    reverse(All(items));        
}

void Instance::write(FILE *fout) const{
    fprintf(fout, "NDIMS: %d\n", ndims);   
    
    for(int i = 0; i < ndims; i++){
        if(i > 0) fprintf(fout, " ");
        fprintf(fout, "%d", W[i]);
    }
    fprintf(fout, "\n");
    
    fprintf(fout, "M: %d\n", m);    
    for(int i = 0; i < m; i++){
        for(int j = 0; j < ndims; j++){
            if(j > 0) fprintf(fout, " ");
            fprintf(fout, "%d", items[i][j]);
        }
        fprintf(fout, " %d\n", items[i].demand);
    }  

    fprintf(fout, "VTYPE: %c\n", vtype);

    fprintf(fout, "CTYPE:");
    for(int i = 0; i < m; i++)
        fprintf(fout, " %c", items[i].ctype);
    fprintf(fout, "\n");    
    
    fprintf(fout, "SORT: %d\n", sort);    
    
    fprintf(fout, "METHOD: %d\n", method);    

    fprintf(fout, "RELAX: %d\n", relax_domains);        
    
    fprintf(fout, "BINARY: %d\n", binary);            
    
    fprintf(fout, "IDS:");
    for(int i = 0; i < m; i++)
        fprintf(fout, " %d", items[i].id);
    fprintf(fout, "\n");    
}

void Instance::write(const char *fname) const{
    FILE *fout = fopen(fname, "w");
    assert(fout != NULL);
    write(fout);
    fclose(fout);
}


