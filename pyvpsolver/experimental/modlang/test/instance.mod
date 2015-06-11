$LOAD_VBP[instance1]{"instance.vbp",1};

set I := 1..instance1_m;
var x{I}, >= 0;

$FLOW[Z]{
    instance1.W,
    instance1.w,
    'x{1..}'
};

minimize obj: Z;
s.t. demand{i in I}: x[i] >= instance1_b[i];

solve;
display Z;
display x;
end;
