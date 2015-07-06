#BEGIN_DEFS
param m := 7;
set V := {'10','S','1','3','2','5','4','7','6','9','8','T'};
set A := {('2','T','LOSS'),('1','4',5),('7','8','LOSS'),('3','T','LOSS'),('9','10',2),('9','T','LOSS'),('5','9','LOSS'),('5','T','LOSS'),('6','T','LOSS'),('S','2','LOSS'),('8','9','LOSS'),('S','2',5),('4','7',3),('6','10',3),('2','3','LOSS'),('8','T','LOSS'),('4','T','LOSS'),('7','10',6),('7','T','LOSS'),('S','1',4),('3','5',6),('4','5','LOSS'),('S','6',7),('2','3',3),('1','T','LOSS'),('8','10',1),('10','T','LOSS'),('1','2','LOSS'),('5','9',1),('3','5','LOSS'),('6','7','LOSS'),('4','8',6)};
#END_DEFS
/*EVALUATED:$PARAM[m]{len(a)};*/

set I := 1..m;
var pi{{0} union I} >= 0;
var theta{V} >= 0;

/*EVALUATED:$EXEC{
m = len(a)
W = [a0]+[1]*len(a)
w = [[a[i]]+[1 if j == i else 0 for j in xrange(m)] for i in xrange(m)]
b = [1 for i in xrange(m)]
labels = [i+1 for i in xrange(m)]
};*/

/*EVALUATED:$GRAPH[V,A]{W, w, labels, b};*/

minimize obj: pi[0];
s.t. gamma{(u,v,i) in A}: theta[v] >= theta[u]+(if i != 'LOSS' then pi[i] else 0);
s.t. pi0: pi[0] = theta['T'];
s.t. pisum: sum{i in I} pi[i] = 1+2*pi[0];

solve;

display{i in I} pi[i];
display pi[0];
data;
#BEGIN_DATA
#END_DATA
end;

