/**
This code is part of the Arc-flow Vector Packing Solver (VPSolver).

Copyright (C) 2013-2021, Filipe Brandao <fdabrandao@gmail.com>
**/
#ifndef SRC_ARCFLOWSOL_HPP_
#define SRC_ARCFLOWSOL_HPP_

#include <ctime>
#include <set>
#include <map>
#include <vector>
#include <utility>
#include "graph.hpp"
#include "common.hpp"
#include "instance.hpp"

typedef std::pair<int, std::vector<int>> pattern_int;
typedef std::pair<int, std::vector<int_pair>> pattern_pair;

class ArcflowSol {
private:
	Instance inst;
	std::map<Arc, int> flow;
	int S;
	std::vector<int> Ts;
	int LOSS;
	int objvalue;
	std::vector<int> nbins;
	std::vector<std::vector<pattern_pair>> sols;

	std::vector<pattern_pair> extract_solution(std::vector<int> *_dem, int T);

	std::vector<pattern_pair> remove_excess(const std::vector<pattern_int> &sol,
											std::vector<int> *_dem) const;

	bool is_valid(const std::vector<pattern_pair> &sol, int btype) const;

public:
	ArcflowSol(const Instance &_inst, const std::map<Arc, int> &_flow, int _S,
			   const std::vector<int> &_Ts, int _LOSS);

	void print_solution(bool print_inst, bool pyout);
};

#endif  // SRC_ARCFLOWSOL_HPP_
