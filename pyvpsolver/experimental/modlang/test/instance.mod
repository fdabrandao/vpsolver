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

var y{I,I}, >= 0;
s.t. cenas: y[1,1] >= 10;

solve;
display Z;
display x;
display y;
end;
