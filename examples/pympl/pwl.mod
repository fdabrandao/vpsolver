$EXEC{
xvalues = [0, 10, 15, 25, 30, 35, 40, 45, 50, 55, 60, 70]
yvalues = [0, 20, 15, 10, 0, 50, 18, 0, 15, 24, 10, 15]
};

var u >= 0;
$PWL[x,y]{zip(xvalues, yvalues)};

maximize obj: 2*x + 15*y;
s.t. A: 3*x + 4*y <= 250;
s.t. B: 7*x - 2*y + 3*u <= 170;

solve;
display x, y, u;
display "Objective:", 2*x + 15*y;
end;
