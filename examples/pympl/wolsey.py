#!/usr/bin/env python
from __future__ import print_function
from __future__ import division
from builtins import range
import os


def main():
    """Parses 'graph.mod'"""
    from pympl import PyMPL, Tools, glpkutils

    os.chdir(os.path.dirname(__file__) or os.curdir)

    a, a0 = [65, 64, 41, 22, 13, 12, 8, 2], 80
    aS = abs(2 * a0 + 1 - sum(a))
    if a0 < (sum(a) - 1) // 2:
        a0 += aS
    a.append(aS)

    print("self-dual:", a, a0)

    m = len(a)
    W = [a0] + [1] * len(a)
    w = [[a[i]] + [1 if j == i else 0 for j in range(m)] for i in range(m)]
    labels = [i + 1 for i in range(m)]
    bounds = [1 if w[i] <= W else 0 for i in range(m)]

    # wolseyR2network:

    print("-" * 10)
    print("Primal:")

    mod_in = "wolseyR2network.mod"
    mod_out = "tmp/wolseyR2network.out.mod"
    parser = PyMPL(locals_=locals(), globals_=globals())
    parser.parse(mod_in, mod_out)
    lp_out = "tmp/wolseyR2network.lp"
    glpkutils.mod2lp(mod_out, lp_out, verbose=False)
    out, varvalues = Tools.script("glpk_wrapper.sh", lp_out, verbose=False)
    print("")
    print("varvalues:", [(k, v) for k, v in sorted(varvalues.items())])
    print("")

    # Check the solution objective value:
    assert abs(varvalues["Z0"] - 9) < 1e-5

    # exit_code = os.system("glpsol --math {0}".format(mod_out))
    # assert exit_code == 0

    # wolseyR1gamma:

    print("-" * 10)
    print("wolseyR1gamma:")

    mod_in = "wolseyR1gamma.mod"
    mod_out = "tmp/wolseyR1gamma.mod.out.mod"
    parser = PyMPL(locals_=locals(), globals_=globals())
    parser.parse(mod_in, mod_out)
    lp_out = "tmp/wolseyR1gamma.mod.lp"
    glpkutils.mod2lp(mod_out, lp_out, verbose=False)
    out, varvalues = Tools.script("glpk_wrapper.sh", lp_out, verbose=False)
    print("")
    print("varvalues:", [(k, v) for k, v in sorted(varvalues.items())])
    print("")

    # Check the solution objective value:
    assert abs(varvalues["theta(T)"] - 9) < 1e-5

    # exit_code = os.system("glpsol --math {0}".format(mod_out))
    # assert exit_code == 0


if __name__ == "__main__":
    main()
