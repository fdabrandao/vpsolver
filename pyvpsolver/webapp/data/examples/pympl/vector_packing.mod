$EXEC{
W = [5180]
w = [[1120], [1250], [520], [1066], [1000], [1150]]
b = [9, 5, 91, 18, 11, 64]
};

$PARAM[b{I}]{b};

var x{I}, integer, >= 0;
$VBP_FLOW[Z]{W, w, ["x[%d]"%i for i in _sets['I']]};

minimize obj: Z;
s.t. demand{i in I}: x[i] >= b[i];

solve;
display Z;
end;
