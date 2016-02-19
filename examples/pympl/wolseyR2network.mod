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
s.t. flowcon{k in V}:
    sum{(u,v,i) in A: v == k} f[u,v,i] -  sum{(u,v,i) in A: u == k} f[u, v, i] = 0;
s.t. feedback: f['T', 'S', 'LOSS'] = 1+2*Z0;
s.t. demand{k in I}: sum{(u,v,i) in A: i == k} -f[u,v,i]+Z0 <= 0;
end;
