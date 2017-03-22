#!/usr/bin/env python
"""
This code is part of the Arc-flow Vector Packing Solver (VPSolver).

Copyright (C) 2013-2017, Filipe Brandao
Faculdade de Ciencias, Universidade do Porto
Porto, Portugal. All rights reserved. E-mail: <fdabrandao@dcc.fc.up.pt>.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from __future__ import print_function


def test_example():
    """Test example."""
    import example
    example.main()


def test_example_vbp():
    """Test example_vbp."""
    import example_vbp
    example_vbp.main()


def test_example_mvp():
    """Test example_mvp."""
    import example_mvp
    example_mvp.main()


def test_example_vsbpp():
    """Test example_vsbpp."""
    import example_vsbpp
    example_vsbpp.main()


if __name__ == "__main__":
    test_example()
    test_example_vbp()
    test_example_mvp()
    test_example_vsbpp()
