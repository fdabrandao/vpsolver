/**
This code is part of the Arc-flow Vector Packing Solver (VPSolver).
**/
#include <cstdio>
#include <cstdlib>
#include <map>
#include <vector>
#include "config.hpp"
#include "common.hpp"
#include "arcflow.hpp"
#include "instance.hpp"

/*
    LP format example:

    Maximize
        obj: x1 + 2 x2 + 3 x3 + x4
    Subject To
        c1: - x1 + x2 + x3 + 10 x4 <= 20
        c2: x1 - 3 x2 + x3 <= 30
        c3: x2 - 3.5 x4 = 0
    Bounds
        0 <= x1 <= 40
        2 <= x4 <= 3
    General
        x4
    End
*/

int swig_main(int argc, char **argv) {
	printf(PACKAGE_STRING", Copyright (C) 2013-2022, Filipe Brandao\n");
	setvbuf(stdout, NULL, _IONBF, 0);
	if (argc != 3) {
		printf("Usage: afg2mps graph.afg model.lp\n");
		return 1;
	}
	try {
		throw_assert(check_ext(argv[1], ".afg"));
		Arcflow afg(argv[1]);
		Instance &inst = afg.inst;

		FILE *fout = fopen(argv[2], "w");
		if (fout == NULL) {
			perror("fopen");
		}
		throw_assert(fout != NULL);

		printf("Generating the .LP model...");

		std::map<int, std::vector<int>> Ai;
		std::map<int, std::vector<int>> in;
		std::map<int, std::vector<int>> out;

		/* objective */

		fprintf(fout, "Minimize");
		std::vector<int> ub(afg.NA);
		for (int i = 0; i < afg.NA; i++) {
			const Arc &a = afg.A[i];
			Ai[a.label].push_back(i);
			in[a.v].push_back(i);
			out[a.u].push_back(i);
			if (a.v == afg.S) {
				for (int j = 0; j < static_cast<int>(afg.Ts.size()); j++) {
					if (afg.Ts[j] == a.u) {
						ub[i] = (inst.Qs[j] >= 0) ? inst.Qs[j] : inst.n;
						if (inst.Cs[j] >= 0) {
							fprintf(fout, " +%d X%x", inst.Cs[j], i);
						} else {
							fprintf(fout, " -%d X%x", abs(inst.Cs[j]), i);
						}
						break;
					}
				}
			} else {
				if (a.label != afg.LOSS && !inst.relax_domains) {
					ub[i] = inst.items[a.label].demand;
				} else {
					ub[i] = inst.n;
				}
			}
		}
		fprintf(fout, "\n");

		/* constraints */

		fprintf(fout, "Subject To\n");

		// demand constraints

		for (int i = 0; i < inst.m; i++) {
			if (inst.items[i].demand == 0) {
				continue;
			}
			fprintf(fout, "\tB%d:", i);
			for (int j = 0; j < inst.nsizes; j++) {
				if (inst.items[j].type == i) {
					for (const int &ai : Ai[j]) {
						fprintf(fout, " + X%x", ai);
					}
				}
			}
			if (inst.ctypes[i] == '=' && !inst.relax_domains) {
				fprintf(fout, " = %d", inst.demands[i]);
			} else {
				fprintf(fout, " >= %d", inst.demands[i]);
			}
			fprintf(fout, "\n");
		}

		// flow conservation constraints

		for (int i = 0; i < afg.NV; i++) {
			fprintf(fout, "\tF%x:", i);
			for (const int &ai : in[i]) {
				fprintf(fout, " + X%x", ai);
			}
			for (const int &ai : out[i]) {
				fprintf(fout, " - X%x", ai);
			}
			fprintf(fout, " = 0\n");
		}

		/* bounds */

		fprintf(fout, "Bounds\n");

		for (int i = 0; i < afg.NA; i++) {
			fprintf(fout, "0 <= X%x <= %d\n", i, ub[i]);
		}

		/* integer variables */

		if (inst.vtype == 'I') {
			fprintf(fout, "General\n");

			fprintf(fout, "\t");
			for (int i = 0; i < afg.NA; i++) {
				if (!i) {
					fprintf(fout, "X%x", i);
				} else {
					fprintf(fout, " X%x", i);
				}
			}
		}

		fprintf(fout, "\nEnd\n");
		fclose(fout);
		printf("DONE!\n");
		return 0;
	} catch (const std::runtime_error &e) {
		printf("%s\n", e.what());
		return 1;
	} catch (...) {
		printf("UnknownError\n");
		return 1;
	}
}

int main(int argc, char *argv[]) {
	return swig_main(argc, argv);
}
