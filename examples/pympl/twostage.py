#!/usr/bin/env python
from __future__ import print_function
from builtins import range
from builtins import map
import os


def read_twostage(fname):
    """Loads two-stage instances."""
    with open(fname) as f:
        lst = list(map(int, f.read().split()))
        W = lst.pop(0)
        H = lst.pop(0)
        m = lst.pop(0)
        w, h, b = [], [], []
        for i in range(m):
            w.append(lst.pop(0))
            h.append(lst.pop(0))
            b.append(lst.pop(0))
        return W, H, w, h, b


def main():
    """Parses 'twostage.mod'."""
    from pympl import PyMPL, Tools, glpkutils

    os.chdir(os.path.dirname(__file__) or os.curdir)

    mod_in = "twostage.mod"
    mod_out = "tmp/twostage.out.mod"
    parser = PyMPL(locals_=locals(), globals_=globals())
    parser.parse(mod_in, mod_out)

    lp_out = "tmp/twostage.lp"
    glpkutils.mod2lp(mod_out, lp_out, True)

    out, varvalues = Tools.script("glpk_wrapper.sh", lp_out, verbose=True)

    print("")
    print(
        "varvalues:",
        [(k, v) for k, v in sorted(varvalues.items()) if not k.startswith("_")],
    )
    print("")
    assert varvalues["Z"] == 11  # check the solution objective value

    exctacted_solution = parser["VBP_FLOW"].extract(
        lambda name: varvalues.get(name, 0), verbose=True
    )

    solution = {}
    for zvar, value, sol in exctacted_solution:
        solution[zvar] = []
        for r, pattern in sol:
            solution[zvar] += [pattern] * r
        assert value == len(solution[zvar])

    def pop_pattern(zvar):
        pattern = []
        for it in solution[zvar].pop():
            if it not in solution:
                pattern.append(it)
            else:
                pattern.append((it, pop_pattern(it)))
        return pattern

    print("\n\nSolution:")
    for i in range(varvalues["Z"]):
        pattern = pop_pattern("Z")
        print("Sheet {}: {}".format(i + 1, pattern))


if __name__ == "__main__":
    main()
