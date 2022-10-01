/**
This code is part of the Arc-flow Vector Packing Solver (VPSolver).
**/
#include <cstdio>
#include <cstring>
#include <cstdarg>
#include <vector>
#include "config.hpp"
#include "arcflow.hpp"
#include "instance.hpp"

/*
MPS format

Field:     1          2          3         4         5         6
Columns:  2-3        5-12      15-22     25-36     40-47     50-61
*/

#define BUF_LEN 80
#define NFIELDS 7

const int field_start[NFIELDS] = {0, 1, 4, 14, 24, 39, 49};

class MPS {
private:
	FILE *fout;
	int p;
	int cur_field;
	char buf[BUF_LEN];

	void clear() {
		p = 0;
		cur_field = 0;
		memset(buf, ' ', sizeof(buf));
	}

	void add_field(const char *str) {
		throw_assert(cur_field < NFIELDS);
		p = field_start[cur_field];
		for (int i = 0; str[i]; i++) {
			buf[p++] = str[i];
		}
		cur_field++;
	}

public:
	MPS(FILE *_fout = stdout) : fout(_fout) {}

	void write(int count, ...) {
		clear();

		va_list v;
		va_start(v, count);
		for (int i = 0; i < count; i++) {
			add_field(va_arg(v, const char *));
		}
		va_end(v);

		throw_assert(p < BUF_LEN);
		buf[p] = 0;
		fprintf(fout, "%s\n", buf);
		clear();
	}
};

int swig_main(int argc, char **argv) {
	printf(PACKAGE_STRING", Copyright (C) 2013-2022, Filipe Brandao\n");
	setvbuf(stdout, NULL, _IONBF, 0);
	if (argc != 3) {
		printf("Usage: afg2mps graph.afg model.mps\n");
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

		printf("Generating the .MPS model...");

		MPS mps(fout);
		mps.write(4, "NAME", "", "", "ARCFLOW");
		mps.write(1, "ROWS");
		mps.write(3, "", "N", "OBJ");

		char buf[BUF_LEN];
		char buf1[BUF_LEN];
		char buf2[BUF_LEN];

		/* demand constraints */

		for (int i = 0; i < inst.m; i++) {
			char ctype = inst.ctypes[i];
			throw_assert(ctype == '>' || ctype == '=');
			snprintf(buf, sizeof(buf), "B%d", i);
			if (ctype == '=' && !inst.relax_domains) {
				mps.write(3, "", "E", buf);
			} else {
				mps.write(3, "", "G", buf);
			}
		}

		/* flow conservation constraints */

		for (int i = 0; i < afg.NV; i++) {
			snprintf(buf, sizeof(buf), "F%x", i);
			mps.write(3, "", "E", buf);
		}

		/* A-matrix */

		mps.write(1, "COLUMNS");

		if (inst.vtype == 'I') {
			mps.write(6, "", "", "MARKER", "'MARKER'", "", "'INTORG'");
		}

		std::vector<int> labels;
		std::vector<int> ub(afg.NA);
		for (int i = 0; i < afg.NA; i++) {
			const Arc &a = afg.A[i];
			labels.push_back(a.label);
			snprintf(buf, sizeof(buf), "X%x", i);
			snprintf(buf1, sizeof(buf1), "F%x", a.u);
			snprintf(buf2, sizeof(buf2), "F%x", a.v);
			mps.write(7, "", "", buf, buf1, "-1", buf2, "1");
			if (a.label != afg.LOSS) {
				snprintf(buf1, sizeof(buf1), "B%d", inst.items[a.label].type);
				mps.write(5, "", "", buf, buf1, "1");
			}
			if (a.v == afg.S) {
				for (int j = 0; j < static_cast<int>(afg.Ts.size()); j++) {
					if (afg.Ts[j] == a.u) {
						ub[i] = (inst.Qs[j] >= 0) ? inst.Qs[j] : inst.n;
						snprintf(buf1, sizeof(buf1), "%d", inst.Cs[j]);
						mps.write(5, "", "", buf, "OBJ", buf1);
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

		if (inst.vtype == 'I') {
			mps.write(6, "", "", "MARKER", "'MARKER'", "", "'INTEND'");
		}

		/* right-hand-side vector */

		mps.write(1, "RHS");

		for (int i = 0; i < inst.m; i++) {
			snprintf(buf, sizeof(buf), "B%d", i);
			snprintf(buf1, sizeof(buf1), "%d", inst.demands[i]);
			mps.write(5, "", "", "RHS1", buf, buf1);
		}

		/* bounds */

		mps.write(1, "BOUNDS");

		for (int i = 0; i < afg.NA; i++) {
			snprintf(buf, sizeof(buf), "X%x", i);
			mps.write(5, "", "LO", "BND1", buf, "0");
			snprintf(buf1, sizeof(buf1), "%d", ub[i]);
			mps.write(5, "", "UP", "BND1", buf, buf1);
		}

		mps.write(1, "ENDATA");
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
