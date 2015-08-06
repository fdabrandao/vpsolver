$PARAM[m]{len(a)};
$PARAM[bounds]{bounds,1};

set I := 1..m;
var pi{{0} union I} >= 0 integer;
var theta{V} >= 0;

$EXEC{
m = len(a)
W = [a0]+bounds
w = [[a[i]]+[1 if j == i else 0 for j in xrange(m)] for i in xrange(m)]
b = bounds
labels = range(1,m+1)
};

$VBP_GRAPH[V,A]{W, w, labels, b};

minimize obj: pi[0];
s.t. gamma{(u,v,i) in A}: theta[v] >= theta[u]+(if i != 'LOSS' then pi[i] else 0);
s.t. pi0: pi[0] = theta['T'];
s.t. pisum: sum{i in I} bounds[i]*pi[i] = 1+2*pi[0];

solve;

display{i in I} pi[i];
display pi[0];
