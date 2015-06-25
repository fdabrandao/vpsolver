\* Problem: 3 *\

Maximize
 obj: + Z0

Subject To
 flowcon(1): - f(1,T,LOSS) - f(1,3,4) - f(1,3,LOSS) + f(S,1,3)
 + f(S,1,LOSS) = -0
 flowcon(2): - f(2,4,3) - f(2,3,LOSS) - f(2,T,LOSS) - f(2,4,4)
 + f(S,2,2) + f(S,2,1) = -0
 flowcon(3): + f(1,3,4) + f(1,3,LOSS) + f(2,3,LOSS) - f(3,T,LOSS)
 - f(3,4,5) = -0
 flowcon(4): + f(2,4,3) + f(2,4,4) + f(3,4,5) - f(4,T,LOSS) = -0
 conZ: + f(1,T,LOSS) + f(2,T,LOSS) + f(3,T,LOSS) + f(4,T,LOSS) - Z = -0
 conZ0: + Z - 2 Z0 = 1
 demand(1): - f(S,2,1) + Z0 <= -0
 demand(2): - f(S,2,2) + Z0 <= -0
 demand(3): - f(S,1,3) - f(2,4,3) + Z0 <= -0
 demand(4): - f(1,3,4) - f(2,4,4) + Z0 <= -0
 demand(5): - f(3,4,5) + Z0 <= -0

Bounds
 Z free
 Z0 free

End
