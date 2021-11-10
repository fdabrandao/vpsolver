/**
This code is part of the Arc-flow Vector Packing Solver (VPSolver).

Copyright (C) 2013-2021, Filipe Brandao <fdabrandao@gmail.com>
**/
#include <cstdio>
#include <cstdlib>
#include "config.hpp"
#include "arcflow.hpp"
#include "instance.hpp"

int swig_main(int argc, char **argv) {
	printf(PACKAGE_STRING", Copyright (C) 2013-2016, Filipe Brandao\n");
	setvbuf(stdout, NULL, _IONBF, 0);
	if (argc < 3 || argc > 6) {
		printf("Usage: vbp2afg instance.vbp/instance.mvp graph.afg "
			   "[method:-3] [binary:0] [vtype:I]\n");
		return 1;
	}
	FILE *fout = NULL;
	try {
		fout = fopen(argv[2], "w");
		if (fout == NULL) {
			perror("fopen");
		}
		throw_assert(fout != NULL);

		Instance inst(argv[1]);
		if (argc >= 4) {
			inst.method = atoi(argv[3]);
			throw_assert(inst.method >= MIN_METHOD &&
						 inst.method <= MAX_METHOD);
		}
		if (argc >= 5) {
			int value = atoi(argv[4]);
			if (value >= 0) {
				inst.binary = value;
			}
		}
		if (argc >= 6) {
			inst.vtype = argv[5][0];
			throw_assert(inst.vtype == 'I' || inst.vtype == 'C');
		}

		Arcflow graph(inst);
		inst.write(fout);
		graph.write(fout);

		fclose(fout);
		return 0;
	} catch (const char *e) {
		if (fout != NULL) {
			fclose(fout);
		}
		printf("%s\n", e);
		return 1;
	} catch (...) {
		if (fout != NULL) {
			fclose(fout);
		}
		printf("UnknownError\n");
		return 1;
	}
}

int main(int argc, char *argv[]) {
	return swig_main(argc, argv);
}
