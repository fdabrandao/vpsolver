/**
This code is part of the Arc-flow Vector Packing Solver (VPSolver).
**/
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cmath>
#include <map>
#include "config.hpp"
#include "common.hpp"
#include "arcflow.hpp"
#include "instance.hpp"
#include "arcflowsol.hpp"

int swig_main(int argc, char **argv) {
	printf(PACKAGE_STRING", Copyright (C) 2013-2022, Filipe Brandao\n");
	setvbuf(stdout, NULL, _IONBF, 0);
	if (argc < 3 || argc > 5) {
		printf("Usage: vbpsol graph.afg vars.sol "
			   "[print_instance:0] [pyout:0]\n");
		return 1;
	}
	FILE *fsol = NULL;
	try {
		throw_assert(check_ext(argv[1], ".afg"));
		Arcflow afg(argv[1]);
		Instance &inst = afg.inst;

		fsol = fopen(argv[2], "r");
		if (fsol == NULL) {
			perror("fopen");
		}
		throw_assert(fsol != NULL);

		bool print_inst = false;
		if (argc >= 4) {
			print_inst = atoi(argv[3]) != 0;
		}
		bool pyout = false;
		if (argc >= 5) {
			pyout = atoi(argv[4]) != 0;
		}

		int ind;
		double x;
		char buf[MAX_LEN];
		std::map<Arc, int> flow;
		while (fscanf(fsol, "%s %lf", buf, &x) != EOF) {
			if (strlen(buf) <= 1) {
				continue;
			}
			sscanf(&buf[1], "%x", &ind);
			throw_assert(ind < afg.NA);
			int rx = static_cast<int>(round(x));
			throw_assert(x - rx <= EPS);
			if (rx > 0) {
				flow[afg.A[ind]] = rx;
			}
		}
		fclose(fsol);

		ArcflowSol sol(inst, flow, afg.S, afg.Ts, afg.LOSS);
		sol.print_solution(print_inst, pyout);
		return 0;
	} catch (const std::runtime_error &e) {
		if (fsol != NULL) {
			fclose(fsol);
		}
		printf("%s\n", e.what());
		return 1;
	} catch (...) {
		if (fsol != NULL) {
			fclose(fsol);
		}
		printf("UnknownError\n");
		return 1;
	}
}

int main(int argc, char *argv[]) {
	return swig_main(argc, argv);
}
