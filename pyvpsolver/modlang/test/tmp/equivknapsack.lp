\* Problem: 3 *\

Minimize
 obj: + pi(0)

Subject To
 gamma('4','7',2): - pi(2) + theta('7') - theta('4') >= -0
 gamma('2',T,LOSS): + theta(T) - theta('2') >= -0
 gamma(S,'1',2): - pi(2) + theta('1') - theta(S) >= -0
 gamma('1','4',2): - pi(2) + theta('4') - theta('1') >= -0
 gamma(S,'2',1): - pi(1) + theta('2') - theta(S) >= -0
 gamma('5','6',1): - pi(1) + theta('6') - theta('5') >= -0
 gamma('7',T,LOSS): - theta('7') + theta(T) >= -0
 gamma('2','3',1): - pi(1) - theta('2') + theta('3') >= -0
 gamma('4','5',LOSS): - theta('4') + theta('5') >= -0
 gamma('1','2',LOSS): + theta('2') - theta('1') >= -0
 gamma('4',T,LOSS): - theta('4') + theta(T) >= -0
 gamma('5',T,LOSS): + theta(T) - theta('5') >= -0
 gamma(S,'1',3): - pi(3) + theta('1') - theta(S) >= -0
 gamma('3','5',1): - pi(1) + theta('5') - theta('3') >= -0
 gamma('3',T,LOSS): + theta(T) - theta('3') >= -0
 gamma('6',T,LOSS): + theta(T) - theta('6') >= -0
 gamma('1',T,LOSS): + theta(T) - theta('1') >= -0
 gamma('6','7',1): - pi(1) + theta('7') - theta('6') >= -0
 pi0: + pi(0) - theta(T) = -0
 pisum: - 2 pi(0) + 3 pi(2) + 5 pi(1) + pi(3) = 1

Generals
 pi(0)
 pi(2)
 pi(1)
 pi(3)

End
