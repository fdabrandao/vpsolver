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

vector<pair<int, vector<int_pair> > > ArcflowSol::remove_excess(
        const vector<pair<int, vector<int> > > &sol, vector<int> dem) const{
    vector<pair<int, vector<int_pair> > > tmp;
    ForEach(pat, sol){
        map<int, int> count;
        ForEach(it, pat->second) count[*it] += 1;
        vector<int> rm;
        int rep = pat->first;
        while(rep > 0){
            rm.clear();
            ForEach(itr, count){
                itr->second = min(itr->second, dem[itr->first]);
                if(itr->second == 0) rm.push_back(itr->first);
            }
            ForEach(ind, rm) count.erase(*ind);

            int f = rep;
            ForEach(itr, count)
                f = min(f, dem[itr->first]/itr->second);
            rep -= f;

            tmp.push_back(MP(f, vector<int_pair>(All(count))));
            ForEach(itr, count)
                dem[itr->first] -= f * itr->second;
        }
    }

    map<vector<int_pair>, int> m;
    ForEach(itr, tmp){
        sort(All(itr->second));
        m[itr->second] += itr->first;
    }

    vector<pair<int, vector<int_pair> > > final;
    ForEach(itr, m)
        final.push_back(MP(itr->second, itr->first));
    return final;
}

vector<pair<int, vector<int_pair> > > ArcflowSol::extract_solution(
        const vector<int> &dem){
    set<int> nodes;
    map<int, vector<Arc> > adj;
    ForEach(a, flow){
        int u = a->first.u;
        int v = a->first.v;
        nodes.insert(u);
        nodes.insert(v);
        adj[v].push_back(a->first);
    }

    vector<int> lst(All(nodes));

    vector<pair<int, vector<int> > > sol;
    while(true){
        map<int, Arc> pred;
        map<int, int> dp;
        dp[S] = INT_MAX;
        ForEach(v, lst){
            int &val = dp[*v];
            Arc &p = pred[*v];
            ForEach(a, adj[*v]){
                assert(dp.count(a->u) != 0);
                int m = min(dp[a->u], flow[*a]);
                if(m > val){
                    p = *a;
                    val = m;
                }
            }
        }
        int f = dp[T];
        if(f == 0) break;
        int v = T;
        sol.push_back(pair<int, vector<int> >());
        pair<int, vector<int> > &pat = sol.back();
        pat.first = f;
        while(v != S){
            Arc a = pred[v];
            int u = a.u;
            int lbl = a.label;
            if(lbl < (int)dem.size()) // != LOSS
                pat.second.push_back(lbl);
            flow[a] -= f;
            v = u;
        }
    }
    int fs = 0;
    ForEach(a, flow)
        fs += a->second;
    assert(fs == 0);
    return remove_excess(sol, dem);
}

bool ArcflowSol::is_valid(vector<pair<int, vector<int_pair> > > sol,
        const Instance &inst, int btype) const{
    vector<int> dem(inst.m);
    for(int i = 0; i < inst.m; i++)
        dem[i] = inst.items[i].demand;
    ForEach(pat, sol){
        vector<int> w(inst.ndims);
        ForEach(itr, pat->second){
            if(binary && itr->second > 1) return false;
            const Item &it = inst.items[itr->first];
            for(int i = 0; i < inst.ndims; i++)
                w[i] += it[i];
            dem[itr->first] -= pat->first * itr->second;
        }
        for(int i = 0; i < inst.ndims; i++)
            if(w[i] > inst.Ws[btype][i]) return false;
    }
    for(int i = 0; i < inst.m; i++){
        if(dem[i] != 0) return false;
    }
    return true;
}

void ArcflowSol::print_solution(const Instance &inst,
        bool print_inst = true, bool validate = true){
    vector<int> dem(inst.m), id(inst.m), rid(inst.m);
    for(int i = 0; i < inst.m; i++){
        dem[i] = inst.items[i].demand;
        int t = inst.items[i].id;
        id[i] = t;
        rid[t] = i;
    }
    vector<pair<int, vector<int_pair> > > sol = extract_solution(dem);
    if(validate)
        assert(is_valid(sol, inst, 0)); // FIXME

    int obj = 0;
    ForEach(pat, sol)
        obj += pat->first;

    printf("Objective: %d\n", obj);

    printf("Solution:\n");

    ForEach(pat, sol){
        vector<int> tmp;
        ForEach(itr, pat->second){
            int t = id[itr->first]+1;
            for(int i = 0; i < itr->second; i++)
                tmp.push_back(t);
        }
        sort(All(tmp));

        printf("%d x [", pat->first);
        ForEach(i, tmp){
            if(i != tmp.begin()) printf(", ");
            printf("i=%d", *i);
        }
        printf("]\n");
    }

    if(print_inst){
        printf("Instance:\n");
        for(int i = 0; i < inst.m; i++){
            printf("w_%d: (", i+1);
            for(int j = 0; j < inst.ndims; j++){
                if(j != 0) printf(", ");
                printf("%d", inst.items[rid[i]][j]);
            }
            printf(") b_%d: %d\n", i+1, inst.items[rid[i]].demand);
        }
    }
}
