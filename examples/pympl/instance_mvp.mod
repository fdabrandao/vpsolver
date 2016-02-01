$EXEC{
from pyvpsolver import MVP
inst = MVP.from_file("data/small.mvp")
};
$PARAM[nbtypes]{len(inst.Ws)};
$PARAM[Cs]{inst.Cs, i0=1};
$PARAM[Qs]{inst.Qs, i0=1};
$PARAM[m]{inst.m};
$PARAM[b]{inst.b, i0=1};

set I := 1..m;
set T := 1..nbtypes;
var Z{T}, integer, >= 0;
var x{I}, >= 0;
var cost;

$MVP_FLOW[^Z{T}]{inst.Ws, inst.ws, ["x[{0}]".format(i+1) for i in range(inst.m)], i0=1};

/*
# MVP_FLOW is equivalent to:
$MVP_GRAPH[V, A]{
    inst.Ws,
    inst.ws,
    {(i, j): (i+1, j+1) for i in range(inst.m) for j in range(len(inst.ws[i]))},
    inst.b,
    S="S", Ts=["T{}".format(i+1) for i in range(len(inst.Ws))], LOSS=("LOSS", "ARC")
};
var f{(u, v, i, o) in A}, >= 0, <= (if i != 'LOSS' then b[i] else Infinity);
s.t. flow_con{k in V}:
    sum{(u, v, i, o) in A: v==k} f[u, v, i, o] - sum{(u, v, i, o) in A: u==k} f[u, v, i, o] = 0;
s.t. assocs{it in I}: x[it] = sum{(u, v, i, o) in A: i == it} f[u, v, i, o];
s.t. zvalues{t in T}: Z[t] = f['T'&t, 'S', 'LOSS', 'ARC'];
*/

minimize obj: cost;
s.t. demand{i in 1..m}: x[i] >= b[i];
s.t. zub{t in T: Qs[t] != -1}: Z[t] <= Qs[t];
s.t. total_cost: cost = sum{t in T} Z[t]*Cs[t];

solve;
display{t in 1..nbtypes} Z[t];
display x;
end;
