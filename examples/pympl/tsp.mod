$EXEC{
n, xs, ys = read_tsp("data/tsp_51_1.txt")
#n, xs, ys = read_tsp("data/tsp_5_1.txt")
#n, xs, ys = read_tsp("data/tsp_20_1.txt")
#n, xs, ys = read_tsp("data/tsp_30_1.txt")
points = zip(xs, ys)

def length(point1, point2):
    from math import sqrt
    x1, y1 = point1
    x2, y2 = point2
    return sqrt((x2 - x1)**2 + (y2 - y1)**2)

dist = {
    (i+1,j+1): length(points[i], points[j])
    for i in xrange(n) for j in xrange(n)
    if i != j
}

V = range(1, n+1)

# time windows
start = 1
from random import randint, random, seed
seed(1234)
R = {i: randint(0, 60*24) for i in V if i != start}
D = {i: R[i]+60 for i in V if i != start}
R[start] = 0
D[start] = 0

maxdist = float(max(dist.values()))
travel = {
    (i, j): dist[i, j]/maxdist*10
    for (i, j) in dist
}

};

$PARAM[n]{n};
$SET[V]{V};
$PARAM[c{A}]{dist};
$PARAM[R]{R}; # release time of node i
$PARAM[D]{D}; # deadline of node i
$PARAM[T]{travel}; # travel time from i to j
$PARAM[start_node]{start};

var x{A}, binary;

minimize total: sum{(i,j) in A} c[i,j] * x[i,j];

# Single Commodity Flow Model
# Gavish and Graves (1978)
#$ATSP_SCF{{(i,j): "x[%d,%d]"%(i,j) for i, j in _sets['A']}, cuts=False};

# Multi Commodity Flow Model
# Wong (1980) and Claus (1984)
#$ATSP_MCF{{(i,j): "x[%d,%d]"%(i,j) for i, j in _sets['A']}, cuts=False};

# Miller, Tucker and Zemlin (MTZ) (1960)
#$ATSP_MTZ{{(i,j): "x[%d,%d]"%(i,j) for i, j in _sets['A']}, cuts=True};

# Desrochers and Laporte (1991)
$ATSP_MTZ{{(i,j): "x[%d,%d]"%(i,j) for i, j in _sets['A']}, DL=True, cuts=True};

# Time Windows:
var s{V}, >= 0;
param start := 1;
s.t. tw1{(i, j) in A: j != start_node}:
    s[j] >= s[i] + T[i,j] - (1-x[i,j])*(D[i] - R[j] + T[i,j]);
s.t. tw2{i in V: i != start_node}:
    s[i] >= R[i];
s.t. tw3{i in V: i != start_node}:
    s[i] <= D[i];

solve;
display x;
end;
