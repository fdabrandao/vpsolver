#!/usr/bin/env python
"""
This code is part of the Arc-flow Vector Packing Solver (VPSolver).

Copyright (C) 2013-2016, Filipe Brandao <fdabrandao@gmail.com>
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
