$LOAD_VBP[instance1{I,D}]{"instance.vbp",1};

var x{I}, >= 0;

$FLOW[Z]{
    instance1.W,
    instance1.w,
    ["x[%d]"%i for i in I]
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
