set I := 1..5;
var x{I}, >= 0;
param c{I};

$FLOW[Z]{
    (10, 1, 1, 1, 1, 1),
    [(6, 1, 0, 0, 0, 0),
     (5, 0, 1, 0, 0, 0),
     (4, 0, 0, 1, 0, 0),
     (4, 0, 0, 0, 1, 0),
     (2, 0, 0, 0, 0, 1)],
    'x{1..5}'
};

var Z0, integer, >= 0;
maximize obj: Z0;
s.t. flow: Z = 1+2*Z0;
s.t. demand{i in I}: -x[i]+Z0 <= 0;

solve;
display Z0;
display x;
display {i in I} demand[i].dual;
end;
