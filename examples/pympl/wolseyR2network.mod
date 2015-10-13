/*
Wolsey, L. A. (1977). Valid inequalities, covering problems and discrete
dynamic programs.
*/
$VBP_GRAPH[V,A]{W, w, labels, bounds};

$PARAM[m]{m};

set I := 1..m;
var f{A} >= 0;
var Z;
var Z0;

maximize obj: Z0;
s.t. flowcon{k in V diff {'S'}}:
    sum{(u,v,i) in A: v == k} f[u,v,i] -  sum{(u,v,i) in A: u == k} f[u, v, i]
    = if k == 'T' then 1+2*Z0 else
      0;
s.t. demand{k in I}: sum{(u,v,i) in A: i == k} -f[u,v,i]+Z0 <= 0;

solve;
display {i in I} demand[i].dual;
display Z0;
end;
