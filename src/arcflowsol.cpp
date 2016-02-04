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
#include <set>
#include <climits>
#include <cstring>
#include <cassert>
#include <ctime>
#include <algorithm>
#include "graph.hpp"
#include "common.hpp"
#include "instance.hpp"
#include "arcflowsol.hpp"
using namespace std;

/* Class ArcflowSol */

vector<pattern_pair> ArcflowSol::remove_excess(
        const vector<pattern_int> &sol, vector<int> &dem) const{
    vector<pattern_pair> tmp;
    ForEach(pat, sol){
        map<int, int> count;
        ForEach(it, pat->second) count[*it] += 1;
        vector<int> rm;
        int rep = pat->first;
        while(rep > 0){
            rm.clear();
            ForEach(itr, count){
                int type = inst.items[itr->first].type;
                itr->second = min(itr->second, dem[type]);
                if(itr->second == 0) rm.push_back(itr->first);
            }
            ForEach(ind, rm) count.erase(*ind);

            int f = rep;
            ForEach(itr, count){
                int type = inst.items[itr->first].type;
                f = min(f, dem[type]/itr->second);
            }
            rep -= f;

            tmp.push_back(MP(f, vector<int_pair>(All(count))));
            ForEach(itr, count){
                int type = inst.items[itr->first].type;
                dem[type] -= f * itr->second;
            }
        }
    }

    map<vector<int_pair>, int> mp;
    ForEach(itr, tmp){
        sort(All(itr->second));
        mp[itr->second] += itr->first;
    }

    vector<pattern_pair> finalsol;
    ForEach(itr, mp)
        finalsol.push_back(MP(itr->second, itr->first));
    return finalsol;
}

vector<pattern_pair> ArcflowSol::extract_solution(vector<int> &dem, int T){
    set<int> nodes;
    map<int, vector<Arc> > adj;
    ForEach(a, flow){
        int u = a->first.u;
        int v = a->first.v;
        nodes.insert(u);
        nodes.insert(v);
        if(v != S) adj[v].push_back(a->first);
    }

    int &zflow = flow[Arc(T, S, LOSS)];

    vector<int> lst(All(nodes));

    vector<pattern_int> sol;
    while(true){
        map<int, Arc> pred;
        map<int, int> dp;
        dp[S] = zflow;
        ForEach(v, lst){
            int &val = dp[*v];
            Arc &p = pred[*v];
            ForEach(a, adj[*v]){
                assert(dp.count(a->u) != 0);
                int mf = min(dp[a->u], flow[*a]);
                if(mf > val){
                    p = *a;
                    val = mf;
                }
            }
        }
        int f = dp[T];
        zflow -= f;
        if(f == 0) break;
        int v = T;
        sol.push_back(pattern_int());
        pattern_int &patt = sol.back();
        patt.first = f;
        while(v != S){
            Arc a = pred[v];
            int u = a.u;
            int lbl = a.label;
            if(lbl != LOSS)
                patt.second.push_back(lbl);
            flow[a] -= f;
            v = u;
        }
    }
    return remove_excess(sol, dem);
}

bool ArcflowSol::is_valid(
        const vector<pattern_pair> &sol, const Instance &inst,
        vector<int> dem, int btype) const {
    ForEach(pat, sol){
        vector<int> w(inst.ndims);
        ForEach(itr, pat->second){
            if(binary && itr->second > 1) return false;
            const Item &it = inst.items[itr->first];
            for(int i = 0; i < inst.ndims; i++)
                w[i] += it[i];
            dem[it.type] -= pat->first * itr->second;
        }
        for(int i = 0; i < inst.ndims; i++)
            if(w[i] > inst.Ws[btype][i]) return false;
    }
    return true;
}

void ArcflowSol::print_solution(
        const Instance &inst, bool print_inst = true,
        bool pyout = false, bool validate = true){
    vector<int> dem(inst.m), id(inst.m), rid(inst.m);
    for(int i = 0; i < inst.m; i++){
        dem[i] = inst.demands[i];
        int t = inst.items[i].type;
        rid[t] = i;
    }

    int obj = 0;
    vector<int> nbins(inst.nbtypes);
    vector<vector<pattern_pair> > sols(inst.nbtypes);
    for(int t = 0; t < inst.nbtypes; t++){
        sols[t] = extract_solution(dem, Ts[t]);
        if(validate && !is_valid(sols[t], inst, dem, t))
            exit_error("Invalid solution! (capacity)");

        ForEach(pat, sols[t]) {
            obj += pat->first * inst.Cs[t];
            nbins[t] += pat->first;
        }
    }

    if(validate){
        for(int i = 0; i < inst.m; i++){
            if(dem[i] > 0) exit_error("Invalid solution! (demand)");
        }

        int fs = 0;
        ForEach(a, flow) fs += a->second;
        if(fs != 0) exit_error("Invalid solution! (flow)");
    }


    printf("Objective: %d\n", obj);
    printf("Solution:\n");
    for(int t = 0; t < inst.nbtypes; t++){
        if(!pyout){
            if(inst.nbtypes > 1)
                printf("Bins of type %d: %d\n", t+1, nbins[t]);
        }else{
            if(t == 0)
                printf("[");
            else
                printf(", [");
        }
        vector<pattern_pair> &sol = sols[t];
        ForEach(pat, sol){
            vector<int_pair> tmp;
            ForEach(itr, pat->second){
                int t = inst.items[itr->first].type;
                int opt = inst.items[itr->first].opt;
                for(int i = 0; i < itr->second; i++)
                    tmp.push_back(MP(t, opt));
            }
            sort(All(tmp));
            printf("%d x [", pat->first);
            ForEach(p, tmp){
                if(p != tmp.begin()) printf(", ");
                if(p->second == -1)
                    printf("i=%d", p->first+1);
                else
                    printf("i=%d opt=%d", p->first+1, p->second+1);
            }
            printf("]\n");
        }
    }

    if(print_inst){
        printf("Instance:\n");
        int p = 0;
        vector<int> rid(inst.nsizes);
        for(int it = 0; it < inst.nsizes; it++)
            rid[inst.items[it].id] = it;
        for(int i = 0; i < inst.m; i++){
            printf("i=%d (nopts: %d, demand: %d)\n", i+1, inst.nopts[i], inst.demands[i]);
            for(int q = 0; q < inst.nopts[i]; q++){
                printf("  opt=%d: (", q+1);
                for(int j = 0; j < inst.ndims; j++){
                    if(j) printf(", ");
                    printf("%d", inst.items[rid[p]][j]);
                }
                printf(")\n");
                p++;
            }
        }
    }

    if(pyout){
        printf("PYSOL=(%d, [", obj);
        for(int t = 0; t < inst.nbtypes; t++){
            printf(t == 0 ? "[" : ", [");
            vector<pattern_pair> &sol = sols[t];
            ForEach(pat, sol){
                vector<int_pair> tmp;
                ForEach(itr, pat->second){
                    int t = inst.items[itr->first].type;
                    int opt = inst.items[itr->first].opt;
                    for(int i = 0; i < itr->second; i++)
                        tmp.push_back(MP(t, opt));
                }
                sort(All(tmp));

                if(pat != sol.begin()) printf(", ");
                printf("(%d, [", pat->first);
                ForEach(p, tmp){
                    if(p != tmp.begin()) printf(", ");
                    if(p->second == -1)
                        printf("(%d, 0)", p->first);
                    else
                        printf("(%d, %d)", p->first, p->second);
                }
                printf("])");
            }
            printf("]");
        }
        printf("])\n");
    }
}
