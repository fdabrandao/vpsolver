/**
This code is part of the Arc-flow Vector Packing Solver (VPSolver).

Copyright (C) 2013-2021, Filipe Brandao <fdabrandao@gmail.com>
**/
#include <cstring>
#include "common.hpp"

bool check_ext(const char *name, const char *extension) {
	const char *end = strrchr(name, '.');
	return strcmp(end, extension) == 0;
}

bool prefix(const char *pre, const char *str) {
	return strncmp(pre, str, strlen(pre)) == 0;
}
