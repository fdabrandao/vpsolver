$EXEC{
# bin capacities:
W1 = [100]
W2 = [120]
W3 = [150]

# bin costs:
Cs = [100, 120, 150]

# item weights:
ws = [[10], [14], [17], [19], [24], [29], [32], [33], [36],
      [38], [40], [50], [54], [55], [63], [66], [71], [77],
      [79], [83], [92], [95], [99]]

# item demands:
b = [1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1]
};

$PARAM[b{I}]{b, i0=1};
$PARAM[C{T}]{Cs, i0=1};

var x1{I};
var x2{I};
var x3{I};
$FLOW[Z1]{W1, ws, ["x1[%d]"%i for i in _sets['I']]};
$FLOW[Z2]{W2, ws, ["x2[%d]"%i for i in _sets['I']]};
$FLOW[Z3]{W3, ws, ["x3[%d]"%i for i in _sets['I']]};

minimize obj: C[1] * Z1 +  C[2] * Z2 + C[3] * Z3;
s.t. demand{i in I}: x1[i] + x2[i] + x3[i] >= b[i];

solve;
display Z1; # number of bins of type 1 used
display Z2; # number of bins of type 2 used
display Z3; # number of bins of type 3 used
display C[1] * Z1 +  C[2] * Z2 + C[3] * Z3; # cost
end;
