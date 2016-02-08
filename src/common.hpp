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
#ifndef _COMMON_HPP_
#define _COMMON_HPP_

#define EPS 1e-5
#define MAX_LEN 256
#define TRANSPOSE (1)
#define all(x) (x).begin(),(x).end()
#define MP(x,y) make_pair(x,y)

#define MIN_METHOD -2
#define MAX_METHOD -2

#define CURTIME clock()
#define TIMEDIF(t0) (double(clock()-t0)/CLOCKS_PER_SEC)

#include <utility>
typedef std::pair<int, int> int_pair;

bool check_ext(const char* name, const char* extension);

extern char _error_msg_[MAX_LEN];

#define throw_error(error) \
{ \
    sprintf(_error_msg_, \
            "Error: `%s` in \"%s\" line %d", \
            error, __FILE__, __LINE__); \
    throw _error_msg_; \
}

#define throw_assert(condition) \
{ if (!(condition)) { \
    sprintf(_error_msg_, \
            "AssertionError: assertion `%s` failed in \"%s\" line %d", \
            #condition, __FILE__, __LINE__); \
    throw _error_msg_; \
} }

#endif
