$PY{
lst = [
    ([8,12,13,64,22,41],80),
    ([8,12,13,75,22,41],96),
    ([3,6,4,18,6,4],20),
    ([5,10,8,32,6,12],36),
    ([5,13,8,42,6,20],44),
    ([5,13,8,48,6,20],48),
    ([0,0,0,0,8,0],10),
    ([3,0,4,0,8,0],18),
    ([3,2,4,0,8,4],22),
    ([3,2,4,8,8,4],24)
]
for i in xrange(len(lst)):
    a, a0 = lst[i]
    aS = abs(2*a0+1-sum(a))
    if a0 < (sum(a)-1)/2:
        a0 += aS
    a.append(aS)
    lst[i] = (a, a0)

a, a0 = lst[9]
print '>>', a, a0
"""
0: [8, 12, 13, 64, 22, 41, 1], 80 -> [1,1,1,4,2,2,0], 5 ok!
1: [8, 12, 13, 75, 22, 41, 22] 96 -> [0,1,1,5,2,2,2], 6 /dominated
2: [3, 6, 4, 18, 6, 4, 0] 20 ->      [1,1,1,4,1,1,0], 4
3: [5, 10, 8, 32, 6, 12, 0] 36 ->    [1,1,1,4,1,1,0], 4 /dominated
4: [5, 13, 8, 42, 6, 20, 5] 49 ->    [1,2,2,6,1,2,1], 7
5: [5, 13, 8, 48, 6, 20, 3] 51 ->    [1,1,1,4,1,1,0], 4
6: [0, 0, 0, 0, 8, 0, 13] 10 ->      [0,0,0,0,0,0,1], 0
7: [3, 0, 4, 0, 8, 0, 22] 18 ->      [0,0,0,0,0,0,1], 0
8: [3, 2, 4, 0, 8, 4, 24] 22 ->      [0,0,0,0,0,0,1], 0
9: [3, 2, 4, 8, 8, 4, 20] 24 ->      [1,1,1,2,2,1,5], 6 /dominated
"""

"""
a, a0 = [65, 64, 41, 22, 13, 12, 8, 2], 80
aS = abs(2*a0+1-sum(a))
if a0 < (sum(a)-1)/2:
    a0 += aS
a.append(aS)
"""

print a,a0

#a, a0 = [6,5,4,4,2], 10
m = len(a)
W = [a0]+[1]*len(a)
w = [[a[i]]+[1 if j == i else 0 for j in xrange(m)] for i in xrange(m)]
m = len(w)
labels = [i+1 for i in xrange(m)]
};

$GRAPH[V,A]{
    W,
    w,
    [i+1 for i in xrange(m)],
    [1 if w[i] <= W else 0 for i in xrange(m)]
};


set I := 1..7;
var pi{{0} union I} >= 0, integer;
var theta{V} >= 0;

minimize obj: pi[0];
s.t. gamma{(u,v,i) in A}: theta[v] >= theta[u]+(if i != 'LOSS' then pi[i] else 0);
s.t. pi0: pi[0] = theta['T'];
s.t. pisum: sum{i in I} pi[i] = 1+2*theta['T'];
solve;
display{i in I} pi[i];
display pi[0];
display theta['T'];


/*
set I := 1..5;
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
display conZ.dual;*/
