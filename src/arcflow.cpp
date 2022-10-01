/**
This code is part of the Arc-flow Vector Packing Solver (VPSolver).
**/
#include <climits>
#include <ctime>
#include <set>
#include <map>
#include <vector>
#include <algorithm>
#include "graph.hpp"
#include "common.hpp"
#include "arcflow.hpp"

/* Class Arcflow */

Arcflow::Arcflow(const Instance &_inst) {
	ready = false;
	tstart = CURTIME;
	init(_inst);
	throw_assert(ready == true);
}

Arcflow::Arcflow(const char *fname) {
	ready = false;
	tstart = CURTIME;
	init(fname);
	throw_assert(ready == true);
}

void Arcflow::init(const Instance &_inst) {
	throw_assert(ready == false);
	inst = _inst;
	LOSS = inst.nsizes;
	label_size = inst.ndims;
	sitems = inst.sorted_items();
	maxW.resize(label_size, 0);
	for (int d = 0; d < inst.ndims; d++) {
		for (int t = 0; t < inst.nbtypes; t++) {
			maxW[d] = std::max(maxW[d], inst.Ws[t][d]);
		}
	}

	max_label = maxW;
	if (inst.binary) {
		label_size = inst.ndims + 1;
		max_label.push_back(INT_MAX);
	}

	std::vector<int> max_state = maxW;
	max_state.push_back(inst.nsizes);
	if (!inst.binary) {
		int maxb = 0;
		for (int it = 0; it < inst.nsizes; it++) {
			maxb = std::max(maxb, sitems[it].demand);
		}
		max_state.push_back(maxb);
	}

	weights.resize(inst.nsizes);
	for (int i = 0; i < inst.nsizes; i++) {
		weights[i] = sitems[i].w;
	}
	weights.push_back(std::vector<int>(inst.ndims, 0));  // loss arcs

	max_rep = count_max_rep(maxW, 0, 0);

	for (int i = 0; i < static_cast<int>(max_state.size()); i++) {
		int nbits = 0, value = max_state[i];
		while (value) {
			nbits++;
			value >>= 1;
		}
		hash_bits.push_back(nbits);
	}

	printf("Build (method = %d)\n", inst.method);
	throw_assert(inst.method >= MIN_METHOD && inst.method <= MAX_METHOD);

	build();  // build step-3' graph
	int nv1 = NS.size() + inst.nbtypes;
	int na1 = A.size() + (NS.size() - 1) * inst.nbtypes + 1;
	printf("  Step-3' Graph: %d vertices and %d arcs (%.2fs)\n",
		   nv1, na1, TIMEDIF(tstart));

	final_compression_step();  // create step-4' graph
	finalize();  // add the final loss arcs
	int nv2 = NS.size() + Ts.size();
	int na2 = A.size();
	printf("  Step-4' Graph: %d vertices and %d arcs (%.2fs)\n",
		   nv2, na2, TIMEDIF(tstart));
	printf("  #V4/#V3 = %.2f\n", nv2 / static_cast<double>(nv1));
	printf("  #A4/#A3 = %.2f\n", na2 / static_cast<double>(na1));
	printf("Ready! (%.2fs)\n", TIMEDIF(tstart));
	throw_assert(ready == true);
}

void Arcflow::init(const char *fname) {
	throw_assert(ready == false);
	if (check_ext(fname, ".vbp")) {
		init(Instance(fname));
	} else if (check_ext(fname, ".mvp")) {
		init(Instance(fname));
	} else if (check_ext(fname, ".afg")) {
		read(fname);
	} else {
		throw_error("Invalid file extension");
	}
	throw_assert(ready == true);
}

bool Arcflow::is_valid(const std::vector<int> &u, const std::vector<int> &W) const {
	for (int i = 0; i < inst.ndims; i++) {
		if (u[i] > W[i]) {
			return false;
		}
	}
	return true;
}

bool Arcflow::is_full(const std::vector<int> &u, const std::vector<int> &W) const {
	for (int i = 0; i < inst.ndims; i++) {
		if (u[i] != W[i]) {
			return false;
		}
	}
	return true;
}

void Arcflow::relabel_graph(const std::vector<int> &labels) {
	std::set<Arc> arcs;
	for (const Arc &a : A) {
		int u = labels[a.u];
		int v = labels[a.v];
		if (u != v) {
			arcs.insert(Arc(u, v, a.label));
		}
	}
	A.assign(all(arcs));
}

std::vector<int> Arcflow::count_max_rep(const std::vector<int> &space, int i0 = 0,
										int sub_i0 = 0) const {
	std::vector<int> r(inst.nsizes);
	for (int i = i0; i < inst.nsizes; i++) {
		int dem = inst.binary ? 1 : sitems[i].demand;
		r[i] = i != i0 ? dem : std::max(0, dem - sub_i0);
		for (int d : sitems[i].nonzero) {
			r[i] = std::min(r[i], space[d] / weights[i][d]);
			if (!r[i]) {
				break;
			}
		}
	}
	return r;
}

int Arcflow::min_slack(const std::vector<int> &b, int i0, int d,
					   const std::vector<int> &caps) const {
	int C = caps.back();
	if (C == 0) {
		return 0;
	}
	std::vector<int> Q;
	std::vector<bool> vis(C + 1);
	vis[0] = true;
	Q.push_back(0);
	int res = 0;
	for (int i = i0; i < inst.nsizes; i++) {
		const int &w = weights[i][d];
		if (!w) {
			continue;
		}
		int qs = Q.size();
		for (int j = 0; j < qs; j++) {
			int u = Q[j];
			int v = u;
			for (int k = 1; k <= b[i]; k++) {
				v += w;
				if (v > C) {
					break;
				} else if (v == C) {
					return 0;
				} else if (vis[v]) {
					break;
				}
				res = std::max(res, v);
				Q.push_back(v);
			}
		}
		for (int j = qs; j < static_cast<int>(Q.size()); j++) {
			vis[Q[j]] = true;
		}
	}
	if (res <= caps[0]) {
		return caps[0] - res;
	} else {
		int mslack = C - res;
		for (int cap : caps) {
			int p = cap;
			while (!vis[p] && cap - p <= mslack) {
				p--;
			}
			mslack = std::min(mslack, cap - p);
		}
		return mslack;
	}
}

void Arcflow::lift_state(const std::vector<int> &valid_opts, std::vector<int> &u, int it,
						 int ic) const {
	if (it >= inst.nsizes) {
		return;
	}
	std::vector<int> space(inst.ndims);
	for (int d = 0; d < inst.ndims; d++) {
		space[d] = maxW[d] - u[d];
	}
	const std::vector<int> &r = count_max_rep(space, it, ic);
	for (int d = 0; d < inst.ndims; d++) {
		int minw = maxW[d];
		for (int t : valid_opts) {
			minw = std::min(minw, inst.Ws[t][d]);
		}
		if (u[d] != minw) {
			// lift method 1
			int maxpos = minw;
			for (int i = it; i < inst.nsizes && maxpos >= u[d]; i++) {
				maxpos -= r[i] * weights[i][d];
			}
			if (maxpos >= u[d]) {
				u[d] = maxpos;
			} else {
				// lift method 2
				std::vector<int> caps;
				for (int t : valid_opts) {
					caps.push_back(inst.Ws[t][d] - u[d]);
				}
				if (caps.size() > 1) {
					sort(all(caps));
					caps.erase(unique(all(caps)), caps.end());
				}
				u[d] += min_slack(r, it, d, caps);
			}
		}
	}
}

inline std::vector<int> Arcflow::hash(const std::vector<int> &su) {
	static int last_size = 1;
	std::vector<int> h;
	h.reserve(last_size);
	int *p = NULL, dst_bits = 0;
	for (int i = 0; i < static_cast<int>(su.size()); i++) {
		int x = su[i];
		int src_bits = hash_bits[i];
		while (src_bits != 0) {
			if (dst_bits == 0) {
				h.push_back(0);
				p = &h.back();
				dst_bits = sizeof(int) * 8;
			}
			int window_width = std::min(src_bits, dst_bits);
			*p <<= window_width;
			*p |= x & ((1u << window_width) - 1);
			x >>= window_width;
			src_bits -= window_width;
			dst_bits -= window_width;
		}
	}
	last_size = h.size();
	return h;
}

int Arcflow::go(std::vector<int> su) {
	int it = su[inst.ndims];
	int ic = inst.binary ? 0 : su[inst.ndims + 1];
	std::vector<int> valid_opts;
	std::vector<int> mu(max_label);
	std::vector<int> maxw(inst.ndims, 0);
	for (int t = 0; t < inst.nbtypes; t++) {
		if (is_valid(su, inst.Ws[t])) {
			valid_opts.push_back(t);
			for (int d = 0; d < inst.ndims; d++) {
				mu[d] = std::min(mu[d], inst.Ws[t][d]);
				maxw[d] = std::max(maxw[d], inst.Ws[t][d]);
			}
		}
	}
	if (valid_opts.empty()) {  // if invalid
		return -1;
	} else if (is_full(su, maxw)) {  // if full
		return NS.get_index(mu);
	} else {
		lift_state(valid_opts, su, it, ic);
	}

	// const vector<int> key(su);
	const std::vector<int> key(hash(su));
	std::map<std::vector<int>, int>::iterator itr = dp.find(key);
	if (itr != dp.end()) {
		return itr->second;
	}

	int up = -1;
	if (it + 1 < inst.nsizes) {
		std::vector<int> sv(su);
		sv[inst.ndims] = it + 1;
		if (!inst.binary) {
			sv[inst.ndims + 1] = 0;
		}
		up = go(sv);
		throw_assert(up != -1);
		mu = NS.get_label(up);
	}

	if (it < inst.nsizes && ic < max_rep[it]) {
		std::vector<int> sv(su);
		const std::vector<int> &w = weights[it];
		for (int d : sitems[it].nonzero) {
			sv[d] += w[d];
			if (sv[d] > maxw[d]) {  // if invalid
				return dp[key] = NS.get_index(mu);
			}
		}

		if (inst.binary) {
			sv[inst.ndims] = it + 1;
		} else {
			if (ic + 1 < max_rep[it]) {
				sv[inst.ndims] = it;
				sv[inst.ndims + 1] = ic + 1;
			} else {
				sv[inst.ndims] = it + 1;
				sv[inst.ndims + 1] = 0;
			}
		}

		int iv = go(sv);

		if (iv != -1) {
			const std::vector<int> &v = NS.get_label(iv);
			for (int d = 0; d < inst.ndims; d++) {
				mu[d] = std::min(mu[d], v[d] - w[d]);
			}
			if (inst.binary) {
				mu[inst.ndims] = std::min(mu[inst.ndims], it + 1);
			}
			int iu = NS.get_index(mu);
			AS.insert(Arc(iu, iv, it));
			if (up != -1 && iu != up) {
				AS.insert(Arc(iu, up, LOSS));
			}
		}
	}

	return dp[key] = NS.get_index(mu);
}

void Arcflow::build() {
	throw_assert(ready == false);
	dp.clear();
	A.clear();
	NS.clear();

	if (inst.binary) {
		go(std::vector<int>(label_size, 0));
	} else {
		go(std::vector<int>(label_size + 2, 0));
	}

	printf("  #dp: %d\n", static_cast<int>(dp.size()));

	dp.clear();
	A.assign(all(AS));
	AS.clear();

	relabel_graph(NS.topological_order());
	NS.sort();
}

void Arcflow::final_compression_step() {
	throw_assert(ready == false);
	int nv = NS.size();
	std::vector<int> labels(nv);
	std::vector<std::vector<int_pair>> adj = get_adj(nv, A, TRANSPOSE);

	NodeSet NStmp;
	for (int u = 0; u < NS.size(); u++) {
		std::vector<int> lbl(label_size, 0);
		for (const auto &pa : adj[u]) {
			throw_assert(pa.first < u);
			int v = labels[pa.first];
			int it = pa.second;
			const std::vector<int> &lv = NStmp.get_label(v);
			for (int d = 0; d < inst.ndims; d++) {
				lbl[d] = std::max(lbl[d], lv[d] + weights[it][d]);
			}
			if (inst.binary) {
				if (it == LOSS) {
					lbl[inst.ndims] = std::max(lbl[inst.ndims],
											   lv[inst.ndims]);
				} else {
					lbl[inst.ndims] = std::max(lbl[inst.ndims],
											   std::max(lv[inst.ndims], it));
				}
			}
		}
		labels[u] = NStmp.get_index(lbl);
	}

	NS = NStmp;
	std::vector<int> order = NS.topological_order();
	for (int &v : labels) {
		v = order[v];
	}
	relabel_graph(labels);
	NS.sort();
}

void Arcflow::reduce_redundancy() {
	throw_assert(ready == false);
	// remove redundant parallel arcs
	std::vector<int> types;
	for (int i = 0; i < inst.nsizes; i++) {
		types.push_back(sitems[i].type);
	}
	types.push_back(-1);
	auto comp_less = [&types](const Arc &a, const Arc &b) {
		return (a.u < b.u) ||
			   (a.u == b.u && a.v < b.v) ||
			   (a.u == b.u && a.v == b.v && types[a.label] < types[b.label]);
	};
	auto comp_equal = [&types](const Arc &a, const Arc &b) {
		return a.u == b.u && a.v == b.v && types[a.label] == types[b.label];
	};
	sort(all(A), comp_less);
	A.erase(unique(all(A), comp_equal), A.end());
}

void Arcflow::finalize() {
	throw_assert(ready == false);
	if (inst.nbtypes == 1) {
		S = 0;
		Ts.assign({NS.size()});
		A.push_back(Arc(Ts[0], S, LOSS));
		for (int i = 1; i < static_cast<int>(NS.size()); i++) {
			A.push_back(Arc(i, Ts[0], LOSS));
		}
	} else {
		S = 0;
		std::vector<int> torder;
		for (int i = 0; i < inst.nbtypes; i++) {
			torder.push_back(i);
		}
		sort(all(torder), [this](int a, int b) {
			return this->inst.Ws[a] < this->inst.Ws[b];
		});
		Ts.resize(inst.nbtypes);
		for (int i = 0; i < inst.nbtypes; i++) {
			Ts[torder[i]] = NS.size() + i;
		}
		for (int i = 0; i < inst.nbtypes; i++) {
			A.push_back(Arc(Ts[i], S, LOSS));
		}

		std::vector<std::vector<int>> bigger_than(inst.nbtypes);
		for (int t1 = 0; t1 < inst.nbtypes; t1++) {
			for (int t2 = 0; t2 < inst.nbtypes; t2++) {
				if (t1 != t2 && is_valid(inst.Ws[t1], inst.Ws[t2])) {
					if (inst.Ws[t1] != inst.Ws[t2] ||
						(t1 < t2 && inst.Ws[t1] == inst.Ws[t2])) {
						bigger_than[t1].push_back(t2);
					}
				}
			}
		}

		std::vector<bool> valid_tgts(inst.nbtypes);
		for (int i = 1; i < static_cast<int>(NS.size()); i++) {
			const std::vector<int> &u = NS.get_label(i);
			for (int t = 0; t < inst.nbtypes; t++) {
				valid_tgts[t] = is_valid(u, inst.Ws[t]);
			}
			for (int t1 = 0; t1 < inst.nbtypes; t1++) {
				if (valid_tgts[t1]) {
					for (int t2 : bigger_than[t1]) {
						valid_tgts[t2] = false;
					}
				}
			}
			for (int t = 0; t < inst.nbtypes; t++) {
				if (valid_tgts[t]) {
					A.push_back(Arc(i, Ts[t], LOSS));
				}
			}
		}

		for (int t1 = 0; t1 < inst.nbtypes; t1++) {
			valid_tgts.assign(inst.nbtypes, false);
			for (int t2 : bigger_than[t1]) {
				valid_tgts[t2] = true;
			}
			for (int t2 : bigger_than[t1]) {
				if (valid_tgts[t2]) {
					for (int t3 : bigger_than[t2]) {
						valid_tgts[t3] = false;
					}
				}
			}
			for (int t2 : bigger_than[t1]) {
				if (valid_tgts[t2]) {
					A.push_back(Arc(Ts[t1], Ts[t2], LOSS));
				}
			}
		}
	}
	reduce_redundancy();
	NV = NS.size() + Ts.size();
	NA = A.size();
	for (Arc &a : A) {
		if (a.label != LOSS) {
			a.label = sitems[a.label].id;
		}
	}
	ready = true;
}

void Arcflow::write(FILE *fout) {
	throw_assert(ready == true);
	sort(all(A));

	int iS = 0;
	fprintf(fout, "#GRAPH_BEGIN#\n");
	fprintf(fout, "$NBTYPES{%d};\n", inst.nbtypes);
	fprintf(fout, "$S{%d};\n", iS);
	fprintf(fout, "$Ts{");
	for (int t = 0; t < static_cast<int>(Ts.size()); t++) {
		if (t) fprintf(fout, ",");
		fprintf(fout, "%d", Ts[t]);
	}
	fprintf(fout, "};\n");

	fprintf(fout, "$LOSS{%d};\n", LOSS);

	int lastv = NS.size() - 1;
	fprintf(fout, "$NV{%d};\n", NV);
	fprintf(fout, "$NA{%d};\n", NA);

	sort(all(A));
	fprintf(fout, "$ARCS{\n");
	for (int i = 0; i < 3; i++) {
		for (const Arc &a : A) {
			if (i == 1 && a.u != iS) {
				continue;
			} else if (i == 2 && a.v <= lastv) {
				continue;
			} else if (i == 0 && (a.u == iS || a.v > lastv)) {
				continue;
			}
			if (a.label == LOSS) {
				fprintf(fout, "%d %d %d\n", a.u, a.v, LOSS);
			} else {
				fprintf(fout, "%d %d %d\n", a.u, a.v, a.label);
			}
		}
	}
	fprintf(fout, "};\n");
	fprintf(fout, "#GRAPH_END#\n");
}

void Arcflow::read(FILE *fin) {
	throw_assert(ready == false);
	tstart = CURTIME;
	inst = Instance(fin);
	throw_assert(fscanf(fin, " #GRAPH_BEGIN#") == 0);

	int nbtypes;
	throw_assert(fscanf(fin, " $NBTYPES { %d } ;", &nbtypes) == 1);
	throw_assert(nbtypes == inst.nbtypes);

	throw_assert(fscanf(fin, " $S { %d } ;", &S) == 1);

	Ts.resize(nbtypes);
	throw_assert(fscanf(fin, " $Ts { ") == 0);
	for (int i = 0; i < nbtypes; i++) {
		if (i) throw_assert(fscanf(fin, " ,") == 0);
		throw_assert(fscanf(fin, "%d", &Ts[i]) == 1);
	}
	throw_assert(fscanf(fin, " } ;") == 0);

	throw_assert(fscanf(fin, " $LOSS { %d } ;", &LOSS) == 1);

	throw_assert(fscanf(fin, " $NV { %d } ;", &NV) == 1);

	throw_assert(fscanf(fin, " $NA { %d } ;", &NA) == 1);

	throw_assert(fscanf(fin, " $ARCS {") == 0);
	for (int i = 0; i < NA; i++) {
		int i_u, i_v, label;
		throw_assert(fscanf(fin, " %d %d %d ", &i_u, &i_v, &label) == 3);
		A.push_back(Arc(i_u, i_v, label));
	}
	throw_assert(fscanf(fin, " } ;") == 0);
	throw_assert(fscanf(fin, " #GRAPH_END#") == 0);
	ready = true;
}

void Arcflow::write(const char *fname) {
	throw_assert(ready == true);
	FILE *fout = fopen(fname, "w");
	if (fout == NULL) {
		perror("fopen");
	}
	throw_assert(fout != NULL);
	write(fout);
	fclose(fout);
}

void Arcflow::read(const char *fname) {
	throw_assert(ready == false);
	throw_assert(check_ext(fname, ".afg"));
	FILE *fin = fopen(fname, "r");
	if (fin == NULL) {
		perror("fopen");
	}
	throw_assert(fin != NULL);
	read(fin);
	fclose(fin);
	throw_assert(ready == true);
}
