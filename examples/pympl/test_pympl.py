#!/usr/bin/env python
"""
This code is part of the Arc-flow Vector Packing Solver (VPSolver).

Copyright (C) 2013-2016, Filipe Brandao <fdabrandao@gmail.com>
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
