#BEGIN_DEFS
param m := 9;
set V := {1,2,3,4,5,6,7,8,9,10,11,'S','T'};
set A := {(1,'T','LOSS'),(10,'T','LOSS'),(3,'T','LOSS'),(2,8,2),('S',3,2),('S',4,3),(5,6,'LOSS'),(2,'T','LOSS'),('S',1,9),(8,'T','LOSS'),(6,7,5),(11,'T','LOSS'),(4,'T','LOSS'),(7,'T','LOSS'),(6,7,'LOSS'),(9,10,'LOSS'),(4,6,'LOSS'),(3,4,'LOSS'),(2,3,'LOSS'),(9,'T','LOSS'),(7,9,6),(7,9,'LOSS'),(5,'T','LOSS'),(8,10,5),(6,'T','LOSS'),(3,5,3),(1,8,1),('S',2,1),(8,10,6),(1,2,'LOSS'),('S',4,'LOSS'),(10,11,8),(8,9,'LOSS'),(4,6,4),(5,8,4),(9,10,7)};
#END_DEFS
/*EVALUATED:$EXEC{
a, a0 = [65, 64, 41, 22, 13, 12, 8, 2], 80
aS = abs(2*a0+1-sum(a))
if a0 < (sum(a)-1)/2:
    a0 += aS
a.append(aS)

print 'self-dual:', a, a0

m = len(a)
W = [a0]+[1]*len(a)
w = [[a[i]]+[1 if j == i else 0 for j in xrange(m)] for i in xrange(m)]
labels = [i+1 for i in xrange(m)]
};*/

/*EVALUATED:$GRAPH[V,A]{
    W,
    w,
    labels,
    [1 if w[i] <= W else 0 for i in xrange(m)]
};*/

/*EVALUATED:$PARAM[m]{m};*/

/*
set I := 1..m;
var pi{{0} union I} >= 0, integer;
var theta{V} >= 0;

minimize obj: pi[0];
s.t. gamma{(u,v,i) in A}: theta[v] >= theta[u]+(if i != 'LOSS' then pi[i] else 0);
s.t. pi0: pi[0] = theta['T'];
s.t. pisum: sum{i in I} pi[i] = 1+2*pi[0];
solve;
display{i in I} pi[i];
display pi[0];
display theta['T'];
*/

set I := 1..m;
var f{A} >= 0;
var Z;
var Z0;

maximize obj: Z0;
s.t. flowcon{k in V diff {'S','T'}}: sum{(u,v,i) in A: v == k} f[u,v,i] - sum{(u,v,i) in A: u == k} f[u, v, i] = 0;
s.t. conZ: sum{(u,v,i) in A: v == 'T'} f[u,v,i] = Z;
s.t. conZ0: Z = 1+2*Z0;
s.t. demand{k in I}: sum{(u,v,i) in A: i == k} -f[u,v,i]+Z0 <= 0;

solve;
display {i in I} demand[i].dual;
display Z0;
display conZ.dual;
data;
#BEGIN_DATA
#END_DATA
end;

