/**
This code is part of the Arc-flow Vector Packing Solver (VPSolver).

Copyright (C) 2013, Filipe Brandao
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
#ifndef _ARCFLOW_MKP_HPP_
#define _ARCFLOW_MKP_HPP_

#include <set>
#include <map>
#include <ctime>
#include <vector>
#include <algorithm>
#include "graph.hpp"
#include "common.hpp"
#include "arcflow.hpp"
#include "instance.hpp"
using namespace std; 

class ArcflowMKP: public Arcflow{
private:
    int iS, iT, nv;
    adj_list adj;
    vector<int> pre_v;
    vector<int> pre_it;
    vector<double> dp1;
    vector<pair<double, int> > dp2;
    
    vector<int_pair> best_path(int best){
        int u = best;
        vector<int> path;
        while(u != iS){
            int item = pre_it[u];
            if(item != m)
                path.push_back(item);
            u = pre_v[u];    
        }
        sort(All(path));
        vector<int_pair> result;
        ForEach(it, path){
            if(result.empty() || *it != result.back().first)
                result.push_back(MP(*it, 1));  
            else
                result[result.size()-1].second++;
        }     
        return result;
    }
    
public:
    ArcflowMKP(const Instance &inst): Arcflow(inst) {
        iS = 0;
        iT = NS.size();
        nv = NS.size()+1;
        adj = get_adj(nv, A, TRANSPOSE);
    }
        
    vector<int_pair> knapsack(const vector<double> &values, double min_profit = 0){  
        return knapsack1(values, min_profit);
    }      
    
    vector<int_pair> knapsack1(const vector<double> &values, double min_profit = 0){
        dp1.assign(nv, -1);    
        pre_v.assign(nv, -1);
        pre_it.assign(nv, -1);    
        dp1[iS] = 0;
        
        int best = iS;                
        for(int v = iS+1; v < iT; v++){
            ForEach(itr, adj[v]){
                const int &u = itr->first;
                const int &it = itr->second;
                double value = dp1[u];
                if(it != m)
                    value += values[it];
                if(value > dp1[v]){
                    dp1[v] = value;
                    pre_v[v] = u;
                    pre_it[v] = it;
                    if(value > dp1[best])
                        best = v;
                }
            }
        }
        
        if(dp1[best] >= min_profit)
            return best_path(best);
        else
            return vector<int_pair>();
    }
        
    vector<int_pair> knapsack2(const vector<double> &values, double min_profit = 0){
        dp2.assign(nv, MP(-1, 0));    
        pre_v.assign(nv, -1);
        pre_it.assign(nv, -1);    
        dp2[iS] = MP(0, 0);
        
        int best = iS;       
        for(int v = iS+1; v < iT; v++){
            ForEach(itr, adj[v]){
                const int &u = itr->first;
                const int &it = itr->second;
                pair<double, int> value = dp2[u];
                if(it != m){
                    value.first += values[it];
                    value.second += 1;
                }
                if(value > dp2[v]){
                    dp2[v] = value;
                    pre_v[v] = u;
                    pre_it[v] = it;
                    if(value > dp2[best])
                        best = v;
                }
            }
        }
        
        if(dp2[best].first >= min_profit)
            return best_path(best);
        else
            return vector<int_pair>();
    }
};

#endif

