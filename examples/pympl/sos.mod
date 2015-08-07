$EXEC{
xvalues = [0, 10, 15, 25, 30, 35, 40, 45, 50, 55, 60, 70]
yvalues = [0, 20, 15, 10, 0, 50, 18, 0, 15, 24, 10, 15]
};

$PARAM[X{I}]{xvalues};
$PARAM[Y{^I}]{yvalues};

var x;
var y;
var u >= 0;

var z{I}, >= 0;
s.t. fix_x: x = sum{i in I} X[i] * z[i];
s.t. fix_y: y = sum{i in I} Y[i] * z[i];
s.t. convexity: sum{i in I} z[i] = 1;

$SOS2{["z[%d]"%i for i in _sets['I']]};

s.t. A: 3*x + 4*y <= 250;
s.t. B: 7*x - 2*y + 3*u <= 170;

maximize obj: 2*x + 15*y;

solve;
display x, y, u;
display z;
display "Objective:", 2*x + 15*y;
end;
