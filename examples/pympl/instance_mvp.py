#!/usr/bin/env python
"""
This code is part of the Arc-flow Vector Packing Solver (VPSolver).

Copyright (C) 2013-2016, Filipe Brandao <fdabrandao@gmail.com>
"""
from __future__ import print_function
import os


def main():
    """Parses 'instance_mvp.mod'"""
    from pympl import PyMPL, Tools, glpkutils

    os.chdir(os.path.dirname(__file__) or os.curdir)

    mod_in = "instance_mvp.mod"
    mod_out = "tmp/instance_mvp.out.mod"
    parser = PyMPL(locals_=locals(), globals_=globals())
    parser.parse(mod_in, mod_out)

    lp_out = "tmp/instance_mvp.lp"
    glpkutils.mod2lp(mod_out, lp_out, True)
    out, varvalues = Tools.script("glpk_wrapper.sh", lp_out, verbose=True)
    sol = parser["MVP_FLOW"].extract(
        lambda varname: varvalues.get(varname, 0), verbose=True
    )

    print("")
    print("sol:", sol)
    print("varvalues:", [(k, v) for k, v in sorted(varvalues.items())])
    print("")
    assert varvalues["cost"] == 8  # check the solution objective value

    # exit_code = os.system("glpsol --math {0}".format(mod_out))
    # assert exit_code == 0


if __name__ == "__main__":
    main()
