$EXEC{
from pyvpsolver import VBP
instance = VBP.from_file("data/instance.vbp")
};
$SET[I]{range(instance.m)};
$PARAM[b{^I}]{instance.b};
var x{I}, >= 0;

$VBP_FLOW[Z]{
    instance.W,
    instance.w,
    ["x[%d]"%i for i in range(instance.m)]
};

minimize obj: Z;
s.t. demand{i in I}: x[i] >= b[i];

solve;
display Z;
display x;
end;
