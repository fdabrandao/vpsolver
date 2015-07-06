#BEGIN_DEFS
param m := 3;
set bounds_I := {1,2,3};
param bounds{bounds_I};
set V := {'S','1','3','2','5','4','7','6','T'};
set A := {('4','7',2),('2','T','LOSS'),('S','1',2),('1','4',2),('S','2',1),('5','6',1),('7','T','LOSS'),('2','3',1),('4','5','LOSS'),('1','2','LOSS'),('4','T','LOSS'),('5','T','LOSS'),('S','1',3),('3','5',1),('3','T','LOSS'),('6','T','LOSS'),('1','T','LOSS'),('6','7',1)};
#END_DEFS
/*EVALUATED:$PARAM[m]{len(a)};*/
/*EVALUATED:$PARAM[bounds]{bounds,1};*/

set I := 1..m;
var pi{{0} union I} >= 0 integer;
var theta{V} >= 0;

/*EVALUATED:$EXEC{
m = len(a)
W = [a0]+bounds
w = [[a[i]]+[1 if j == i else 0 for j in xrange(m)] for i in xrange(m)]
b = bounds
labels = range(1,m+1)
};*/

/*EVALUATED:$GRAPH[V,A]{W, w, labels, b};*/

minimize obj: pi[0];
s.t. gamma{(u,v,i) in A}: theta[v] >= theta[u]+(if i != 'LOSS' then pi[i] else 0);
s.t. pi0: pi[0] = theta['T'];
s.t. pisum: sum{i in I} bounds[i]*pi[i] = 1+2*pi[0];

solve;

display{i in I} pi[i];
display pi[0];
data;
#BEGIN_DATA
param bounds := [1]5,[2]3,[3]1;
#END_DATA
end;

