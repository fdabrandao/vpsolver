$EXEC{
# bin capacities:
W1 = [100]
W2 = [120]
W3 = [150]

# bin costs:
Costs = [100, 120, 150]

# item weights:
ws = [[10], [14], [17], [19], [24], [29], [32], [33], [36],
      [38], [40], [50], [54], [55], [63], [66], [71], [77],
      [79], [83], [92], [95], [99]]

# item demands:
b = [1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1]
};

$PARAM[b{I}]{b, i0=1};
$PARAM[C{T}]{Costs, i0=1};

var Z{T}, integer, >= 0;
var x{T, I}, integer, >= 0;
$VBP_FLOW[^Z[1]]{W1, ws, ["x[1, %d]"%i for i in _sets['I']]};
$VBP_FLOW[^Z[2]]{W2, ws, ["x[2, %d]"%i for i in _sets['I']]};
$VBP_FLOW[^Z[3]]{W3, ws, ["x[3, %d]"%i for i in _sets['I']]};

minimize obj: sum{t in T} C[t] * Z[t];
s.t. demand{i in I}: sum{t in T} x[t, i] >= b[i];

solve;
display{t in T} Z[t]; # number of bins of type t used
display sum{t in T} C[t] * Z[t]; # cost
end;
