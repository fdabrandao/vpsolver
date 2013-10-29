/**
Copyright (C) 2013, Filipe Brandao
Faculdade de Ciencias, Universidade do Porto
Porto, Portugal. All rights reserved. E-mail: <fdabrandao@dcc.fc.up.pt>.
**/
#ifndef _COMMON_HPP_
#define _COMMON_HPP_

#define EPS 1e-5
#define MAX_LEN 256
#define TRANSPOSE (1)
#define All(x) (x).begin(),(x).end()
#define ForEach(i,c) for(__typeof((c).begin()) i = (c).begin(); i != (c).end(); i++)
#define MP(x,y) make_pair(x,y)

#define MIN_METHOD -2
#define MAX_METHOD 1

#define CURTIME clock()
#define TIMEDIF(t0) (double(clock()-t0)/CLOCKS_PER_SEC)

#include <utility>
typedef std::pair<int, int> int_pair;

#endif
