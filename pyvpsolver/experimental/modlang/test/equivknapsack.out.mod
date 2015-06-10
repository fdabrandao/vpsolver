set I := 1..5;
var x{I}, >= 0;
param c{I};

/*EVALUATED:$FLOW[Z]{
    (10, 1, 1, 1, 1, 1),
    [(6, 1, 0, 0, 0, 0),
     (5, 0, 1, 0, 0, 0),
     (4, 0, 0, 1, 0, 0),
     (4, 0, 0, 0, 1, 0),
     (2, 0, 0, 0, 0, 1)],
    'x{1..5}'
};*/var _Z_F1, integer, >= 0;var _Z_F2, integer, >= 0;var _Z_F3, integer, >= 0;var _Z_F4, integer, >= 0;var _Z_F5, integer, >= 0;var _Z_F6, integer, >= 0;var _Z_F7, integer, >= 0;var _Z_F8, integer, >= 0;var _Z_F9, integer, >= 0;var _Z_Fa, integer, >= 0;var _Z_Fb, integer, >= 0;var _Z_Fc, integer, >= 0;var _Z_Fd, integer, >= 0;var _Z_Fe, integer, >= 0;var Z, integer, >= 0;s.t. _Z_RC0: + _Z_F3 + _Z_Fc - _Z_F5 - _Z_F8 - _Z_Fd = 0;s.t. _Z_RC1: + _Z_Fa + _Z_Fe - _Z_F1 - _Z_F4 - _Z_F7 - _Z_Fb = 0;s.t. _Z_RC2: + _Z_F1 + _Z_F8 + _Z_Fd - _Z_F6 - _Z_F9 = 0;s.t. _Z_RC3: + _Z_F4 + _Z_F7 + _Z_F9 - _Z_F2 = 0;s.t. _Z_RC4: + Z - _Z_F3 - _Z_Fa - _Z_Fc - _Z_Fe = 0;s.t. _Z_RC5: + _Z_F2 + _Z_F5 + _Z_F6 + _Z_Fb - Z = 0;s.t. _Z_RC6: + _Z_Fe - x[1] = 0;s.t. _Z_RC7: + _Z_Fa - x[2] = 0;s.t. _Z_RC8: + _Z_F3 + _Z_F7 - x[3] = 0;s.t. _Z_RC9: + _Z_F4 + _Z_Fd - x[4] = 0;s.t. _Z_RCa: + _Z_F9 - x[5] = 0;

var Z0, integer, >= 0;
maximize obj: Z0;
s.t. flow: Z = 1+2*Z0;
s.t. demand{i in I}: -x[i]+Z0 <= 0;

solve;
display Z0;
display x;
display {i in I} demand[i].dual;
data;

end;

