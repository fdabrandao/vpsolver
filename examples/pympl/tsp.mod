$EXEC{
#n, xs, ys = read_tsp("data/tsp_51_1.txt")
#n, xs, ys = read_tsp("data/tsp_5_1.txt")
n, xs, ys = read_tsp("data/tsp_20_1.txt")
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

};

$PARAM[n]{n};
$SET[V]{range(1, n+1)};
$PARAM[c{A}]{dist};

var x{A}, binary;

minimize total: sum{(i,j) in A} c[i,j] * x[i,j];

# Single Commodity Flow Model
# Gavish and Graves (1978)
$ATSP_FLOW{{(i,j): "x[%d,%d]"%(i,j) for i, j in _sets['A']}};

# Multi Commodity Flow Model
# Wong (1980) and Claus (1984)
#$ATSP_FLOW{{(i,j): "x[%d,%d]"%(i,j) for i, j in _sets['A']}, multi=True};

# Miller, Tucker and Zemlin (MTZ) (1960)
#$ATSP_MTZ{{(i,j): "x[%d,%d]"%(i,j) for i, j in _sets['A']}};

# Desrochers and Laporte (1991)
#$ATSP_MTZ{{(i,j): "x[%d,%d]"%(i,j) for i, j in _sets['A']}, DL=True};

solve;
display x;
end;
