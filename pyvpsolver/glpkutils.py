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
from .vpsolver import VPSolver


def mod2lp(fname_mod, fname_lp, verbose=False):
    """Converts a GMPL file into an LP file using GLPK."""
    if verbose:
        VPSolver.run(
            "glpsol --math {0} --check --wlp {1}".format(
                fname_mod, fname_lp
            )
        )
    else:
        VPSolver.run(
            "glpsol --math {0} --check --wlp {1} >> /dev/null".format(
                fname_mod, fname_lp
            )
        )


def mod2mps(fname_mod, fname_mps, verbose=False):
    """Converts a GMPL file into an MPS file using GLPK."""
    if verbose:
        VPSolver.run(
            "glpsol --math {0} --check --wmps {1}".format(
                fname_mod, fname_mps
            )
        )
    else:
        VPSolver.run(
            "glpsol --math {0} --check --wmps {1} >> /dev/null".format(
                fname_mod, fname_mps
            )
        )
