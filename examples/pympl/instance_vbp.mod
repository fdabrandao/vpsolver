$EXEC{
from pyvpsolver import VBP
instance = VBP.from_file("data/instance.vbp")
};
$SET[I]{range(instance.m)};
$PARAM[b{^I}]{instance.b};
var x{I}, >= 0;
var Z, >= 0;

minimize obj: Z;
s.t. demand{i in I}: x[i] >= b[i];

$VBP_FLOW[^Z]{instance.W, instance.w, ["x[%d]"%i for i in range(instance.m)]};

/*
# VBP_FLOW is equivalent to:
$VBP_GRAPH[V,A]{instance.W, instance.w, range(instance.m), instance.b, S="S", T="T", LOSS="LOSS"};
var f{(u, v, i) in A}, >= 0, <= (if i != 'LOSS' then b[i] else Infinity);
s.t. flow_con{k in V}:
    sum{(u, v, i) in A: v==k} f[u, v, i] - sum{(u, v, i) in A: u==k} f[u, v, i] = 0;
s.t. assocs{it in I}: x[it] = sum{(u, v, i) in A: i == it} f[u, v, i];
s.t. zvalue: Z = f['T', 'S', 'LOSS'];
*/
end;
