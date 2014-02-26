/**
This code is part of the Arc-flow Vector Packing Solver (VPSolver).

Copyright (C) 2013-2014, Filipe Brandao
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
#include <string>
#include <cstring>
#include <glpk.h>
using namespace std;

int main(int argc, char *argv[]){     
    printf("Copyright (C) 2013-2014, Filipe Brandao\n");    
    setvbuf(stdout, NULL, _IONBF, 0);
    if(argc < 2 || argc > 3){
        printf("Usage: solve_glpk model.mps|model.lp [vars.sol]\n");  
        return 1;
    }
                
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

