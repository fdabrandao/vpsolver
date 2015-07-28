#!/usr/bin/env python
"""
This code is part of the Arc-flow Vector Packing Solver (VPSolver).

Copyright (C) 2013-2015, Filipe Brandao
Faculdade de Ciencias, Universidade do Porto
Porto, Portugal. All rights reserved. E-mail: <fdabrandao@dcc.fc.up.pt>.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import sys
sdir = os.path.dirname(__file__)
if sdir != "":
    os.chdir(sdir)

if __name__ == "__main__":
    if "test_install" in sys.argv:
        sys.argv.remove("test_install")
    else:
        project_dir = "../../"
        sys.path.insert(0, project_dir)
        os.environ["PATH"] = "{0}/scripts:{0}/bin:{1}".format(
            project_dir, os.environ["PATH"]
        )

from pyvpsolver.pympl import PyMPL, glpk_mod2lp
from pyvpsolver import VPSolver


def main():
    """Parses 'graph.mod'"""

    mod_in = "graph.mod"
    mod_out = "tmp/graph.out.mod"
    parser = PyMPL()
    parser.parse(mod_in, mod_out)

    lp_out = "tmp/graph.lp"
    glpk_mod2lp(mod_out, lp_out)
    out, varvalues = VPSolver.script_wsol(
        "vpsolver_glpk.sh", lp_out, verbose=True
    )

    sol, varvalues = parser["FLOW"].extract(varvalues, verbose=True)
    print
    print "sol:", sol
    print "varvalues:", [(k, v) for k, v in sorted(varvalues.items())]
    print

    os.system("glpsol --math {0} | grep -v Generating".format(mod_out))

if __name__ == "__main__":
    main()
