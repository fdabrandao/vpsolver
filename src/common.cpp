/**
This code is part of the Arc-flow Vector Packing Solver (VPSolver).

Copyright (C) 2013-2016, Filipe Brandao
Faculdade de Ciencias, Universidade do Porto
Porto, Portugal. All rights reserved. E-mail: <fdabrandao@dcc.fc.up.pt>.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
**/
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include "common.hpp"

char _error_msg_[MAX_LEN];

bool check_ext(const char* name, const char* extension) {
    const char* end = strrchr(name, '.');
    return strcmp(end, extension) == 0;
}

bool prefix(const char *pre, const char *str) {
    return strncmp(pre, str, strlen(pre)) == 0;
}
