$PY{
a, a0 = [65, 64, 41, 22, 13, 12, 8, 2], 80
aS = abs(2*a0+1-sum(a))
if a0 < (sum(a)-1)/2:
    a0 += aS
a.append(aS)

print 'sel-dual:', a, a0

#a, a0 = [6,5,4,4,2], 10
m = len(a)
W = [a0]+[1]*len(a)
w = [[a[i]]+[1 if j == i else 0 for j in xrange(m)] for i in xrange(m)]
labels = [i+1 for i in xrange(m)]
};

$GRAPH[V,A]{
    W,
    w,
    labels,
    [1 if w[i] <= W else 0 for i in xrange(m)]
};


/*
set I := 1..9;
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

set I := 1..9;
var f{A} >= 0;
var Z;
var Z0;

$SET[stest1]{range(10)};
$PARAM[ptest2]{{(i,'a',i):i for i in range(10)}};
$PARAM[ptest3{indexset}]{range(10)};
$PARAM[ptest4]{10};
display indexset;

set I1 := 1..2;
set I2 := 1..2;
set I3 := 1..2;
set II := I1 cross I2 cross I3;
display II;
param coise{II} default 0;
param coise2{(i,j,k) in II} := coise[i,j,k];

maximize obj: Z0;
s.t. flowcon{k in V diff {'S','T'}}: sum{(u,v,i) in A: v == k} f[u,v,i] - sum{(u,v,i) in A: u == k} f[u, v, i] = 0;
s.t. conZ: sum{(u,v,i) in A: v == 'T'} f[u,v,i] = Z;
s.t. conZ0: Z = 1+2*Z0;
s.t. demand{k in I}: sum{(u,v,i) in A: i == k} -f[u,v,i]+Z0 <= 0;

solve;
display {i in I} demand[i].dual;
display Z0;
display conZ.dual;
