#!/usr/bin/env python
"""
This code is part of the Arc-flow Vector Packing Solver (VPSolver).

Copyright (C) 2013-2016, Filipe Brandao
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


def test_instance_vbp():
    """Test instance_vbp."""
    import instance_vbp
    instance_vbp.main()


def test_instance_mvp():
    """Test instance_mvp."""
    import instance_mvp
    instance_mvp.main()


def test_wolsey():
    """Test wolsey."""
    import wolsey
    wolsey.main()


def test_twostage():
    """Test twostage."""
    import twostage
    twostage.main()


if __name__ == "__main__":
    test_instance_vbp()
    test_instance_mvp()
    test_wolsey()
    test_twostage()
