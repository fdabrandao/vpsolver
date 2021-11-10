/**
This code is part of the Arc-flow Vector Packing Solver (VPSolver).

Copyright (C) 2013-2021, Filipe Brandao <fdabrandao@gmail.com>
**/
#ifndef SRC_GRAPH_HPP_
#define SRC_GRAPH_HPP_

#include <ctime>
#include <set>
#include <map>
#include <vector>
#include "common.hpp"

typedef std::vector<std::vector<int_pair>> adj_list;

class NodeSet {
private:
	std::map<std::vector<int>, int> index;
	std::vector<std::vector<int>> labels;
public:
	int get_index(const std::vector<int> &lbl);

	std::vector<int> get_label(int ind) const;

	int size() const;

	void clear();

	void sort();

	std::vector<int> topological_order() const;
};

class Arc {
public:
	int u;
	int v;
	int label;

	explicit Arc(const int &_u = -1, const int &_v = -1, int _label = -1) :
			u(_u), v(_v), label(_label) {}

	bool operator<(const Arc &o) const;

	bool operator==(const Arc &o) const;
};

adj_list get_adj(int nv, const std::vector<Arc> &arcs, bool transpose = false);

#endif  // SRC_GRAPH_HPP_
