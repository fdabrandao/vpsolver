$LOAD_VBP[instance1]{"instance.vbp",1};

set I := 1..instance1_m;
var x{I}, >= 0;

/*$FLOW[Z]{
    instance1.W,
    instance1.w,
    'x{1..}'
};*/

/*$FLOW[Z]{
    instance1_W,
    instance1_w,
    'x{1..}'
};*/

/*$FLOW[Z]{
    instance1,
    'x{1..}'
};*/

/*$FLOW[Z]{
    instance1
};*/

/*$FLOW[Z]{
    instance1,
    'x',
    instance1_b
};*/

/*$FLOW[Z]{
    "instance.vbp"
};*/

$FLOW[Z]{
    "instance.vbp",
    'x'
};

$PY[model]{
print instance1_b
print instance1.b
};

minimize obj: Z;
s.t. demand{i in I}: x[i] >= instance1_b[i];

solve;
display Z;
display x;
end;
