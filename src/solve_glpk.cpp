/**
Copyright (C) 2013, Filipe Brandao
Faculdade de Ciencias, Universidade do Porto
Porto, Portugal. All rights reserved. E-mail: <fdabrandao@dcc.fc.up.pt>.
**/
#include <cstdio>
#include <cassert>
#include <string>
#include <cstring>
#include <glpk.h>
using namespace std;

int main(int argc, char *argv[]){     
    printf("Copyright (C) 2013, Filipe Brandao\n");
    printf("Usage: solve_glpk model.mps|model.lp [vars.sol]\n");    
    setvbuf(stdout, NULL, _IONBF, 0);
    assert(argc == 2 || argc == 3);
                
    glp_prob *P;
    P = glp_create_prob();
    
    char *fname = argv[1];
    char *dot = strrchr(fname, '.');
    if(dot && !strcmp(dot, ".mps")){
        assert(glp_read_mps(P, GLP_MPS_DECK, NULL, fname)==0);
    }else if(dot && !strcmp(dot, ".lp")){
        assert(glp_read_lp(P, NULL, fname)==0);
    }else{
        printf("Error: Invalid file format!\n");
	return -1;
    }

    glp_adv_basis(P, 0);
    glp_simplex(P, NULL);
    glp_intopt(P, NULL);

    if(argc == 3){
        FILE *fout = fopen(argv[2], "w");
        assert(fout != NULL);        
            
        int nvars = glp_get_num_cols(P);
        for (int i = 1; i <= nvars; i++){      
            double value = glp_mip_col_val(P, i);
            if(value != 0){
                const char *name = glp_get_col_name(P, i);
                fprintf(fout, "%s %.6f\n", name, value);    
            }
        }
        fclose(fout);
    }
    
    glp_delete_prob(P);        
    return 0;
}

