$EXEC{
from pyvpsolver import MVP
inst = MVP.from_file("data/small.mvp")
};
$PARAM[nbtypes]{len(inst.Ws)};
$PARAM[Cs]{inst.Cs, i0=1};
$PARAM[Qs]{inst.Qs, i0=1};
$PARAM[m]{inst.m};
$PARAM[b]{inst.b, i0=1};

#$MVP_GRAPH[V, A]{
#    inst.Ws,
#    inst.ws,
#    {(i, j): "({},{})".format(i+1, j+1) for i in range(inst.m) for j in range(len(inst.ws[i]))}
#};

var cost;
var x{1..m}, >= 0;
var Z{i in 1..nbtypes}, >= 0, <= (if Qs[i] != -1 then Qs[i] else Infinity);

$MVP_FLOW[^Z[1], ^Z[2], ^Z[3], ^Z[4], ^Z[5]]{
    inst.Ws,
    inst.ws,
    ["x[{0}]".format(i+1) for i in range(inst.m)]
};

minimize obj: cost;
s.t. demand{i in 1..m}: x[i] >= b[i];
s.t. total_cost: cost = sum{i in 1..nbtypes} Z[i]*Cs[i];

solve;
display{i in 1..nbtypes} Z[i];
display x;
end;
