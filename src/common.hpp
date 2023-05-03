/**
This code is part of the Arc-flow Vector Packing Solver (VPSolver).
**/
#ifndef SRC_COMMON_HPP_
#define SRC_COMMON_HPP_

#define EPS 1e-5
#define MAX_LEN 256
#define TRANSPOSE (1)
#define all(x) (x).begin(),(x).end()
#define MP(x, y) std::make_pair(x,y)

#define MIN_METHOD -3
#define MAX_METHOD -3

#define CURTIME clock()
#define TIMEDIF(t0) (static_cast<double>(clock()-t0)/CLOCKS_PER_SEC)

#include <utility>
#include <cstdio>
#include <exception>
#include <stdexcept>

typedef std::pair<int, int> int_pair;

bool check_ext(const char *name, const char *extension);

bool prefix(const char *pre, const char *str);

#define throw_error(error) \
{                          \
    char _error_msg_[MAX_LEN]; \
    snprintf(_error_msg_, MAX_LEN, \
            "Error: `%s` in \"%s\" line %d", \
            error, __FILE__, __LINE__); \
    throw std::runtime_error(_error_msg_); \
}

#define throw_assert(condition) \
{ if (!(condition)) {           \
	char _error_msg_[MAX_LEN]; \
    snprintf(_error_msg_, MAX_LEN, \
            "AssertionError: assertion `%s` failed in \"%s\" line %d", \
            #condition, __FILE__, __LINE__); \
    throw std::runtime_error(_error_msg_); \
} }

#endif  // SRC_COMMON_HPP_
