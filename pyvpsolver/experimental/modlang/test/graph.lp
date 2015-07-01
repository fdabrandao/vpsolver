\* Problem: 3 *\

Maximize
 obj: + Z0

Subject To
 flowcon(1): - f(1,T,LOSS) - f(1,8,1) - f(1,2,LOSS) + f(S,1,9) = -0
 flowcon(2): + f(1,2,LOSS) - f(2,8,2) - f(2,T,LOSS) - f(2,3,LOSS)
 + f(S,2,1) = -0
 flowcon(3): + f(2,3,LOSS) - f(3,T,LOSS) - f(3,4,LOSS) - f(3,5,3)
 + f(S,3,2) = -0
 flowcon(4): + f(3,4,LOSS) - f(4,T,LOSS) - f(4,6,LOSS) - f(4,6,4)
 + f(S,4,3) + f(S,4,LOSS) = -0
 flowcon(5): + f(3,5,3) - f(5,6,LOSS) - f(5,T,LOSS) - f(5,8,4) = -0
 flowcon(6): + f(4,6,LOSS) + f(4,6,4) + f(5,6,LOSS) - f(6,7,5)
 - f(6,7,LOSS) - f(6,T,LOSS) = -0
 flowcon(7): + f(6,7,5) + f(6,7,LOSS) - f(7,T,LOSS) - f(7,9,6)
 - f(7,9,LOSS) = -0
 flowcon(8): + f(1,8,1) + f(2,8,2) + f(5,8,4) - f(8,T,LOSS) - f(8,10,5)
 - f(8,10,6) - f(8,9,LOSS) = -0
 flowcon(9): + f(7,9,6) + f(7,9,LOSS) + f(8,9,LOSS) - f(9,10,LOSS)
 - f(9,T,LOSS) - f(9,10,7) = -0
 flowcon(10): + f(8,10,5) + f(8,10,6) + f(9,10,LOSS) + f(9,10,7)
 - f(10,T,LOSS) - f(10,11,8) = -0
 flowcon(11): + f(10,11,8) - f(11,T,LOSS) = -0
 conZ: + f(1,T,LOSS) + f(2,T,LOSS) + f(3,T,LOSS) + f(4,T,LOSS)
 + f(5,T,LOSS) + f(6,T,LOSS) + f(7,T,LOSS) + f(8,T,LOSS) + f(9,T,LOSS)
 + f(10,T,LOSS) + f(11,T,LOSS) - Z = -0
 conZ0: + Z - 2 Z0 = 1
 demand(1): - f(1,8,1) - f(S,2,1) + Z0 <= -0
 demand(2): - f(2,8,2) - f(S,3,2) + Z0 <= -0
 demand(3): - f(3,5,3) - f(S,4,3) + Z0 <= -0
 demand(4): - f(4,6,4) - f(5,8,4) + Z0 <= -0
 demand(5): - f(6,7,5) - f(8,10,5) + Z0 <= -0
 demand(6): - f(7,9,6) - f(8,10,6) + Z0 <= -0
 demand(7): - f(9,10,7) + Z0 <= -0
 demand(8): - f(10,11,8) + Z0 <= -0
 demand(9): - f(S,1,9) + Z0 <= -0

Bounds
 Z free
 Z0 free

End
