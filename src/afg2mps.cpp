/**
Copyright (C) 2013, Filipe Brandao
Faculdade de Ciencias, Universidade do Porto
Porto, Portugal. All rights reserved. E-mail: <fdabrandao@dcc.fc.up.pt>.
**/
#include <cstdio>
#include <cassert>
#include <cstring>
#include <cstdarg>
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

int main(int argc, char *argv[]){     
    printf("Copyright (C) 2013, Filipe Brandao\n");
    printf("Usage: afg2mps graph.afg model.mps\n");
    setvbuf(stdout, NULL, _IONBF, 0);
    assert(argc == 3);    
    FILE *fin = fopen(argv[1], "r");
    FILE *fout = fopen(argv[2], "w");    
    assert(fin != NULL);
    assert(fout != NULL);
    
    assert(fscanf(fin, " #INSTANCE_BEGIN# ")==0);
    Instance inst(fin);
    
    assert(fscanf(fin, " #GRAPH_BEGIN# ")==0);      

    int S, T;
    assert(fscanf(fin, " S: %d ", &S)==1);
    assert(fscanf(fin, " T: %d ", &T)==1);    
    
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
        char ctype = inst.items[i].ctype;
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
    for(int i = 0; i < NA; i++){
        int i_u, i_v, label;    
        assert(fscanf(fin, " %d %d %d ", &i_u, &i_v, &label)==3);
        labels.push_back(label);
        sprintf(buf, "X%x", i);
        sprintf(buf1, "F%x", i_u);
        sprintf(buf2, "F%x", i_v);        
        mps.write(7, "", "", buf, buf1, "-1", buf2, "1");
        if(label < inst.m){
            sprintf(buf1, "B%d", label);
            mps.write(5, "", "", buf, buf1, "1");
        }        
    }
    
    sprintf(buf1, "F%x", T);
    sprintf(buf2, "F%x", S);  
    mps.write(7, "", "", "Z", buf1, "-1", buf2, "1");    
    mps.write(5, "", "", "Z", "OBJ", "1");
    
    if(inst.vtype == 'I')
        mps.write(6, "", "", "MARKER", "'MARKER'", "", "'INTEND'");
    
    /* right-hand-side vector */
    
    mps.write(1, "RHS");
    
    for(int i = 0; i < inst.m; i++){
        sprintf(buf, "B%d", i);
        sprintf(buf1, "%d", inst.items[i].demand);
        mps.write(5, "", "", "RHS1", buf, buf1);
    }
    
    /* bounds */
    
    mps.write(1, "BOUNDS");
    
    int n = 0;
    for(int i = 0; i < inst.m; i++)
        n += inst.items[i].demand;
    
    for(int i = 0; i < NA; i++){
        int lbl = labels[i];
        sprintf(buf, "X%x", i);

        mps.write(5, "", "LO", "BND1", buf, "0");
    
        if(lbl < inst.m && !inst.relax_domains)
            sprintf(buf1, "%d", inst.items[lbl].demand);        
        else
            sprintf(buf1, "%d", n);        

        mps.write(5, "", "UP", "BND1", buf, buf1);
    }

    mps.write(5, "", "LO", "BND1", "Z", "0");
    sprintf(buf, "%d", n);
    mps.write(5, "", "UP", "BND1", "Z", buf);    
    
    mps.write(1, "ENDATA");

    fclose(fin);
    fclose(fout);
    printf("DONE!\n");
    return 0;
}


