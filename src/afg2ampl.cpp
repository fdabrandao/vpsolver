/**
This code is part of the Arc-flow Vector Packing Solver (VPSolver).
**/
#include <cstdio>
#include "config.hpp"
#include "common.hpp"
#include "arcflow.hpp"
#include "instance.hpp"

int swig_main(int argc, char **argv) {
	printf(PACKAGE_STRING", Copyright (C) 2013-2022, Filipe Brandao\n");
	setvbuf(stdout, NULL, _IONBF, 0);
	if (argc != 4) {
		printf("Usage: afg2ampl graph.afg model.mod data.dat\n");
		return 1;
	}
	try {
		throw_assert(check_ext(argv[1], ".afg"));
		Arcflow afg(argv[1]);
		Instance &inst = afg.inst;

		FILE *fmod = fopen(argv[2], "w");
		if (fmod == NULL) {
			perror("fopen");
		}
		throw_assert(fmod != NULL);

		FILE *fdat = fopen(argv[3], "w");
		if (fmod == NULL) {
			perror("fopen");
		}
		throw_assert(fdat != NULL);

		/* model file */
		printf("Generating the .mod file...");
		const char *model = \
			"set Items;\n"
			"param Demand{Items};\n"
			"set Labels;\n"
			"param ItemId{Labels};\n"
			"param ItemOpt{Labels};\n"
			"\n"
			"set V;\n"
			"set A dimen 3;\n"
			"param S;\n"
			"param LOSS;\n"
			"param ArcId{A};\n"
			"param ArcBounds{Labels union {LOSS}} default +Infinity;\n"
			"var Flow{(u,v,l) in A} integer >= 0 <= ArcBounds[l];\n"
			"set Targets;\n"
			"param Cost{Targets};\n"
			"param Quantity{Targets};\n"
			"\n"
			"minimize TotalCost:\n"
			"    sum{t in Targets} Cost[t] * Flow[t,S,LOSS];\n"
			"s.t. BinQuantity{t in Targets: Quantity[t] >= 0}:\n"
			"    Flow[t,S,LOSS] <= Quantity[t];\n"
			"param RelaxDomains default 1;\n"
			"s.t. SatisfyDemandStrict{i in Items: RelaxDomains != 1}:\n"
			"    sum{l in Labels : ItemId[l]==i} sum{(u,v,l) in A} Flow[u,v,l] == Demand[i];\n"
			"s.t. SatisfyDemandRelaxed{i in Items: RelaxDomains == 1}:\n"
			"    sum{l in Labels : ItemId[l]==i} sum{(u,v,l) in A} Flow[u,v,l] >= Demand[i];\n"
			"s.t. FlowConservation{k in V}:\n"
			"    (sum{(u,v,l) in A: v == k} Flow[u,v,l]) - (sum{(u,v,l) in A: u == k} Flow[u,v,l]) == 0;";
		fprintf(fmod, "%s", model);
		fclose(fmod);

		/* data file */
		printf("Generating the .dat file...");
		fprintf(fdat, "data;\n");
		fprintf(fdat, "set Targets :=");
		for (const int t : afg.Ts) {
			fprintf(fdat, " %d", t);
		}
		fprintf(fdat, ";\n");

		fprintf(fdat, "param Cost :=");
		for (size_t i = 0; i < afg.Ts.size(); i++) {
			fprintf(fdat, " %d %d", afg.Ts[i], inst.Cs[i]);
		}
		fprintf(fdat, ";\n");

		fprintf(fdat, "param Quantity :=");
		for (size_t i = 0; i < afg.Ts.size(); i++) {
			fprintf(fdat, " %d %d", afg.Ts[i], inst.Qs[i]);
		}
		fprintf(fdat, ";\n");

		fprintf(fdat, "set Items :=");
		for (int i = 0; i < inst.m; i++) {
			fprintf(fdat, " %d", i+1);
		}
		fprintf(fdat, ";\n");

		fprintf(fdat, "param Demand :=");
		for (int i = 0; i < inst.m; i++) {
			fprintf(fdat, " %d %d", i+1, inst.demands[i]);
		}
		fprintf(fdat, ";\n");

		fprintf(fdat, "param RelaxDomains := %d;\n", inst.relax_domains);

		if (!inst.relax_domains) {
			fprintf(fdat, "param ArcBounds :=");
			for (const Item &item : inst.items) {
				fprintf(fdat, " %d %d", item.id, item.demand);
			}
			fprintf(fdat, ";\n");
		}

		fprintf(fdat, "set Labels :=");
		for (const Item &item : inst.items) {
			fprintf(fdat, " %d", item.id);
		}
		fprintf(fdat, ";\n");

		fprintf(fdat, "param ItemId :=");
		for (const Item &item : inst.items) {
			fprintf(fdat, " %d %d", item.id, item.type+1);
		}
		fprintf(fdat, ";\n");

		fprintf(fdat, "param ItemOpt :=");
		for (const Item &item : inst.items) {
			fprintf(fdat, " %d %d", item.id, item.opt+1);
		}
		fprintf(fdat, ";\n");

		fprintf(fdat, "param S := %d;\n", afg.S);
		fprintf(fdat, "param LOSS := %d;\n", afg.LOSS);

		fprintf(fdat, "set V :=");
		for (int i = 0 ; i < afg.NV; i++) {
			fprintf(fdat, " %d", i);
		}
		fprintf(fdat, ";\n");

		fprintf(fdat, "set A :=");
		for (const Arc &a : afg.A) {
			fprintf(fdat, " (%d, %d, %d)", a.u, a.v, a.label);
		}
		fprintf(fdat, ";\n");
		fclose(fdat);

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
