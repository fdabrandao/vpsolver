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

};

$PARAM[n]{n};
$SET[V]{range(1, n+1)};
$PARAM[c{E}]{dist};

var x{E}, binary;

minimize total: sum{(i,j) in E} c[i,j] * x[i,j];

$TSP_SCF{{(i,j): "x[%d,%d]"%(i,j) for i, j in _sets['E']}};

solve;
display x;
end;
