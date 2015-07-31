$GRAPH[V,A]{W, w, labels, bounds};

$PARAM[m]{m};

set I := 1..m;
var pi{I} >= 0;
var theta{V} >= 0;

minimize obj: theta['T'];
s.t. gamma{(u,v,i) in A}:
    theta[v] >= theta[u]+(if i != 'LOSS' then pi[i] else 0);
s.t. pisum: sum{i in I} pi[i] = 1+2*theta['T'];

solve;
display{i in I} pi[i];
display theta['T'];
end;
