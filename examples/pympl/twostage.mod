/*
Models the two-stage two-dimensional guillotine cutting stock problem
based on a simplified version of Macedo et al. (2010) arc-flow model
*/

$EXEC{
W, H, w, h, b = read_twostage("data/twostage_A2.txt")
hcuts = sorted(set(h)|set(w))
};

$SET[HS]{hcuts};
$SET[I]{range(len(b))};
$PARAM[b{^I}]{b};

$EXEC{
HS = _sets["HS"]
I = _sets["I"]
};

# Stage 1 (horizontal cuts):
# Z is the number of sheets used
# hbars[h] is the number of horizontal strips of height h cut
var hbars{HS}, >= 0, integer;
$VBP_FLOW[Z]{
    [H],
    [[hc] for hc in hcuts],
    ["hbars[%d]"%height for height in HS]
};

# Stage 2 (vertical cuts):
# x[h, i] is the number of items of type i cut from strips of height h
var x{HS, I, {0, 1}}, >= 0, integer;
$EXEC{
for height in HS:
    ws, xvars, labels = [], [], []

    ws += [[w[it]] if h[it] <= height else [W+1] for it in I]
    xvars += ["x[%d,%d,0]"%(height, it) for it in I]
    labels += ["({}x{})".format(w[it], h[it]) for it in I]

    ws += [[h[it]] if w[it] <= height else [W+1] for it in I]
    xvars += ["x[%d,%d,1]"%(height, it) for it in I]
    labels += ["({}x{})^r".format(w[it], h[it]) for it in I]

    VBP_FLOW["^hbars[%d]"%height]([W], ws, xvars, labels=labels)
};

# Demand constraints:
s.t. demand{it in I}: sum{h in HS} (x[h, it, 0] + x[h, it, 1]) >= b[it];

minimize obj: Z;
end;
