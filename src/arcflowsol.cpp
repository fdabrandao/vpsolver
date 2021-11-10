/**
This code is part of the Arc-flow Vector Packing Solver (VPSolver).

Copyright (C) 2013-2021, Filipe Brandao <fdabrandao@gmail.com>
**/
#include <climits>
#include <cstring>
#include <ctime>
#include <set>
#include <map>
#include <vector>
#include <algorithm>
#include "graph.hpp"
#include "common.hpp"
#include "instance.hpp"
#include "arcflowsol.hpp"

/* Class ArcflowSol */

ArcflowSol::ArcflowSol(const Instance &_inst, const std::map<Arc, int> &_flow,
					   int _S, const std::vector<int> &_Ts, int _LOSS) :
		inst(_inst), flow(_flow), S(_S), Ts(_Ts), LOSS(_LOSS) {
	std::vector<int> dem(inst.m);
	for (int i = 0; i < inst.m; i++) {
		dem[i] = inst.demands[i];
	}

	objvalue = 0;
	sols.resize(inst.nbtypes);
	nbins.resize(inst.nbtypes);
	for (int t = 0; t < inst.nbtypes; t++) {
		sols[t] = extract_solution(&dem, Ts[t]);
		if (!is_valid(sols[t], t)) {
			throw_error("Invalid solution! (capacity)");
		}

		for (const pattern_pair &pat : sols[t]) {
			objvalue += pat.first * inst.Cs[t];
			nbins[t] += pat.first;
		}
	}

	for (int i = 0; i < inst.m; i++) {
		if (dem[i] > 0) {
			throw_error("Invalid solution! (demand)");
		}
	}

	int fs = 0;
	for (const auto &kvpair : flow) {
		fs += kvpair.second;
	}
	if (fs != 0) {
		throw_error("Invalid solution! (flow)");
	}
}

std::vector<pattern_pair> ArcflowSol::remove_excess(const std::vector<pattern_int> &sol,
													std::vector<int> *_dem) const {
	std::vector<int> &dem = *_dem;
	std::vector<pattern_pair> tmp;
	for (const pattern_int &pat : sol) {
		std::map<int, int> count;
		for (const int &it : pat.second) {
			count[it] += 1;
		}
		std::vector<int> rm;
		int rep = pat.first;
		while (rep > 0) {
			rm.clear();
			for (auto &kvpair : count) {
				int type = inst.items[kvpair.first].type;
				kvpair.second = std::min(kvpair.second, dem[type]);
				if (kvpair.second == 0) {
					rm.push_back(kvpair.first);
				}
			}
			for (const int &ind : rm) {
				count.erase(ind);
			}

			int f = rep;
			for (const auto &kvpair : count) {
				int type = inst.items[kvpair.first].type;
				f = std::min(f, dem[type] / kvpair.second);
			}
			rep -= f;

			tmp.push_back(MP(f, std::vector<int_pair>(all(count))));
			for (const auto &kvpair : count) {
				int type = inst.items[kvpair.first].type;
				dem[type] -= f * kvpair.second;
			}
		}
	}

	std::map<std::vector<int_pair>, int> mp;
	for (pattern_pair &pp : tmp) {
		sort(all(pp.second));
		mp[pp.second] += pp.first;
	}

	std::vector<pattern_pair> finalsol;
	for (const auto &kvpair : mp) {
		finalsol.push_back(MP(kvpair.second, kvpair.first));
	}
	return finalsol;
}

std::vector<pattern_pair> ArcflowSol::extract_solution(std::vector<int> *_dem, int T) {
	std::vector<int> &dem = *_dem;
	std::set<int> nodes;
	std::map<int, std::vector<Arc>> adj;
	for (const auto &kvpair : flow) {
		int u = kvpair.first.u;
		int v = kvpair.first.v;
		nodes.insert(u);
		nodes.insert(v);
		if (v != S) {
			adj[v].push_back(kvpair.first);
		}
	}

	int &zflow = flow[Arc(T, S, LOSS)];

	std::vector<int> lst(all(nodes));

	std::vector<pattern_int> sol;
	while (true) {
		std::map<int, Arc> pred;
		std::map<int, int> dp;
		dp[S] = zflow;
		for (const int &v : lst) {
			int &val = dp[v];
			Arc &p = pred[v];
			for (const Arc &a : adj[v]) {
				throw_assert(dp.count(a.u) != 0);
				int mf = std::min(dp[a.u], flow[a]);
				if (mf > val) {
					p = a;
					val = mf;
				}
			}
		}
		int f = dp[T];
		zflow -= f;
		if (f == 0) {
			break;
		}
		int v = T;
		sol.push_back(pattern_int());
		pattern_int &patt = sol.back();
		patt.first = f;
		while (v != S) {
			Arc a = pred[v];
			int u = a.u;
			int lbl = a.label;
			if (lbl != LOSS) {
				patt.second.push_back(lbl);
			}
			flow[a] -= f;
			v = u;
		}
	}
	return remove_excess(sol, &dem);
}

bool ArcflowSol::is_valid(const std::vector<pattern_pair> &sol, int btype) const {
	for (const pattern_pair &pat : sol) {
		std::vector<int> w(inst.ndims);
		for (const auto &itpair : pat.second) {
			if (inst.binary && itpair.second > 1) {
				return false;
			}
			const Item &it = inst.items[itpair.first];
			for (int i = 0; i < inst.ndims; i++) {
				w[i] += it[i] * itpair.second;
			}
		}
		for (int i = 0; i < inst.ndims; i++) {
			if (w[i] > inst.Ws[btype][i]) {
				return false;
			}
		}
	}
	return true;
}

void ArcflowSol::print_solution(bool print_inst = true, bool pyout = false) {
	printf("Objective: %d\n", objvalue);
	printf("Solution:\n");
	for (int t = 0; t < inst.nbtypes; t++) {
		if (inst.nbtypes > 1) {
			printf("Bins of type %d: %d\n", t + 1, nbins[t]);
		}
		std::vector<pattern_pair> &sol = sols[t];
		for (const pattern_pair &pat : sol) {
			std::vector<int_pair> tmp;
			for (const int_pair &itpair : pat.second) {
				int t = inst.items[itpair.first].type;
				int opt = inst.items[itpair.first].opt;
				for (int i = 0; i < itpair.second; i++) {
					tmp.push_back(MP(t, opt));
				}
			}
			sort(all(tmp));
			printf("%d x [", pat.first);
			bool first = true;
			for (const int_pair &p : tmp) {
				if (first) {
					first = false;
				} else {
					printf(", ");
				}
				if (p.second == -1) {
					printf("i=%d", p.first + 1);
				} else {
					printf("i=%d opt=%d", p.first + 1, p.second + 1);
				}
			}
			printf("]\n");
		}
	}

	if (print_inst) {
		inst.print();
	}

	if (pyout) {
		printf("PYSOL=(%d,[", objvalue);
		for (int t = 0; t < inst.nbtypes; t++) {
			printf("[");
			std::vector<pattern_pair> &sol = sols[t];
			for (const pattern_pair &pat : sol) {
				std::vector<int_pair> tmp;
				for (const int_pair &itpair : pat.second) {
					int t = inst.items[itpair.first].type;
					int opt = inst.items[itpair.first].opt;
					for (int i = 0; i < itpair.second; i++) {
						tmp.push_back(MP(t, opt));
					}
				}
				sort(all(tmp));

				printf("(%d,[", pat.first);
				for (const int_pair &p : tmp) {
					if (p.second == -1) {
						printf("(%d, 0),", p.first);
					} else {
						printf("(%d, %d),", p.first, p.second);
					}
				}
				printf("]),");
			}
			printf("],");
		}
		printf("])\n");
	}
}
