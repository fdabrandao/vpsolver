\* Problem: 3 *\

Maximize
 obj: + Z0

Subject To
 _Z_RC0: + _Z_F3 - _Z_F5 - _Z_F8 + _Z_Fc - _Z_Fd = -0
 _Z_RC1: - _Z_F1 - _Z_F4 - _Z_F7 + _Z_Fa - _Z_Fb + _Z_Fe = -0
 _Z_RC2: + _Z_F1 - _Z_F6 + _Z_F8 - _Z_F9 + _Z_Fd = -0
 _Z_RC3: - _Z_F2 + _Z_F4 + _Z_F7 + _Z_F9 = -0
 _Z_RC4: - _Z_F3 - _Z_Fa - _Z_Fc - _Z_Fe + Z = -0
 _Z_RC5: + _Z_F2 + _Z_F5 + _Z_F6 + _Z_Fb - Z = -0
 _Z_RC6: - x(1) + _Z_Fe = -0
 _Z_RC7: - x(2) + _Z_Fa = -0
 _Z_RC8: - x(3) + _Z_F3 + _Z_F7 = -0
 _Z_RC9: - x(4) + _Z_F4 + _Z_Fd = -0
 _Z_RCa: - x(5) + _Z_F9 = -0
 flow: + Z - 2 Z0 = 1
 demand(1): - x(1) + Z0 <= -0
 demand(2): - x(2) + Z0 <= -0
 demand(3): - x(3) + Z0 <= -0
 demand(4): - x(4) + Z0 <= -0
 demand(5): - x(5) + Z0 <= -0

End
