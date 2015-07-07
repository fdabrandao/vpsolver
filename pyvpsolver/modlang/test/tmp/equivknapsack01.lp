\* Problem: equivknapsack01 *\

Minimize
 obj: + pi(0)

Subject To
 gamma('2',T,LOSS): + theta(T) - theta('2') >= -0
 gamma('1','4',5): - pi(5) + theta('4') - theta('1') >= -0
 gamma('7','8',LOSS): + theta('8') - theta('7') >= -0
 gamma('3',T,LOSS): + theta(T) - theta('3') >= -0
 gamma('9','10',2): - pi(2) + theta('10') - theta('9') >= -0
 gamma('9',T,LOSS): + theta(T) - theta('9') >= -0
 gamma('5','9',LOSS): + theta('9') - theta('5') >= -0
 gamma('5',T,LOSS): + theta(T) - theta('5') >= -0
 gamma('6',T,LOSS): + theta(T) - theta('6') >= -0
 gamma(S,'2',LOSS): + theta('2') - theta(S) >= -0
 gamma('8','9',LOSS): - theta('8') + theta('9') >= -0
 gamma(S,'2',5): - pi(5) + theta('2') - theta(S) >= -0
 gamma('4','7',3): - pi(3) - theta('4') + theta('7') >= -0
 gamma('6','10',3): - pi(3) + theta('10') - theta('6') >= -0
 gamma('2','3',LOSS): - theta('2') + theta('3') >= -0
 gamma('8',T,LOSS): + theta(T) - theta('8') >= -0
 gamma('4',T,LOSS): + theta(T) - theta('4') >= -0
 gamma('7','10',6): - pi(6) - theta('7') + theta('10') >= -0
 gamma('7',T,LOSS): + theta(T) - theta('7') >= -0
 gamma(S,'1',4): - pi(4) + theta('1') - theta(S) >= -0
 gamma('3','5',6): - pi(6) - theta('3') + theta('5') >= -0
 gamma('4','5',LOSS): - theta('4') + theta('5') >= -0
 gamma(S,'6',7): - pi(7) + theta('6') - theta(S) >= -0
 gamma('2','3',3): - pi(3) - theta('2') + theta('3') >= -0
 gamma('1',T,LOSS): + theta(T) - theta('1') >= -0
 gamma('8','10',1): - pi(1) - theta('8') + theta('10') >= -0
 gamma('10',T,LOSS): + theta(T) - theta('10') >= -0
 gamma('1','2',LOSS): + theta('2') - theta('1') >= -0
 gamma('5','9',1): - pi(1) + theta('9') - theta('5') >= -0
 gamma('3','5',LOSS): - theta('3') + theta('5') >= -0
 gamma('6','7',LOSS): + theta('7') - theta('6') >= -0
 gamma('4','8',6): - pi(6) - theta('4') + theta('8') >= -0
 pi0: + pi(0) - theta(T) = -0
 pisum: - 2 pi(0) + pi(5) + pi(2) + pi(3) + pi(6) + pi(4) + pi(7)
 + pi(1) = 1

End
