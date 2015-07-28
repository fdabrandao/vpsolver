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

from collections import Iterable, defaultdict


def linear_constraint(left, sign, right):
    """Transforms (left, sign, right) constraints into (lincomb, sign, rhs)."""
    assert (
        not isinstance(left, (int, float)) or
        not isinstance(right, (int, float))
    )
    pairs = defaultdict(lambda: 0)
    rhs = 0

    def add_entry(e, signal):
        assert isinstance(e, (int, float, str, Iterable))
        if isinstance(e, (int, float)):
            return -signal*e
        elif isinstance(e, str):
            pairs[e] += signal
            return 0
        elif isinstance(e, Iterable):
            a, b = e
            assert isinstance(a, int) or isinstance(b, int)
            assert isinstance(a, str) or isinstance(b, str)
            if isinstance(a, str):
                pairs[a] += signal*b
            else:
                pairs[b] += signal*a
            return 0

    if isinstance(left, (int, float, str)):
        rhs += add_entry(left, 1)
    else:
        for e in left:
            rhs += add_entry(e, 1)

    if isinstance(right, (int, float, str)):
        rhs += add_entry(right, -1)
    else:
        for e in right:
            rhs += add_entry(e, -1)

    if sign in ("<", ">"):
        sign += "="

    lincomb = sorted(pairs.items())
    return (lincomb, sign, rhs)
