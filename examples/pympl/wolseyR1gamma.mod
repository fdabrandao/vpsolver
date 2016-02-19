/*
Wolsey, L. A. (1977). Valid inequalities, covering problems and discrete
dynamic programs.
*/
$VBP_GRAPH[V,A]{W, w, labels, bounds};

$PARAM[m]{m};

set I := 1..m;
var pi{I} >= 0;
var theta{V} >= 0;

minimize obj: theta['T'];
s.t. gamma{(u,v,i) in A: v != 'S'}:
    theta[v] >= theta[u]+(if i != 'LOSS' then pi[i] else 0);
s.t. pisum: sum{i in I} pi[i] = 1+2*theta['T'];
end;
