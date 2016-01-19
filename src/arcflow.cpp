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
#include <bitset>
#include <algorithm>
#include "graph.hpp"
#include "common.hpp"
#include "arcflow.hpp"
using namespace std;

/* Class Arcflow */

Arcflow::Arcflow(const Instance &inst){
    tstart = CURTIME;
    ready = false;
    nsizes = inst.items.size();
    nbtypes = inst.nbtypes;
    W = inst.Ws[0]; // FIXME
    ndims = inst.ndims;
    items = inst.items;
    binary = inst.binary;
    int method = inst.method;

    ls_mat.assign(nsizes+1, vector<int>(ndims, 0));
    const vector<int> &r = max_rep(vector<int>(ndims, 0), 0, 0);
    for(int i = 0; i < nsizes; i++){
        int next = binary ? i+1 : i;
        for(int j = next; j < nsizes; j++){
            if(is_compatible(items[i], items[j])){
                for(int d = 0; d < ndims; d++)
                    ls_mat[i][d] = min(ls_mat[i][d]+r[j]*items[j][d], W[d]);
            }
        }
    }

    lsize = ndims;
    max_label = W;
    if(binary){
        lsize = ndims+1;
        max_label.push_back(INT_MAX);
    }

    Item loss(ndims);
    for(int d = 0; d < ndims; d++)
        loss[d] = 0;
    loss.demand = INT_MAX;
    items.push_back(loss);

    printf("Build (method = %d)\n", method);
    assert(method >= MIN_METHOD && method <= MAX_METHOD);
    if(method < 0){
        build_dp(); // build step-3' graph
        int nv1 = NS.size()+1;
        int na1 = A.size()+NS.size()-1;
        printf("  Step-3' Graph: %d vertices and %d arcs (%.2fs)\n",
            nv1, na1, TIMEDIF(tstart));

        if(method <= -2){
            final_compression_step(); // create step-4' graph

            int nv2 = NS.size()+1;
            int na2 = A.size()+NS.size()-1;
            printf("  Step-4' Graph: %d vertices and %d arcs (%.2fs)\n",
                nv2, na2, TIMEDIF(tstart));
            printf("  #V4/#V3 = %.2f\n", nv2/double(nv1));
            printf("  #A4/#A3 = %.2f\n", na2/double(na1));
        }
    }else{
        build(); // build step-1 graph
        int nv1 = NS.size()+1;
        int na1 = A.size()+NS.size()-1;
        printf("  Step-1 Graph: %d vertices and %d arcs (%.2fs)\n",
            nv1, na1, TIMEDIF(tstart));

        if(method >= 1){
            compress();
        }
    }
    finalize(); // add the final loss arcs
}

void Arcflow::compress(){
    assert(ready == false);
    int nv1 = NS.size()+1;
    int na1 = A.size()+NS.size()-1;

    break_symmetry(); // create step-2 graph

    int nv2 = NS.size()+1;
    int na2 = A.size()+NS.size()-1;
    printf("  Step-2 Graph: %d vertices and %d arcs (%.2fs)\n",
        nv2, na2, TIMEDIF(tstart));

    main_compression_step(); // create step-3 graph

    int nv3 = NS.size()+1;
    int na3 = A.size()+NS.size()-1;
    printf("  Step-3 Graph: %d vertices and %d arcs (%.2fs)\n",
        nv3, na3, TIMEDIF(tstart));

    final_compression_step(); // create step-4 graph

    int nv4 = NS.size()+1;
    int na4 = A.size()+NS.size()-1;
    printf("  Step-4 Graph: %d vertices and %d arcs (%.2fs)\n",
        nv4, na4, TIMEDIF(tstart));
    printf("  #V4/#V1 = %.2f\n", nv4/double(nv1));
    printf("  #A4/#A1 = %.2f\n", na4/double(na1));
}

bool Arcflow::is_valid(const vector<int> &u) const{
    for(int i = 0; i < ndims; i++)
        if(u[i] > W[i]) return false;
    return true;
}

bool Arcflow::is_compatible(const Item &a, const Item &b) const{
    for(int i = 0; i < ndims; i++)
        if(a[i]+b[i] > W[i]) return false;
    return true;
}

void Arcflow::relabel_graph(const vector<int> &label){
    set<Arc> arcs;
    ForEach(itr, A){
        int u = label[itr->u];
        int v = label[itr->v];
        if(u != v)
            arcs.insert(Arc(u, v, itr->label));
    }
    A.assign(All(arcs));
}

vector<int> Arcflow::max_rep(const vector<int> &u, int i0 = 0, int sub_i0 = 0) const{
    vector<int> r(nsizes);
    for(int i = i0; i < nsizes; i++){
        int dem = binary ? 1 : items[i].demand;
        if(i != i0)
            r[i] = dem;
        else
            r[i] = max(0, dem-sub_i0);
        for(int d = 0; d < ndims && r[i] > 0; d++)
            if(items[i][d] != 0)
                r[i] = min(r[i], (W[d]-u[d])/items[i][d]);
    }
    return r;
}

int Arcflow::knapsack(const vector<int> &b, int i0, int d, int C) const{
    if(C == 0) return 0;
    vector<int> Q;
    bool vis[C];
    memset(&vis, 0, sizeof(vis));
    vis[0] = true;
    Q.push_back(0);
    int res = 0;
    for(int i = i0; i < nsizes; i++){
        int w = items[i][d];
        int qs = Q.size();
        for(int j = 0; j < qs; j++){
            int u = Q[j];
            int v = u;
            for(int k = 1; k <= b[i]; k++){
                v += w;
                if(v > C) break;
                if(v == C) return v;
                if(vis[v]) break;
                res = max(res, v);
                Q.push_back(v);
            }
        }
        for(int j = qs; j < (int)Q.size(); j++)
            vis[Q[j]] = true;
    }
    return res;
}

void Arcflow::build(){
    A.clear();
    NS.clear();
    NS.get_index(vector<int>(lsize, 0));
    int nv = NS.size();
    for(int i = 0; i < nsizes; i++){
        for(int p = 0; p < nv; p++){
            int u = p;
            vector<int> lu = NS.get_label(u);
            int rep = items[i].demand;
            if(binary) rep = 1;
            for(int c = 0; c < rep; c++){
                vector<int> lv(lu);
                for(int d = 0; d < ndims; d++) lv[d] += items[i][d];
                if(binary) lv[ndims] = i;
                if(!is_valid(lv)) break;
                lift_state(lv, i, c+1);
                int v = NS.get_index(lv);
                assert(u != v);
                A.push_back(Arc(u, v, i));
                if(v < nv) break;
                u = v;
                lu = lv;
            }
        }
        nv = NS.size();
        printf("  %d: %d vertices and %d arcs (%.2fs)\n", i+1,
            (int)nv, (int)A.size(), TIMEDIF(tstart));
    }

    relabel_graph(NS.topological_order());
    NS.sort();
}

void Arcflow::lift_state(vector<int> &u, int it, int ic) const{
    for(int d = 0; d < ndims; d++){
        // lift method 1
        if(ic > 0)
            u[d] = max(u[d], W[d]-ls_mat[it][d]);
        else if(it > 0)
            u[d] = max(u[d], W[d]-ls_mat[it-1][d]);
    }
    const vector<int> &r = max_rep(u, it, ic);
    for(int d = 0; d < ndims; d++){
        if(u[d] < W[d]){
            // lift method 2
            int val = W[d];
            for(int t = it; t < nsizes && val >= u[d]; t++)
                val -= r[t]*items[t][d];

            if(val >= u[d]){
                u[d] = val;
            }else{
                // lift method 3
                u[d] = W[d]-knapsack(r, it, d, W[d]-u[d]);
            }
        }
    }
}

inline vector<int> Arcflow::hash(const vector<int> &su){
    if(ndims <= 1) return su;
    static size_t last_size = 1;
    vector<int> h(0);
    h.reserve(last_size);
    int *p = NULL, bits = 0;
    const int all = sizeof(int)*8;
    for(int d = 0; d < ndims; d++){
        int x = su[d], xl = W[d];
        while(xl != 0){
            if(bits == 0){
                h.push_back(0);
                p = &h.back();
                bits = all;
            }
            *p = (*p<<1)|(x&1);
            bits--;
            x >>= 1;
            xl >>= 1;
        }
    }
    for(int d = ndims; d < (int)su.size(); d++){
        h.push_back(su[d]);
    }
    last_size = h.size();
    return h;
}

int Arcflow::go(const vector<int> &su){
    //const vector<int> key(su);
    const vector<int> key(hash(su));
    map<vector<int>, int>::iterator itr = dp.find(key);
    if(itr != dp.end())
        return itr->second;

    int it = 0, ic = 0;
    if(binary){
        it = su[ndims];
    }else{
        it = su[ndims];
        ic = su[ndims+1];
    }

    vector<int> mu(max_label);

    int up = -1;
    if(it+1 < nsizes){
        vector<int> sv(su);
        sv[ndims] = it+1;
        if(!binary)
            sv[ndims+1] = 0;
        up = go(sv);
        mu = NS.get_label(up);
    }

    int dem = items[it].demand;
    if(it < nsizes && ic < dem){
        vector<int> sv(su);
        const vector<int> &w = items[it].w;
        for(int d = 0; d < ndims; d++)
            sv[d] += w[d];
        if(is_valid(sv)){
            int iv;
            if(binary){
                sv[ndims] = it+1;
                if(it+1 < nsizes)
                    lift_state(sv, it+1, 0);
                iv = go(sv);
            }else{
                if(ic+1 < dem){
                    sv[ndims] = it;
                    sv[ndims+1] = ic+1;
                    lift_state(sv, it, ic+1);
                }else{
                    sv[ndims] = it+1;
                    sv[ndims+1] = 0;
                    lift_state(sv, it+1, 0);
                }
                iv = go(sv);
            }
            const vector<int> &v = NS.get_label(iv);

            for(int d = 0; d < ndims; d++)
                mu[d] = min(mu[d], v[d]-w[d]);
            if(binary)
                mu[ndims] = min(mu[ndims], it+1);
            int iu = NS.get_index(mu);
            AS.insert(Arc(iu, iv, it));
            if(up != -1 && iu != up)
                AS.insert(Arc(iu, up, nsizes));
        }
    }

    return dp[key] = NS.get_index(mu);
}

void Arcflow::build_dp(){
    dp.clear();
    A.clear();
    NS.clear();

    if(binary)
        go(vector<int>(lsize, 0));
    else
        go(vector<int>(lsize+2, 0));

    printf("  #dp: %d\n", (int)dp.size());

    dp.clear();
    A.assign(All(AS));
    AS.clear();

    relabel_graph(NS.topological_order());
    NS.sort();
}

void Arcflow::break_symmetry(){
    assert(ready == false);
    vector<set<int> > groups(NS.size());

    NodeSet NStmp;
    ForEach(itr, A){
        assert(itr->label != nsizes);
        vector<int> lu(NS.get_label(itr->u));
        lu.push_back(itr->label);
        int nu = NStmp.get_index(lu);
        groups[itr->u].insert(nu);

        vector<int> lv(NS.get_label(itr->v));
        lv.push_back(itr->label);
        int nv = NStmp.get_index(lv);
        groups[itr->v].insert(nv);

        itr->u = nu;
        itr->v = nv;
    }

    vector<int> order = NStmp.topological_order();
    NS = NStmp;
    NS.sort();

    ForEach(itr, A){
        itr->u = order[itr->u];
        itr->v = order[itr->v];
        assert(itr->u < itr->v);
    }

    ForEach(itr, groups){
        vector<int> g(All(*itr));
        ForEach(v, g)
            *v = order[*v];
        sort(All(g));
        for(int i = 1; i < (int)g.size(); i++){
            int u = g[i-1], v = g[i];
            A.push_back(Arc(u, v, nsizes));
            assert(u < v);
        }
    }
}

void Arcflow::main_compression_step(){
    assert(ready == false);
    int nv = NS.size();
    vector<int> label(nv);
    vector<vector<int_pair> > adj = get_adj(nv, A);

    NodeSet NStmp;
    for(int u = NS.size()-1; u >= 0; u--){
        vector<int> lbl(max_label);
        ForEach(itr, adj[u]){
            assert(itr->first > u);
            int v = label[itr->first];
            int it = itr->second;
            const vector<int> &lv = NStmp.get_label(v);
            for(int d = 0; d < ndims; d++)
                lbl[d] = min(lbl[d], lv[d]-items[it][d]);
            if(binary)
                lbl[ndims] = min(lbl[ndims], min(lv[ndims], it));
        }
        label[u] = NStmp.get_index(lbl);
    }

    NS = NStmp;
    vector<int> order = NS.topological_order();
    ForEach(itr, label)
        *itr = order[*itr];
    relabel_graph(label);
    NS.sort();
}

void Arcflow::final_compression_step(){
    assert(ready == false);
    int nv = NS.size();
    vector<int> label(nv);
    vector<vector<int_pair> > adj = get_adj(nv, A, TRANSPOSE);

    NodeSet NStmp;
    for(int u = 0; u < NS.size(); u++){
        vector<int> lbl(lsize, 0);
        ForEach(itr, adj[u]){
            assert(itr->first < u);
            int v = label[itr->first];
            int it = itr->second;
            const vector<int> &lv = NStmp.get_label(v);
            for(int d = 0; d < ndims; d++)
                lbl[d] = max(lbl[d], lv[d]+items[it][d]);
            if(binary){
                if(it == nsizes)
                    lbl[ndims] = max(lbl[ndims], lv[ndims]);
                else
                    lbl[ndims] = max(lbl[ndims], max(lv[ndims], it));
            }
        }
        label[u] = NStmp.get_index(lbl);
    }

    NS = NStmp;
    vector<int> order = NS.topological_order();
    ForEach(itr, label)
        *itr = order[*itr];
    relabel_graph(label);
    NS.sort();
}

void Arcflow::finalize(){
    assert(ready == false);
    S = 0;
    int t = NS.size();
    Ts.clear();
    Ts.push_back(t); // FIXME
    for(int i = 1; i < NS.size(); i++)
        A.push_back(Arc(i, t, nsizes));
    for(int i = 0; i < (int)Ts.size(); i++){
        A.push_back(Arc(Ts[i], S, nsizes));
    }
    ready = true;
    printf("Ready! (%.2fs)\n", TIMEDIF(tstart));
}

void Arcflow::write(FILE *fout){
    assert(ready == true);
    sort(All(A));

    int iS = 0;
    fprintf(fout, "S: %d\n", iS);
    fprintf(fout, "Ts:");
    for(int t = 0; t < (int)Ts.size(); t++){
        fprintf(fout, " %d", Ts[t]);
    }
    fprintf(fout, "\n");

    fprintf(fout, "NV: %d\n", (int)NS.size()+1);
    fprintf(fout, "NA: %d\n", (int)A.size());

    sort(All(A));
    for(int i = 0; i < 3; i++){
        ForEach(a, A){
            if(i == 1 && a->u != iS) continue;
            if(i == 2 && a->v < Ts[0]) continue;
            if(i == 0 && (a->u == iS || a->v >= Ts[0])) continue;
            fprintf(fout, "%d %d %d\n", a->u, a->v, a->label);
        }
    }
}

void Arcflow::write(const char *fname){
    FILE *fout = fopen(fname, "w");
    assert(fout != NULL);
    write(fout);
    fclose(fout);
}
