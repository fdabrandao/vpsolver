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

import example
import example_vbp
import example_vsbpp
import example_mvbp


def main():
    """Runs all VPSolver examples."""

    print "example:"
    example.main()

    print "example_vbp:"
    example_vbp.main()

    print "example_vsbpp:"
    example_vsbpp.main()

    print "example_mvbp:"
    example_mvbp.main()


if __name__ == "__main__":
    main()
