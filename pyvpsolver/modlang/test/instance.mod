$LOAD_VBP[instance1{I,D}]{"instance.vbp",1};
var x{I}, >= 0;

$FLOW[Z]{
    _instance1.W,
    _instance1.w,
    ["x[%d]"%i for i in _sets['I']]
};

$EXEC{
print _params['instance1_b']
print _instance1.b
print "_sets:", _sets.keys()
print "_params:", _params.keys()
};

minimize obj: Z;
s.t. demand{i in I}: x[i] >= instance1_b[i];

solve;
display Z;
display x;
end;
