/**
Copyright (C) 2013, Filipe Brandao
Faculdade de Ciencias, Universidade do Porto
Porto, Portugal. All rights reserved. E-mail: <fdabrandao@dcc.fc.up.pt>.
**/
#ifndef _INSTANCE_HPP_
#define _INSTANCE_HPP_

#include <vector>
#include <cstdio>
using namespace std;

class Item{
public:    
    vector<int> w;
    vector<int> nonzero;
    int id;
    int ndims;
    int demand;
    int key;
    char ctype;
    
    Item(int _ndims): ndims(_ndims){
        ctype = '*';
        w = vector<int>(_ndims);
    }
    void add_dim(int dw){
        ndims++;
        w.push_back(dw);
    }
    bool operator<(const Item &o) const;    
    int operator[](int i) const;   
    int &operator[](int i);
};

class Instance{
private:
    void init();
public:
    char vtype;
    int ndims, m;
    vector<int> W;
    vector<int> MAXLABEL;    
    vector<Item> items;
    int method;
    bool sort;
    bool binary;    
    bool relax_domains;    

    Instance();
    Instance(FILE *fin);
    Instance(const char *fname);
    Instance(vector<int> W, vector<vector<int> > w, vector<int> b);
    
    void read(FILE *fin);
    void read(const char *fname);
    void write(FILE *fout) const;    
    void write(const char *fname) const;    
};

#endif
